from __future__ import annotations

import hashlib
import hmac
import json
from pathlib import Path
from typing import Any


def _mac(key: str, value: int) -> str:
    return hmac.new(key.encode("utf-8"), str(value).encode("utf-8"), hashlib.sha256).hexdigest()


def init_counter(path: Path, hw_fp: str) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"boot_count": 0, "mac": _mac(hw_fp, 0), "last_boot_id": None}), encoding="utf-8")


def read_counter(path: Path, hw_fp: str) -> int:
    data = json.loads(path.read_text(encoding="utf-8"))
    expected = _mac(hw_fp, int(data["boot_count"]))
    if not hmac.compare_digest(expected, data["mac"]):
        raise ValueError("Counter MAC mismatch")
    return int(data["boot_count"])


def _read_counter_payload(path: Path, hw_fp: str) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if "last_boot_id" not in data:
        raise ValueError("Counter metadata missing")
    expected = _mac(hw_fp, int(data["boot_count"]))
    if not hmac.compare_digest(expected, data["mac"]):
        raise ValueError("Counter MAC mismatch")
    return data


def increment_counter(path: Path, hw_fp: str) -> int:
    current = read_counter(path, hw_fp)
    nxt = current + 1
    data = _read_counter_payload(path, hw_fp)
    path.write_text(
        json.dumps({"boot_count": nxt, "mac": _mac(hw_fp, nxt), "last_boot_id": data.get("last_boot_id")}),
        encoding="utf-8",
    )
    return nxt


def ensure_boot_counter(path: Path, hw_fp: str, current_boot_id: str) -> int:
    data = _read_counter_payload(path, hw_fp)
    current = int(data["boot_count"])
    if data.get("last_boot_id") != current_boot_id:
        current += 1
    path.write_text(
        json.dumps({"boot_count": current, "mac": _mac(hw_fp, current), "last_boot_id": current_boot_id}),
        encoding="utf-8",
    )
    return current

