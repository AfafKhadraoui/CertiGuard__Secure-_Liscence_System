"""L9 watermark: distinct raw payloads per customer (migrated from test_watermark.py)."""

from __future__ import annotations

import base64
import json
from pathlib import Path

from certiguard.ca import issue_license
from certiguard.layers.crypto_core import generate_keypair
from certiguard.license_client import CertiGuardClient


def test_license_watermark_distinct_payloads(tmp_path: Path) -> None:
    state_dir = tmp_path / "state"
    state_dir.mkdir(parents=True, exist_ok=True)

    priv_path = state_dir / "private.key"
    pub_path = state_dir / "public.key"
    generate_keypair(priv_path, pub_path)

    client = CertiGuardClient(state_dir)
    req = client.bootstrap()
    req_path = state_dir / "request.cgreq"
    req_path.write_text(json.dumps(req), encoding="utf-8")

    acme_path = state_dir / "acme_license.lic"
    issue_license(
        request_path=req_path,
        private_key_path=priv_path,
        out_path=acme_path,
        issued_to="ACME Corp",
        max_users=10,
        modules=["core"],
        valid_days=30,
        exe_hash="dummy_hash",
    )

    beta_path = state_dir / "beta_license.lic"
    issue_license(
        request_path=req_path,
        private_key_path=priv_path,
        out_path=beta_path,
        issued_to="Beta Corp",
        max_users=10,
        modules=["core"],
        valid_days=30,
        exe_hash="dummy_hash",
    )

    def extract_raw_json(lic_path: Path) -> bytes:
        raw_b64 = lic_path.read_text(encoding="ascii")
        raw_bytes = base64.b64decode(raw_b64)
        return raw_bytes[64:]

    acme_raw = extract_raw_json(acme_path)
    beta_raw = extract_raw_json(beta_path)
    assert acme_raw != beta_raw

    acme_payload = json.loads(acme_raw.decode("utf-8"))
    beta_payload = json.loads(beta_raw.decode("utf-8"))
    assert acme_payload["issued_to"] == "ACME Corp"
    assert beta_payload["issued_to"] == "Beta Corp"
    assert acme_payload["parameters"]["max_users"] == 10
    assert beta_payload["parameters"]["max_users"] == 10
