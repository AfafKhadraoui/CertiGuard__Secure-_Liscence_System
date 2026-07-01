#!/usr/bin/env python3
"""
Thin "host application" for CertiGuard demos — calls verify_runtime so all gated
layers run and audit.log is updated. Use alongside the vendor dashboard.

Run from the certiguard repo root (parent of examples/):

  Windows PowerShell:
    $env:PYTHONPATH = "src"
    python examples/demo_host_app.py ping --state-dir demo_runs/clientA ...

  Or after pip install -e .:
    python examples/demo_host_app.py ping --state-dir ...
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Repo-local execution without install
_REPO_SRC = Path(__file__).resolve().parents[1] / "src"
if _REPO_SRC.is_dir() and str(_REPO_SRC) not in sys.path:
    sys.path.insert(0, str(_REPO_SRC))

from certiguard.license_client import CertiGuardClient  # noqa: E402


def _client(state_dir: Path, collector: str | None) -> CertiGuardClient:
    return CertiGuardClient(state_dir, collector_url=collector)


def _print_result(label: str, result) -> None:
    print(f"\n=== {label} ===")
    print(json.dumps(result.__dict__, indent=2))


def _dashboard_hint(collector: str | None) -> None:
    print("\n--- Dashboard ---")
    if collector:
        print(f"Ingest target: {collector.rstrip('/')}/api/logs/ingest (via CERTIGUARD_COLLECTOR_URL or --collector-url)")
        print("Refresh Audit Logs / Overview after each scenario.")
    else:
        print("CERTIGUARD_COLLECTOR_URL not set: events stay in local state_dir/audit.log only.")
        print("Vendor view: point dashboard --audit-log at that file, or enable collector + sync-audit.")


def cmd_ping(args: argparse.Namespace) -> int:
    client = _client(Path(args.state_dir), args.collector_url)
    features = [float(x) for x in args.features.split(",")]
    r = client.verify_runtime(
        license_path=Path(args.license),
        public_key_path=Path(args.public_key),
        heartbeat_key=args.heartbeat_key,
        behavior_features=features,
        require_tpm_if_present=args.require_tpm_if_present,
        app_binary_path=Path(args.app_binary) if args.app_binary else None,
        policy_path=Path(args.policy_path) if args.policy_path else None,
        use_machine_behavior_probe=args.machine_behavior_probe,
    )
    _print_result("verify_runtime (ping)", r)
    _dashboard_hint(args.collector_url or os.environ.get("CERTIGUARD_COLLECTOR_URL"))
    return 0 if r.ok else 1


def cmd_warm(args: argparse.Namespace) -> int:
    """Run verify N times with the same features to advance L6 learning_sessions."""
    client = _client(Path(args.state_dir), args.collector_url)
    features = [float(x) for x in args.features.split(",")]
    last = None
    for i in range(args.count):
        last = client.verify_runtime(
            license_path=Path(args.license),
            public_key_path=Path(args.public_key),
            heartbeat_key=args.heartbeat_key,
            behavior_features=features,
            require_tpm_if_present=args.require_tpm_if_present,
            app_binary_path=Path(args.app_binary) if args.app_binary else None,
            policy_path=Path(args.policy_path) if args.policy_path else None,
            use_machine_behavior_probe=args.machine_behavior_probe,
        )
        print(f"warm {i + 1}/{args.count} ok={last.ok} code={last.code}")
    if last:
        _print_result("last verify after warm", last)
    print(
        "\nTip: with short baseline_learning_days in policy.json, next step is "
        "`stress` with extreme --features to try for L6_ANOMALY."
    )
    _dashboard_hint(args.collector_url or os.environ.get("CERTIGUARD_COLLECTOR_URL"))
    return 0 if last and last.ok else 1


def cmd_stress(args: argparse.Namespace) -> int:
    """Single verify with aggressive feature vector (may trigger L6 after learning)."""
    client = _client(Path(args.state_dir), args.collector_url)
    features = [float(x) for x in args.features.split(",")]
    r = client.verify_runtime(
        license_path=Path(args.license),
        public_key_path=Path(args.public_key),
        heartbeat_key=args.heartbeat_key,
        behavior_features=features,
        require_tpm_if_present=args.require_tpm_if_present,
        app_binary_path=Path(args.app_binary) if args.app_binary else None,
        policy_path=Path(args.policy_path) if args.policy_path else None,
        use_machine_behavior_probe=args.machine_behavior_probe,
    )
    _print_result("verify_runtime (stress features)", r)
    _dashboard_hint(args.collector_url or os.environ.get("CERTIGUARD_COLLECTOR_URL"))
    return 0 if r.ok else 1


def _common_verify_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--state-dir", required=True)
    p.add_argument("--license", required=True)
    p.add_argument("--public-key", required=True)
    p.add_argument("--heartbeat-key", default="dev-heartbeat")
    p.add_argument("--features", default="20,10,3,30", help="Comma-separated floats for L6")
    p.add_argument("--require-tpm-if-present", action="store_true")
    p.add_argument("--app-binary")
    p.add_argument("--policy-path")
    p.add_argument(
        "--collector-url",
        default=None,
        help="Overrides CERTIGUARD_COLLECTOR_URL for this process",
    )
    p.add_argument(
        "--machine-behavior-probe",
        action="store_true",
        help="L6 uses CPU/RAM/process/GPU snapshot (see certiguard.layers.behavior_probe)",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="CertiGuard demo host — layer verification driver")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_ping = sub.add_parser("ping", help="Single verify_runtime (happy path smoke)")
    _common_verify_args(p_ping)
    p_ping.set_defaults(func=cmd_ping)

    p_warm = sub.add_parser("warm", help="Repeat verify with same features (L6 learning sessions)")
    _common_verify_args(p_warm)
    p_warm.add_argument("--count", type=int, default=5, help="Number of verify calls")
    p_warm.set_defaults(func=cmd_warm)

    p_stress = sub.add_parser("stress", help="Single verify with custom (often extreme) features")
    _common_verify_args(p_stress)
    p_stress.set_defaults(func=cmd_stress)

    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
