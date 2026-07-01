from __future__ import annotations

import hashlib
import hmac
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature

from certiguard.layers.counter import read_counter
from certiguard.layers.crypto_core import load_public_key, verify_payload
from certiguard.layers.dna import derive_session_key, load_installation_dna, validate_and_update_timeline
from certiguard.layers.hardware import hardware_fingerprint
from certiguard.layers.tpm import tpm_anchor
from certiguard.layers.integrity import file_sha256
from certiguard.layers.storage import read_json, secure_write_json


import base64

HONEYPOT_KEYS = ("PREMIUM_UNLOCK", "ADMIN_OVERRIDE", "DEBUG_MODE", "FEATURE_FLAG_XYZ")
_HONEYPOT_STRING_TRUTHY = frozenset(
    {"true", "1", "yes", "on", "enable", "enabled", "y", "t"}
)


def _now() -> datetime:
    return datetime.now(UTC)


def check_honeypot_tripwire(raw_license_bytes: bytes) -> None:
    """
    L7 — Inspect the **unsigned** JSON suffix (after the 64-byte Ed25519 signature).

    Runs **before** ``verify_payload`` so obviously tampered unlock flags are rejected
    even if an attacker experiments with the blob structure. Legitimate vendor licenses
    **omit** these keys entirely, or set them explicitly to JSON ``false`` / ``0`` if
    ever embedded as decoys.

    Raises:
        PermissionError: if a tripwire key carries an attacker-friendly value.
    """
    if len(raw_license_bytes) < 65:
        return
    try:
        raw_payload = json.loads(raw_license_bytes[64:].decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return
    for key in HONEYPOT_KEYS:
        if key not in raw_payload:
            continue
        v = raw_payload[key]
        if isinstance(v, bool):
            if v is True:
                raise PermissionError(f"L7_HONEYPOT: {key} is true")
            continue
        if isinstance(v, (int, float)) and v != 0:
            raise PermissionError(f"L7_HONEYPOT: {key} non-zero ({v!r})")
        if isinstance(v, str) and v.strip().lower() in _HONEYPOT_STRING_TRUTHY:
            raise PermissionError(f"L7_HONEYPOT: {key} string truthy ({v!r})")
        if isinstance(v, (dict, list)) and v and key == "FEATURE_FLAG_XYZ":
            raise PermissionError("L7_HONEYPOT: FEATURE_FLAG_XYZ non-empty collection")


def verify_license_and_respond(
    *,
    license_path: Path,
    public_key_path: Path,
    challenge_nonce: bytes,
    dna_path: Path,
    counter_path: Path,
    app_binary_path: Path | None = None,
    grace_state_path: Path | None = None,
    exe_hash_grace_hours: int = 72,
) -> dict[str, Any]:
    raw_b64 = license_path.read_text(encoding="ascii")
    raw_bytes = base64.b64decode(raw_b64)

    # --- L7: honeypot tripwire on unsigned JSON suffix (before Ed25519 verify) ---
    check_honeypot_tripwire(raw_bytes)

    # In production, replace PUBLIC_KEY_HEX with hardcoded hex string
    # For dynamic tests, we fall back to public_key_path
    PUBLIC_KEY_HEX = os.environ.get("CERTIGUARD_PUBLIC_KEY_HEX", None)
    if PUBLIC_KEY_HEX:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        pub = Ed25519PublicKey.from_public_bytes(bytes.fromhex(PUBLIC_KEY_HEX))
    else:
        pub = load_public_key(public_key_path)

    payload_bytes = verify_payload(raw_bytes, pub)
    payload = json.loads(payload_bytes.decode("utf-8"))

    if datetime.fromisoformat(payload["valid_until"].replace("Z", "+00:00")) < _now():
        raise PermissionError("License expired")

    if datetime.fromisoformat(payload["issued_at"].replace("Z", "+00:00")) > _now():
        raise PermissionError("License from the future")

    hw_fp = hardware_fingerprint()
    if not hmac.compare_digest(payload["hardware_fingerprint"], hw_fp):
        raise PermissionError("Hardware fingerprint mismatch")

    boot_count = read_counter(counter_path, hw_fp)
    if boot_count < int(payload["install_dna"]["boot_count_at_issue"]):
        raise PermissionError("Boot counter rollback detected")

    local_dna = load_installation_dna(dna_path, hw_fp)
    if local_dna["uuid_hash"] != payload["install_dna"]["uuid_hash"]:
        raise PermissionError("Installation UUID mismatch")
    if local_dna["first_boot_hash"] != payload["install_dna"]["first_boot_hash"]:
        raise PermissionError("Installation first-boot mismatch")
    validate_and_update_timeline(dna_path, hw_fp, boot_count)

    # Optional TPM premium enforcement.
    expected_tpm_anchor = payload.get("tpm", {}).get("anchor")
    if expected_tpm_anchor:
        local_tpm_anchor = tpm_anchor()
        if local_tpm_anchor != expected_tpm_anchor:
            raise PermissionError("TPM anchor mismatch")

    if app_binary_path and payload.get("exe_hash"):
        observed = file_sha256(app_binary_path)
        if observed != payload["exe_hash"]:
            if not grace_state_path:
                raise PermissionError("Executable hash mismatch")
            state = read_json(grace_state_path, default={})
            first_seen = state.get("first_mismatch_at")
            now = _now()
            if not first_seen:
                secure_write_json(grace_state_path, {"first_mismatch_at": now.isoformat(), "expected": payload["exe_hash"], "observed": observed})
            else:
                age_hours = (now - datetime.fromisoformat(first_seen)).total_seconds() / 3600.0
                if age_hours > exe_hash_grace_hours:
                    raise PermissionError("Executable hash mismatch beyond grace window")

    session_key = derive_session_key(dna_path, hw_fp, boot_count)
    license_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).digest()
    response = hmac.new(session_key, license_hash + challenge_nonce, hashlib.sha256).hexdigest()
    return {"hmac_response": response, "license_id": payload["license_id"], "boot_count": boot_count}


def verify_challenge_response(
    response: str,
    *,
    license_path: Path,
    challenge_nonce: bytes,
    dna_path: Path,
    counter_path: Path,
) -> bool:
    raw_b64 = license_path.read_text(encoding="ascii")
    raw_bytes = base64.b64decode(raw_b64)
    payload_bytes = raw_bytes[64:]
    payload = json.loads(payload_bytes.decode("utf-8"))
    hw_fp = hardware_fingerprint()
    boot_count = read_counter(counter_path, hw_fp)
    session_key = derive_session_key(dna_path, hw_fp, boot_count)
    license_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).digest()
    expected = hmac.new(session_key, license_hash + challenge_nonce, hashlib.sha256).hexdigest()
    return hmac.compare_digest(response, expected)


def random_challenge() -> bytes:
    return os.urandom(32)

