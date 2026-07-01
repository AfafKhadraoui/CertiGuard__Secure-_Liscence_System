#!/usr/bin/env python3
"""
CertiGuard end-to-end harness — provisions keys + license + policy, runs verify scenarios,
optional synthetic audit lines, and attack simulations for dashboard demos.

Industry pattern (offline licensing): run a *local check* on startup, persist evidence
(audit trail), optionally sync to a vendor console — see docs/HOW_TO_TEST.md.

Usage (from certiguard repo root):
  set PYTHONPATH=src
  python examples/cg_e2e_app/run_harness.py setup
  python examples/cg_e2e_app/run_harness.py verify-ok
  python examples/cg_e2e_app/run_harness.py dashboard-hint

  python examples/cg_e2e_app/run_harness.py verify-probe
  python examples/cg_e2e_app/run_harness.py warm --times 5
  python examples/cg_e2e_app/run_harness.py stress

  python examples/cg_e2e_app/run_harness.py synthetic-audit
  python examples/cg_e2e_app/run_harness.py attack-audit
  python examples/cg_e2e_app/run_harness.py attack-honeypot
  python examples/cg_e2e_app/run_harness.py attack-signature

  python examples/cg_e2e_app/run_harness.py status
"""

from __future__ import annotations

import argparse
import base64
import json
import shutil
import sys
from pathlib import Path

# certiguard/src on path
_REPO = Path(__file__).resolve().parents[2]
_SRC = _REPO / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from certiguard.ca import issue_license  # noqa: E402
from certiguard.config import SecurityPolicy  # noqa: E402
from certiguard.layers.audit import append_event, verify_chain  # noqa: E402
from certiguard.layers.crypto_core import generate_keypair  # noqa: E402
from certiguard.license_client import CertiGuardClient  # noqa: E402


def _paths(root: Path) -> dict[str, Path]:
    return {
        "root": root,
        "state": root / "client_state",
        "req": root / "client.cgreq.json",
        "lic": root / "license.lic",
        "evil_lic": root / "evil_honeypot.lic",
        "priv": root / "vendor_private.pem",
        "pub": root / "vendor_public.pem",
    }


def cmd_setup(args: argparse.Namespace) -> None:
    p = _paths(Path(args.root))
    if args.clean and p["root"].exists():
        shutil.rmtree(p["root"])
    p["root"].mkdir(parents=True, exist_ok=True)
    p["state"].mkdir(parents=True, exist_ok=True)

    generate_keypair(p["priv"], p["pub"])
    client = CertiGuardClient(p["state"], collector_url=args.collector or None)
    req = client.bootstrap()
    p["req"].write_text(json.dumps(req, indent=2), encoding="utf-8")

    issue_license(
        request_path=p["req"],
        private_key_path=p["priv"],
        out_path=p["lic"],
        issued_to="CG_E2E_Demo",
        max_users=50,
        modules=["demo", "qa"],
        valid_days=400,
        exe_hash="ab" * 32,
    )
    SecurityPolicy(
        baseline_learning_days=max(3, int(args.learning_days)),
        anomaly_enforcement_after_learning=True,
        use_machine_behavior_probe=bool(args.machine_probe_policy),
    ).save(p["state"] / "policy.json")

    print("[setup] OK")
    print(f"  state_dir:  {p['state']}")
    print(f"  license:    {p['lic']}")
    print(f"  public key: {p['pub']}")
    print(f"  audit.log:  {p['state'] / 'audit.log'}")


def _client(args: argparse.Namespace) -> tuple[CertiGuardClient, dict[str, Path]]:
    p = _paths(Path(args.root))
    if not p["lic"].exists():
        sys.exit("Run `setup` first.")
    return CertiGuardClient(p["state"], collector_url=args.collector or None), p


def cmd_verify_ok(args: argparse.Namespace) -> None:
    client, p = _client(args)
    r = client.verify_runtime(
        license_path=p["lic"],
        public_key_path=p["pub"],
        heartbeat_key=args.heartbeat_key,
        behavior_features=[float(x) for x in args.features.split(",")],
        policy_path=p["state"] / "policy.json",
        use_machine_behavior_probe=False,
    )
    print(json.dumps(r.__dict__, indent=2))


