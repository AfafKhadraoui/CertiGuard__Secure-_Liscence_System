from __future__ import annotations

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
    signed = {**payload, "signature": sign_payload(payload, load_private_key(private_key_path))}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(signed, indent=2), encoding="utf-8")
    return signed


def verify_signed_manifest(manifest_path: Path, public_key_path: Path) -> bool:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    signature = data["signature"]
    payload = {k: v for k, v in data.items() if k != "signature"}
    return verify_payload(payload, signature, load_public_key(public_key_path))

