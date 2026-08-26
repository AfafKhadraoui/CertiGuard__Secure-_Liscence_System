from __future__ import annotations

import base64
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from certiguard.layers.crypto_core import load_private_key, load_public_key, sign_payload, verify_payload


def create_signed_manifest(
    *,
    version: str,
    files: dict[str, str],
    private_key_path: Path,
    out_path: Path,
) -> dict[str, Any]:
    payload = {
        "version": version,
        "generated_at": datetime.now(UTC).isoformat(),
        "files": files,
    }
    signed_bytes = sign_payload(payload, load_private_key(private_key_path))
    signed = {**payload, "signature": base64.b64encode(signed_bytes).decode("ascii")}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(signed, indent=2), encoding="utf-8")
    return signed


def verify_signed_manifest(manifest_path: Path, public_key_path: Path) -> bool:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    signed_bytes = base64.b64decode(data["signature"])
    payload = {k: v for k, v in data.items() if k != "signature"}
    verified_payload = json.loads(verify_payload(signed_bytes, load_public_key(public_key_path)).decode("utf-8"))
    return verified_payload == payload

