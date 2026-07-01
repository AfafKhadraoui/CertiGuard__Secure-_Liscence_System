from __future__ import annotations

import hashlib
import json
import os
from base64 import b64decode, b64encode
from datetime import UTC, datetime
from pathlib import Path
import platform
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def _key_from_fp(hardware_fp: str) -> bytes:
    return hashlib.sha256(hardware_fp.encode("utf-8")).digest()


def _encrypt_uuid(uuid_raw: bytes, key: bytes) -> dict[str, str]:
    nonce = os.urandom(12)
    ciphertext = AESGCM(key).encrypt(nonce, uuid_raw, None)
    return {"uuid_ciphertext": b64encode(ciphertext).decode("ascii"), "uuid_nonce": b64encode(nonce).decode("ascii")}


def _decrypt_uuid(ciphertext_b64: str, nonce_b64: str, key: bytes) -> bytes:
    nonce = b64decode(nonce_b64)
    ciphertext = b64decode(ciphertext_b64)
    return AESGCM(key).decrypt(nonce, ciphertext, None)


def _read_boot_id() -> str:
    boot_id_path = Path("/proc/sys/kernel/random/boot_id")
    if boot_id_path.exists():
        return boot_id_path.read_text(encoding="utf-8").strip()
    # Non-linux fallback for local development/testing.
    return f"non-linux-{platform.node() or 'host'}"


def _read_uptime_seconds() -> float:
    uptime_path = Path("/proc/uptime")
    if uptime_path.exists():
        raw = uptime_path.read_text(encoding="utf-8").split()[0]
        return float(raw)
    return 0.0


def capture_runtime_snapshot() -> dict[str, Any]:
    now = datetime.now(UTC)
    return {
        "wall_clock_time": now.isoformat(),
        "boot_id": _read_boot_id(),
        "uptime_seconds": _read_uptime_seconds(),
    }


def init_installation_dna(state_path: Path, hardware_fp: str) -> None:
    if state_path.exists():
        return
    uuid_raw = os.urandom(16)
    runtime = capture_runtime_snapshot()
    key = _key_from_fp(hardware_fp)
    enc = _encrypt_uuid(uuid_raw, key)
    payload = {
        **enc,
        "install_wall_clock_time": runtime["wall_clock_time"],
        "install_boot_id": runtime["boot_id"],
        "install_uptime_seconds": runtime["uptime_seconds"],
        "first_boot_hash": hashlib.sha256(runtime["wall_clock_time"].encode("utf-8")).hexdigest(),
        "created_at": runtime["wall_clock_time"],
        "last_seen_time": runtime["wall_clock_time"],
        "last_seen_uptime_seconds": runtime["uptime_seconds"],
        "last_seen_boot_id": runtime["boot_id"],
        "enc_scheme": "aesgcm-v1",
    }
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _decrypt_uuid_raw(state_path: Path, hardware_fp: str) -> bytes:
    data = json.loads(state_path.read_text(encoding="utf-8"))
    return _decrypt_uuid(data["uuid_ciphertext"], data["uuid_nonce"], _key_from_fp(hardware_fp))


def load_installation_dna(state_path: Path, hardware_fp: str) -> dict[str, Any]:
    data = json.loads(state_path.read_text(encoding="utf-8"))
    uuid_raw = _decrypt_uuid_raw(state_path, hardware_fp)
    return {
        "uuid_hash": hashlib.sha256(uuid_raw).hexdigest(),
        "first_boot_hash": data["first_boot_hash"],
        "install_wall_clock_time": data["install_wall_clock_time"],
        "install_boot_id": data["install_boot_id"],
        "install_uptime_seconds": data["install_uptime_seconds"],
    }


def validate_and_update_timeline(state_path: Path, hardware_fp: str, boot_count: int) -> dict[str, Any]:
    data = json.loads(state_path.read_text(encoding="utf-8"))
    _decrypt_uuid_raw(state_path, hardware_fp)
    runtime = capture_runtime_snapshot()
    now = datetime.fromisoformat(runtime["wall_clock_time"])
    last_seen = datetime.fromisoformat(data["last_seen_time"])
    if now < last_seen:
        raise PermissionError("System clock rollback detected")
    if runtime["boot_id"] == data.get("last_seen_boot_id") and runtime["uptime_seconds"] < float(data.get("last_seen_uptime_seconds", 0.0)):
        raise PermissionError("Uptime rollback detected in same boot session")
    data["last_seen_time"] = runtime["wall_clock_time"]
    data["last_seen_uptime_seconds"] = runtime["uptime_seconds"]
    data["last_seen_boot_id"] = runtime["boot_id"]
    data["last_seen_boot_count"] = boot_count
    state_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return runtime


def derive_session_key(state_path: Path, hardware_fp: str, boot_count: int) -> bytes:
    uuid_raw = _decrypt_uuid_raw(state_path, hardware_fp)
    material = uuid_raw + hardware_fp.encode("utf-8") + str(boot_count).encode("utf-8")
    return hashlib.sha256(material).digest()