def cmd_verify_probe(args: argparse.Namespace) -> None:
    client, p = _client(args)
    r = client.verify_runtime(
        license_path=p["lic"],
        public_key_path=p["pub"],
        heartbeat_key=args.heartbeat_key,
        behavior_features=[0.0, 0.0, 0.0, 0.0],
        policy_path=p["state"] / "policy.json",
        use_machine_behavior_probe=True,
    )
    print(json.dumps(r.__dict__, indent=2))


def cmd_warm(args: argparse.Namespace) -> None:
    client, p = _client(args)
    feats = [float(x) for x in args.features.split(",")]
    for i in range(int(args.times)):
        r = client.verify_runtime(
            license_path=p["lic"],
            public_key_path=p["pub"],
            heartbeat_key=args.heartbeat_key,
            behavior_features=feats,
            policy_path=p["state"] / "policy.json",
        )
        print(f"warm {i+1}/{args.times} ok={r.ok} code={r.code}")


def cmd_stress(args: argparse.Namespace) -> None:
    client, p = _client(args)
    r = client.verify_runtime(
        license_path=p["lic"],
        public_key_path=p["pub"],
        heartbeat_key=args.heartbeat_key,
        behavior_features=[float(x) for x in args.stress_features.split(",")],
        policy_path=p["state"] / "policy.json",
    )
    print(json.dumps(r.__dict__, indent=2))


def cmd_synthetic_audit(args: argparse.Namespace) -> None:
    """Append harmless chained events so the dashboard has richer rows."""
    _, p = _client(args)
    log = p["state"] / "audit.log"
    if not verify_chain(log):
        sys.exit("audit.log chain invalid — fix or delete audit.log before synthetic")
    append_event(log, "demo_synthetic", {"source": "cg_e2e_app", "note": "dashboard richness"})
    append_event(log, "demo_synthetic", {"source": "cg_e2e_app", "note": "second line"})
    print("[synthetic-audit] appended 2 events; refresh dashboard")


def cmd_attack_audit(args: argparse.Namespace) -> None:
    _, p = _client(args)
    log = p["state"] / "audit.log"
    if not log.exists():
        sys.exit("No audit.log")
    lines = log.read_text(encoding="utf-8").splitlines()
    if not lines:
        sys.exit("audit.log is empty — run verify-ok first")
    # Change payload without recomputing entry_hash so verify_chain fails.
    idx = 1 if len(lines) >= 2 else 0
    row = json.loads(lines[idx])
    row["payload"] = {"TAMPER": True}
    lines[idx] = json.dumps(row)
    log.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[attack-audit] tampered line index {idx}; next verify-ok should return AUDIT_TAMPER")


def cmd_attack_honeypot(args: argparse.Namespace) -> None:
    p = _paths(Path(args.root))
    body = {
        "version": "3.0",
        "PREMIUM_UNLOCK": True,
        "license_id": "EVIL",
        "issued_to": "x",
        "hardware_fingerprint": "0" * 64,
    }
    raw = b"\x00" * 64 + json.dumps(body).encode("utf-8")
    p["evil_lic"].write_text(base64.b64encode(raw).decode("ascii"), encoding="ascii")
    print(f"[attack-honeypot] wrote {p['evil_lic']} (fake sig + JSON tripwire; L7 runs before Ed25519)")
    client, paths = _client(args)
    r = client.verify_runtime(
        license_path=p["evil_lic"],
        public_key_path=paths["pub"],
        heartbeat_key=args.heartbeat_key,
        behavior_features=[1.0, 2.0, 3.0, 4.0],
        policy_path=paths["state"] / "policy.json",
    )
    print(json.dumps(r.__dict__, indent=2))


def cmd_attack_signature(args: argparse.Namespace) -> None:
    _, p = _client(args)
    txt = p["lic"].read_text(encoding="ascii")
    buf = bytearray(base64.b64decode(txt))
    if len(buf) < 70:
        sys.exit("license too short")
    buf[20] ^= 0xFF
    p["lic"].write_text(base64.b64encode(bytes(buf)).decode("ascii"), encoding="ascii")
    print("[attack-signature] flipped byte in signature; verify output shows L1_L4_REJECT")
    r = CertiGuardClient(p["state"]).verify_runtime(
        license_path=p["lic"],
        public_key_path=p["pub"],
        heartbeat_key=args.heartbeat_key,
        behavior_features=[20.0, 10.0, 3.0, 30.0],
        policy_path=p["state"] / "policy.json",
    )
    print(json.dumps(r.__dict__, indent=2))


