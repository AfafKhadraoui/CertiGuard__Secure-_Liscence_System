from __future__ import annotations

"""
L5 heartbeat / dead-man-switch primitives.

Each append-only line proves **recent work** (partial SHA-256 prefix) and chains to the
previous line's hash. ``verify_runtime`` requires a **fresh** last line (recency), so if
the protected app stops calling ``write_heartbeat``, the next verification fails — the
**dead man's switch** pattern. Optional ``watchdog-supervise`` polls the same file.

The shared ``heartbeat_key`` is mixed into the PoW preimage so another local process
cannot extend the chain without the deployment secret.
"""

import hashlib
import json
import os
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

from certiguard.layers.hardware import hardware_fingerprint

# Partial-hash difficulty (hex prefix). Increase to harden; decreases mining speed.
_POW_PREFIX = "00000"


def _pow_preimage(ts: str, machine_id: str, heartbeat_key: str, nonce: int, prev_hash: str) -> bytes:
    """Canonical byte layout for mining and verification (must stay in sync)."""
    return (
        f"{ts}{machine_id}|{heartbeat_key}|{nonce}|{prev_hash}".encode("utf-8")
    )


def _pow_preimage_legacy(ts: str, machine_id: str, nonce: int, prev_hash: str) -> bytes:
    """Pre-SDK layout: key was not mixed in (still used 5-hex PoW prefix)."""
    return f"{ts}{machine_id}{nonce}{prev_hash}".encode("utf-8")


def mine_pow(ts: str, machine_id: str, prev_hash: str, heartbeat_key: str = "") -> tuple[int, str]:
    nonce = 0
    while True:
        data = _pow_preimage(ts, machine_id, heartbeat_key, nonce, prev_hash)
        h = hashlib.sha256(data).hexdigest()
        if h.startswith(_POW_PREFIX):
            return nonce, h
        nonce += 1


def write_heartbeat(path: Path, key: str) -> None:
    now = datetime.now(UTC).isoformat()
    machine_id = hardware_fingerprint()

    path.parent.mkdir(parents=True, exist_ok=True)

    prev_hash = "0" * 64
    if path.exists():
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
            if lines:
                prev_hash = json.loads(lines[-1])["hash"]
        except Exception:
            pass

    nonce, new_hash = mine_pow(now, machine_id, prev_hash, key)
    
    payload = {
        "ts": now,
        "nonce": nonce,
        "prev_hash": prev_hash,
        "hash": new_hash,
        "pid": os.getpid(),
        "pow": _POW_PREFIX,
    }
    
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")


def verify_heartbeat_recent(path: Path, key: str, timeout_seconds: int = 60) -> bool:
    if not path.exists():
        return False
        
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        if not lines:
            return False
            
        machine_id = hardware_fingerprint()
        prev_hash = "0" * 64
        
        for line in lines:
            payload = json.loads(line)
            ts = payload["ts"]
            nonce = payload["nonce"]
            recorded_prev = payload["prev_hash"]
            recorded_hash = payload["hash"]
            
            if recorded_prev != prev_hash:
                return False
                
            pow_prefix = payload.get("pow") or _POW_PREFIX
            n = int(nonce)
            calc_v2 = hashlib.sha256(_pow_preimage(ts, machine_id, key, n, prev_hash)).hexdigest()
            calc_legacy = hashlib.sha256(_pow_preimage_legacy(ts, machine_id, n, prev_hash)).hexdigest()
            calc_hash = calc_v2 if calc_v2 == recorded_hash else calc_legacy
            if calc_hash != recorded_hash or not calc_hash.startswith(pow_prefix):
                return False

            prev_hash = calc_hash
            
        # Check recency of the last heartbeat
        last_payload = json.loads(lines[-1])
        age = datetime.now(UTC) - datetime.fromisoformat(last_payload["ts"])
        return age <= timedelta(seconds=timeout_seconds)
        
    except Exception:
        return False


def heartbeat_loop(path: Path, key: str, every_seconds: int = 30) -> None:
    while True:
        write_heartbeat(path, key)
        time.sleep(every_seconds)

