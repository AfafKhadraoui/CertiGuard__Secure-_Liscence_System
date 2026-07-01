"""L7 honeypot: re-signed payload with tripwire still rejected (migrated from test_honeypot.py)."""

from __future__ import annotations

import base64
import json
from pathlib import Path

from certiguard.ca import issue_license
from certiguard.layers.crypto_core import generate_keypair, sign_payload
from certiguard.license_client import CertiGuardClient


def test_honeypot_reject_resigned_tripwire_license(tmp_path: Path) -> None:
    state_dir = tmp_path / "state"
    state_dir.mkdir(parents=True, exist_ok=True)

    priv_path = state_dir / "private.key"
    pub_path = state_dir / "public.key"
    generate_keypair(priv_path, pub_path)

    client = CertiGuardClient(state_dir)
    req = client.bootstrap()
    req_path = state_dir / "request.cgreq"
    req_path.write_text(json.dumps(req), encoding="utf-8")

    lic_path = state_dir / "valid_license.lic"
    issue_license(
        request_path=req_path,
        private_key_path=priv_path,
        out_path=lic_path,
        issued_to="Test Customer",
        max_users=10,
        modules=["core"],
        valid_days=30,
        exe_hash="dummy_hash",
    )

    raw_b64 = lic_path.read_text(encoding="ascii")
    raw_bytes = base64.b64decode(raw_b64)
    payload_bytes = raw_bytes[64:]
    payload = json.loads(payload_bytes.decode("utf-8"))
    payload["PREMIUM_UNLOCK"] = True

    from certiguard.layers.crypto_core import load_private_key

    tampered_signed_bytes = sign_payload(payload, load_private_key(priv_path))
    tampered_lic_path = state_dir / "tampered_license.lic"
    tampered_lic_path.write_text(base64.b64encode(tampered_signed_bytes).decode("ascii"), encoding="ascii")

    result = client.verify_runtime(
        license_path=tampered_lic_path,
        public_key_path=pub_path,
        heartbeat_key="test_key",
        behavior_features=[1.0, 2.0, 3.0, 4.0],
    )

    assert result.code == "L1_L4_REJECT"
    assert "L7_HONEYPOT" in result.message
