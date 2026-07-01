#!/usr/bin/env python3
"""
Aggregate layer smoke tests (maps to CertiGuard_Final_Implementation.md Part 5).

Run from repo root:
  python certiguard/tests/test_all_layers.py
Or:
  cd certiguard && set PYTHONPATH=src && python tests/test_all_layers.py

Exit 0 if all checks pass; non-zero on first failure.
"""

from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from cryptography.exceptions import InvalidSignature  # noqa: E402

from certiguard.layers.audit import append_event, verify_chain  # noqa: E402
from certiguard.layers.crypto_core import (  # noqa: E402
    generate_keypair,
    load_private_key,
    load_public_key,
    sign_payload,
    verify_payload,
)
from certiguard.layers.verifier_server import check_honeypot_tripwire  # noqa: E402


def _ok(name: str) -> None:
    print(f"  [PASS] {name}")


def _fail(name: str, detail: str) -> None:
    print(f"  [FAIL] {name} — {detail}")
    raise SystemExit(1)


def test_l10_audit_chain(tmp_path: Path) -> None:
    log = tmp_path / "audit.log"
    append_event(log, "t1", {"n": 1})
    append_event(log, "t2", {"n": 2})
    if not verify_chain(log):
        _fail("L10", "valid chain rejected")
    _ok("L10 valid hash chain")
    lines = log.read_text(encoding="utf-8").splitlines()
    row = json.loads(lines[1])
    row["payload"] = {"n": 999}
    lines[1] = json.dumps(row)
    log.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if verify_chain(log):
        _fail("L10", "tampered chain still valid")
    _ok("L10 tamper detected (chain break)")


def test_l7_honeypot() -> None:
    body = json.dumps({"PREMIUM_UNLOCK": True, "license_id": "x"}).encode()
    raw = b"\x00" * 64 + body
    try:
        check_honeypot_tripwire(raw)
        _fail("L7", "PREMIUM_UNLOCK true not rejected")
    except PermissionError as e:
        if "L7_HONEYPOT" not in str(e):
            _fail("L7", f"wrong error: {e}")
    _ok("L7 honeypot (boolean true)")

    body2 = json.dumps({"PREMIUM_UNLOCK": "yes"}).encode()
    try:
        check_honeypot_tripwire(b"\x00" * 64 + body2)
        _fail("L7", "string yes not rejected")
    except PermissionError:
        pass
    _ok("L7 honeypot (string truthy)")

    clean = json.dumps({"license_id": "ok", "hardware_fingerprint": "ab"}).encode()
    check_honeypot_tripwire(b"\x00" * 64 + clean)
    _ok("L7 clean payload (no tripwire keys)")


def test_l1_signature(tmp_path: Path) -> None:
    priv = tmp_path / "priv.pem"
    pub = tmp_path / "pub.pem"
    generate_keypair(priv, pub)
    sk = load_private_key(priv)
    pk = load_public_key(pub)
    payload = {"k": "v", "n": 1}
    signed = sign_payload(payload, sk)
    verify_payload(signed, pk)
    _ok("L1 valid Ed25519 sign+verify")
    bad = bytearray(signed)
    bad[0] ^= 0xFF
    try:
        verify_payload(bytes(bad), pk)
        _fail("L1", "corrupt signature accepted")
    except InvalidSignature:
        pass
    _ok("L1 corrupt signature rejected")


def main() -> None:
    print("CertiGuard — aggregate layer tests\n")
    tmp = Path(__file__).resolve().parent / "_layer_smoke_tmp"
    tmp.mkdir(exist_ok=True)
    try:
        test_l1_signature(tmp)
        test_l7_honeypot()
        test_l10_audit_chain(tmp)
    finally:
        for p in tmp.glob("*"):
            try:
                p.unlink()
            except OSError:
                pass
        try:
            tmp.rmdir()
        except OSError:
            pass

    print(
        "\nMore coverage: tests/test_pow_heartbeat.py (L5), tests/test_license_watermark.py (L9), "
        "test_behavior_probe.py (L6), tests/test_antidebug.py, tests/test_integrity.py"
    )
    print("\nAll aggregate checks passed.")


if __name__ == "__main__":
    main()