def cmd_status(args: argparse.Namespace) -> None:
    p = _paths(Path(args.root))
    log = p["state"] / "audit.log"
    print("root:", p["root"])
    print("chain_ok:", verify_chain(log) if log.exists() else "n/a")
    if log.exists():
        lines = log.read_text(encoding="utf-8").splitlines()
        print("audit_lines:", len(lines))
        for ln in lines[-5:]:
            print(" ", ln[:120] + ("…" if len(ln) > 120 else ""))


def cmd_dashboard_hint(args: argparse.Namespace) -> None:
    p = _paths(Path(args.root))
    ap = (p["state"] / "audit.log").resolve()
    print(
        "Point the vendor dashboard at THIS file (same path the harness writes):\n"
        f"  certiguard dashboard --audit-log \"{ap}\" --port 8080\n"
        "Then open http://localhost:8080 and run verify-ok / synthetic-audit / etc.\n"
        "Optional client→vendor push (second terminal):\n"
        f"  set CERTIGUARD_COLLECTOR_URL=http://127.0.0.1:8080\n"
        f"  python examples/cg_e2e_app/run_harness.py verify-ok --root \"{p['root']}\" --collector http://127.0.0.1:8080"
    )


def main() -> None:
    default_root = str(_REPO / "demo_runs" / "cg_e2e")
    ap = argparse.ArgumentParser(description="CertiGuard E2E harness + attack simulators")
    ap.add_argument("--root", default=default_root, help="Harness data directory")
    ap.add_argument("--collector", default=None, help="Optional collector URL for sync after verify")
    ap.add_argument("--heartbeat-key", default="e2e-heartbeat-secret", help="PoW heartbeat key")
    ap.add_argument("--features", default="22,14,4,40", help="Comma floats for L6 app mode")
    ap.add_argument("--stress-features", default="8000,0,900,9000", help="Comma floats for stress")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_setup = sub.add_parser("setup", help="Keys + cgreq + license + short L6 learning policy")
    p_setup.add_argument("--clean", action="store_true", help="Delete harness root before provisioning")
    p_setup.add_argument("--learning-days", default="4", help="Policy baseline_learning_days")
    p_setup.add_argument(
        "--machine-probe-policy",
        action="store_true",
        help="Persist use_machine_behavior_probe in policy.json",
    )
    p_setup.set_defaults(func=cmd_setup)
    sub.add_parser("verify-ok", help="Normal verify_runtime").set_defaults(func=cmd_verify_ok)
    sub.add_parser("verify-probe", help="verify with machine behavior probe").set_defaults(func=cmd_verify_probe)
    p_warm = sub.add_parser("warm", help="Repeat verify for L6 learning")
    p_warm.add_argument("--times", type=int, default=5, help="Number of verify_runtime calls")
    p_warm.set_defaults(func=cmd_warm)
    sub.add_parser("stress", help="One verify with extreme features").set_defaults(func=cmd_stress)
    sub.add_parser("synthetic-audit", help="Append demo audit lines (valid chain)").set_defaults(
        func=cmd_synthetic_audit
    )
    sub.add_parser("attack-audit", help="Tamper audit.log line 2 (breaks chain)").set_defaults(
        func=cmd_attack_audit
    )
    sub.add_parser("attack-honeypot", help="Write evil license + run verify").set_defaults(
        func=cmd_attack_honeypot
    )
    sub.add_parser("attack-signature", help="Corrupt license signature bytes").set_defaults(
        func=cmd_attack_signature
    )
    sub.add_parser("status", help="Show audit tail + chain_ok").set_defaults(func=cmd_status)
    sub.add_parser("dashboard-hint", help="Print exact dashboard command for this root").set_defaults(
        func=cmd_dashboard_hint
    )

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
