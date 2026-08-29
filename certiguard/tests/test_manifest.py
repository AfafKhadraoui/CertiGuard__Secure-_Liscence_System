from __future__ import annotations

import json
from pathlib import Path

from certiguard.layers.crypto_core import generate_keypair
from certiguard.layers.manifest import create_signed_manifest, verify_signed_manifest


def test_manifest_roundtrip(tmp_path: Path) -> None:
    private_key = tmp_path / "vendor_priv.pem"
    public_key = tmp_path / "vendor_pub.pem"
    manifest_path = tmp_path / "manifest.json"

    generate_keypair(private_key, public_key)

    created = create_signed_manifest(
        version="1.2.3",
        files={"app.exe": "abc123", "assets/config.json": "def456"},
        private_key_path=private_key,
        out_path=manifest_path,
    )

    assert created["signature"]
    assert verify_signed_manifest(manifest_path, public_key) is True

    tampered = json.loads(manifest_path.read_text(encoding="utf-8"))
    tampered["files"]["app.exe"] = "deadbeef"
    manifest_path.write_text(json.dumps(tampered, indent=2), encoding="utf-8")

    assert verify_signed_manifest(manifest_path, public_key) is False