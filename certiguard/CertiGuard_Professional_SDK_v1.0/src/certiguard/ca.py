from __future__ import annotations

import json
import hashlib
import base64
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from certiguard.layers.crypto_core import load_private_key, sign_payload, derive_key_hkdf, encrypt_binary


def issue_license(
    *,
    request_path: Path,
    private_key_path: Path,
    out_path: Path,
    issued_to: str,
    max_users: int,
    modules: list[str],
    valid_days: int,
    exe_hash: str,
    k_app_b64: str | None = None,
    binary_secret_b64: str | None = None,
) -> dict[str, Any]:
    req = json.loads(request_path.read_text(encoding="utf-8"))
    payload = {
        "version": "3.0",
        "issued_to": issued_to,
        "issued_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "valid_until": (datetime.now(UTC) + timedelta(days=valid_days)).isoformat().replace("+00:00", "Z"),
        "parameters": {"max_users": max_users, "modules": modules},
        "hardware_fingerprint": req["hardware_fingerprint"],
        "install_dna": req["install_dna"],
        "tpm": req.get("tpm", {"available": False, "anchor": None}),
        "exe_hash": exe_hash,
        "license_id": f"LIC-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}",
        "watermark": hashlib.sha256(f"{issued_to}|{req['hardware_fingerprint']}".encode("utf-8")).hexdigest()[:16],
        "seed_b64": base64.b64encode(os.urandom(32)).decode("ascii"),
        "tripwires": {"premium_unlock": False, "admin_override": False},
    }

    # --- ShieldWrap Logic: Key Wrapping ---
    if k_app_b64 and binary_secret_b64:
        seed = base64.b64decode(payload["seed_b64"])
        binary_secret = base64.b64decode(binary_secret_b64)
        k_app = base64.b64decode(k_app_b64)
        
        # Derive K_derived (cryptographic dependency)
        # Enhanced IKM: HWID | ValidUntil | BinarySecret [ | TPMAnchor ]
        ikm_str = f"{payload['hardware_fingerprint']}|{payload['valid_until']}"
        tpm_anchor = payload["tpm"].get("anchor")
        if tpm_anchor:
            ikm_str += f"|{tpm_anchor}"
            
        ikm = ikm_str.encode("utf-8") + binary_secret
        k_derived = derive_key_hkdf(
            salt=seed,
            ikm=ikm,
            info=b"certiguard-v3-kdf"
        )
        
        # Wrap K_app with K_derived
        encrypted_key = encrypt_binary(k_derived, k_app)
        payload["shieldwrap"] = {
            "binary_secret_b64": binary_secret_b64,
            "encrypted_key_b64": base64.b64encode(encrypted_key).decode("ascii")
        }
    signed_bytes = sign_payload(payload, load_private_key(private_key_path))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(base64.b64encode(signed_bytes).decode("ascii"), encoding="ascii")
    return payload

