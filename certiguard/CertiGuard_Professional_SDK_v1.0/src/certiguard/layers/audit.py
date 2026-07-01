from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def append_event(path: Path, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    prev_hash = "0" * 64
    if path.exists():
        lines = path.read_text(encoding="utf-8").splitlines()
        if lines:
            prev_hash = json.loads(lines[-1])["entry_hash"]
    entry = {
        "ts": datetime.now(UTC).isoformat(),
        "event": event_type,
        "payload": payload,
        "prev_hash": prev_hash,
    }
    digest = hashlib.sha256(json.dumps(entry, sort_keys=True).encode("utf-8")).hexdigest()
    entry["entry_hash"] = digest
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def verify_chain(path: Path) -> bool:
    if not path.exists():
        return True
    prev_hash = "0" * 64
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row["prev_hash"] != prev_hash:
            return False
        entry_hash = row.pop("entry_hash")
        calc = hashlib.sha256(json.dumps(row, sort_keys=True).encode("utf-8")).hexdigest()
        if calc != entry_hash:
            return False
        prev_hash = entry_hash
    return True

