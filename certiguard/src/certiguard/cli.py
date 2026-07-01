from __future__ import annotations

import argparse
import json
from pathlib import Path

from certiguard.build_noise import generate_noise_header
from certiguard.license_client import CertiGuardClient
from certiguard.config import SecurityPolicy
from certiguard.ca import issue_license
from certiguard.layers.crypto_core import generate_keypair
from certiguard.layers.integrity import file_sha256
from certiguard.layers.manifest import create_signed_manifest, verify_signed_manifest
from certiguard.layers.obfuscator import obfuscate_c_file, run_confuserex
from certiguard.layers.vm_generator import generate_vm_layer
from certiguard.layers.protector import protect_executable
from certiguard.dashboard import review_audit_logs
from certiguard.watchdog_supervisor import supervise_heartbeat_or_fail


def _cmd_gen_keys(args: argparse.Namespace) -> None:
    generate_keypair(Path(args.private_key), Path(args.public_key))
    print("Keys generated")


def _cmd_gen_request(args: argparse.Namespace) -> None:
    client = CertiGuardClient(Path(args.state_dir), collector_url=args.collector_url)
    req = client.bootstrap()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(req, indent=2), encoding="utf-8")
    print(f"Request generated: {out}")


def _cmd_issue(args: argparse.Namespace) -> None:
    if not args.exe_hash and not args.app_binary:
        raise ValueError("Provide either --exe-hash or --app-binary")
    exe_hash = args.exe_hash or file_sha256(Path(args.app_binary))
    issue_license(
        request_path=Path(args.request),
        private_key_path=Path(args.private_key),
        out_path=Path(args.out),
        issued_to=args.issued_to,
        max_users=args.max_users,
        modules=args.modules.split(","),
        valid_days=args.valid_days,
        exe_hash=exe_hash,
        k_app_b64=args.k_app_b64,
        binary_secret_b64=args.binary_secret_b64,
    )
    print(f"License issued: {args.out}")


def _cmd_protect(args: argparse.Namespace) -> None:
    metadata = protect_executable(
        exe_path=Path(args.exe),
        out_dir=Path(args.out_dir)
    )
    print(f"Binary protected in: {args.out_dir}")
    print(f"App Hash:      {metadata['app_hash']}")
    print(f"K_app (B64):   {metadata['k_app_b64']}")
    print(f"Secret (B64):  {metadata['binary_secret_b64']}")
    print("\nIMPORTANT: Pass these to 'issue-license' to link them.")


def _cmd_run(args: argparse.Namespace) -> None:
    client = CertiGuardClient(Path(args.state_dir), collector_url=args.collector_url)
    run_kw = {
        "package_dir": Path(args.package_dir),
        "license_path": Path(args.license),
        "public_key_path": Path(args.public_key),
    }
    if args.skip_layered_verify:
        run_kw["skip_layered_verify"] = True
    else:
        run_kw["heartbeat_key"] = args.heartbeat_key
        run_kw["behavior_features"] = [float(x) for x in args.features.split(",")]
        run_kw["require_tpm_if_present"] = args.require_tpm_if_present
        run_kw["app_binary_path"] = Path(args.app_binary) if args.app_binary else None
        run_kw["policy_path"] = Path(args.policy_path) if args.policy_path else None
        run_kw["use_machine_behavior_probe"] = args.machine_behavior_probe

    exit_code = client.run_protected_app(**run_kw)
    # Flush any queued audit lines when collector is configured (offline-first sync).
    client.push_audit_logs_now()
    exit(exit_code)


def _cmd_dashboard(args: argparse.Namespace) -> None:
    review_audit_logs(audit_log_path=args.audit_log, port=args.port)


def _cmd_sync_audit(args: argparse.Namespace) -> None:
    client = CertiGuardClient(Path(args.state_dir), collector_url=args.collector_url)
    if not client.collector_configured():
        raise SystemExit(
            "Configure a collector: set CERTIGUARD_COLLECTOR_URL or pass --collector-url "
            "(dashboard base URL, e.g. http://localhost:8080)"
        )
    ok = client.push_audit_logs_now()
    print(json.dumps({"synced": ok}, indent=2))


def _cmd_verify(args: argparse.Namespace) -> None:
    client = CertiGuardClient(Path(args.state_dir), collector_url=args.collector_url)
    features = [float(x) for x in args.features.split(",")]
    result = client.verify_runtime(
        license_path=Path(args.license),
        public_key_path=Path(args.public_key),
        heartbeat_key=args.heartbeat_key,
        behavior_features=features,
        require_tpm_if_present=args.require_tpm_if_present,
        app_binary_path=Path(args.app_binary) if args.app_binary else None,
        policy_path=Path(args.policy_path) if args.policy_path else None,
        use_machine_behavior_probe=args.machine_behavior_probe,
    )
    print(json.dumps(result.__dict__, indent=2))


def _cmd_renewal(args: argparse.Namespace) -> None:
    client = CertiGuardClient(Path(args.state_dir), collector_url=args.collector_url)
    key_path = Path(args.customer_private_key) if args.customer_private_key else None
    client.export_renewal_request(Path(args.out), customer_private_key_path=key_path)
    print(f"Renewal request exported: {args.out}")


def _cmd_generate_noise(args: argparse.Namespace) -> None:
    out = generate_noise_header(seed=args.seed, out_path=Path(args.out), mode=args.mode, lang=args.lang, lines=args.lines)
    print(f"Noise header generated: {out} [Mode: {args.mode}, Lang: {args.lang}]")


def _cmd_create_manifest(args: argparse.Namespace) -> None:
    files = {}
    for entry in args.file:
        path = Path(entry)
        files[str(path)] = file_sha256(path)
    create_signed_manifest(version=args.version, files=files, private_key_path=Path(args.private_key), out_path=Path(args.out))
    print(f"Signed manifest generated: {args.out}")


def _cmd_verify_manifest(args: argparse.Namespace) -> None:
    ok = verify_signed_manifest(Path(args.manifest), Path(args.public_key))
    print(json.dumps({"manifest_valid": ok}, indent=2))


def _cmd_init_policy(args: argparse.Namespace) -> None:
    policy = SecurityPolicy(
        require_tpm_if_present=args.require_tpm_if_present,
        exe_hash_grace_hours=args.exe_hash_grace_hours,
        baseline_learning_days=args.baseline_learning_days,
        anomaly_enforcement_after_learning=not args.disable_anomaly_enforcement,
        use_machine_behavior_probe=args.machine_behavior_probe,
    )
    policy.save(Path(args.out))
    print(f"Policy file written: {args.out}")


def _cmd_watchdog_supervise(args: argparse.Namespace) -> None:
    ok = supervise_heartbeat_or_fail(
        heartbeat_path=Path(args.heartbeat),
        heartbeat_key=args.heartbeat_key,
        timeout_seconds=args.timeout_seconds,
        poll_seconds=args.poll_seconds,
        max_checks=args.max_checks,
    )
    print(json.dumps({"watchdog_ok": ok}, indent=2))


def _cmd_obfuscate_source(args: argparse.Namespace) -> None:
    input_path = Path(args.input)
    output_path = Path(args.out)
    source = input_path.read_text(encoding="utf-8")
    
    obfuscated = obfuscate_c_file(
        source=source,
        seed=args.seed,
        intensity=args.intensity,
    )
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(obfuscated, encoding="utf-8")
    print(f"Obfuscated source written: {output_path} [Intensity: {args.intensity}]")


def _cmd_confuserex_protect(args: argparse.Namespace) -> None:
    confuser_path = Path(args.confuserex) if args.confuserex else None
    ok = run_confuserex(
        input_assembly=Path(args.input),
        output_dir=Path(args.out),
        confuserex_path=confuser_path,
    )
    if not ok:
        raise SystemExit(1)


def _cmd_generate_vm(args: argparse.Namespace) -> None:
    mapping = generate_vm_layer(
        out_header=Path(args.out),
        seed=args.seed,
    )
    print(f"[*] Polymorphic VM Header generated: {args.out} [Seed: {args.seed}]")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="certiguard")
    sub = parser.add_subparsers(required=True)

    gen_keys = sub.add_parser("gen-keys", help="Generate Ed25519 keys")
    gen_keys.add_argument("--private-key", required=True)
    gen_keys.add_argument("--public-key", required=True)
    gen_keys.set_defaults(func=_cmd_gen_keys)

    gen_req = sub.add_parser("gen-request", help="Generate .cgreq request")
    gen_req.add_argument("--state-dir", required=True)
    gen_req.add_argument("--out", required=True)
    gen_req.add_argument(
        "--collector-url",
        default=None,
        help="Dashboard base URL for audit sync; overrides CERTIGUARD_COLLECTOR_URL for this process",
    )
    gen_req.set_defaults(func=_cmd_gen_request)

    issue = sub.add_parser("issue-license", help="Issue signed license")
    issue.add_argument("--request", required=True)
    issue.add_argument("--private-key", required=True)
    issue.add_argument("--out", required=True)
    issue.add_argument("--issued-to", required=True)
    issue.add_argument("--max-users", type=int, required=True)
    issue.add_argument("--modules", required=True, help="Comma-separated modules")
    issue.add_argument("--valid-days", type=int, default=365)
    issue.add_argument("--app-binary")
    issue.add_argument("--exe-hash")
    issue.add_argument("--k-app-b64", help="From 'protect' command")
    issue.add_argument("--binary-secret-b64", help="From 'protect' command")
    issue.set_defaults(func=_cmd_issue)

    protect = sub.add_parser("protect", help="Encrypt binary (ShieldWrap)")
    protect.add_argument("--exe", required=True, help="Binary to encrypt")
    protect.add_argument("--out-dir", required=True, help="Folder for app.enc + manifest.json")
    protect.set_defaults(func=_cmd_protect)

    run = sub.add_parser(
        "run",
        help="Run encrypted binary (ShieldWrap). By default runs full verify_runtime before decrypt (L5→L10→L4→L5→L2→L6); use --skip-layered-verify for crypto-only path.",
    )
    run.add_argument("--package-dir", required=True)
    run.add_argument("--license", required=True)
    run.add_argument("--public-key", required=True)
    run.add_argument("--state-dir", required=True)
    run.add_argument(
        "--skip-layered-verify",
        action="store_true",
        help="Only Ed25519 + ShieldWrap unwrap (no anti-debug, challenge, heartbeat, anomaly). Not recommended.",
    )
    run.add_argument(
        "--heartbeat-key",
        default="dev-heartbeat",
        help="Shared secret for PoW heartbeat (ignored if --skip-layered-verify)",
    )
    run.add_argument(
        "--features",
        default="20,10,3,30",
        help="Comma-separated behavior_features for L6 (same as verify)",
    )
    run.add_argument(
        "--require-tpm-if-present",
        action="store_true",
        help="Same as verify (ignored with --skip-layered-verify)",
    )
    run.add_argument("--app-binary", help="Optional app path for exe-hash policy during layered verify")
    run.add_argument("--policy-path", help="Optional security policy JSON during layered verify")
    run.add_argument(
        "--machine-behavior-probe",
        action="store_true",
        help="L6: use machine probe (same as verify --machine-behavior-probe)",
    )
    run.add_argument(
        "--collector-url",
        default=None,
        help="Dashboard base URL for audit sync; overrides CERTIGUARD_COLLECTOR_URL for this process",
    )
    run.set_defaults(func=_cmd_run)

    dashboard = sub.add_parser("dashboard", help="Launch the vendor security dashboard")
    dashboard.add_argument("--audit-log", required=True, help="Path to audit.log file")
    dashboard.add_argument("--port", type=int, default=8080, help="Port to serve on")
    dashboard.set_defaults(func=_cmd_dashboard)

    sync_audit = sub.add_parser(
        "sync-audit",
        help="Push unsynced local audit.log lines to the dashboard (offline queue flush)",
    )
    sync_audit.add_argument("--state-dir", required=True)
    sync_audit.add_argument(
        "--collector-url",
        default=None,
        help="Dashboard base URL; overrides CERTIGUARD_COLLECTOR_URL",
    )
    sync_audit.set_defaults(func=_cmd_sync_audit)

    verify = sub.add_parser("verify", help="Run full verification")
    verify.add_argument("--state-dir", required=True)
    verify.add_argument("--license", required=True)
    verify.add_argument("--public-key", required=True)
    verify.add_argument("--heartbeat-key", required=True)
    verify.add_argument(
        "--features",
        default="20,10,3,30",
        help="active_users,hour_of_day,unique_machines_24h,api_calls_per_min",
    )
    verify.add_argument(
        "--require-tpm-if-present",
        action="store_true",
        help="Fail verification if TPM exists locally but license is not TPM-bound",
    )
    verify.add_argument("--app-binary", help="Path to app binary for exe-hash integrity policy")
    verify.add_argument("--policy-path", help="Optional security policy JSON")
    verify.add_argument(
        "--machine-behavior-probe",
        action="store_true",
        help="L6: score psutil CPU/RAM/process + GPU heuristics (ignores --features vector)",
    )
    verify.add_argument(
        "--collector-url",
        default=None,
        help="Dashboard base URL for audit sync; overrides CERTIGUARD_COLLECTOR_URL",
    )
    verify.set_defaults(func=_cmd_verify)

    renewal = sub.add_parser("renewal-export", help="Export renewal request")
    renewal.add_argument("--state-dir", required=True)
    renewal.add_argument("--out", required=True)
    renewal.add_argument("--customer-private-key", help="Optional customer key to sign renewal export")
    renewal.add_argument(
        "--collector-url",
        default=None,
        help="Dashboard base URL for audit sync; overrides CERTIGUARD_COLLECTOR_URL",
    )
    renewal.set_defaults(func=_cmd_renewal)

    noise = sub.add_parser("generate-noise", help="Generate per-build dynamic noise header/class")
    noise.add_argument("--seed", type=int, required=True)
    noise.add_argument("--out", required=True)
    noise.add_argument("--mode", choices=["rule", "smart", "polymorphic"], default="rule")
    noise.add_argument("--lang", choices=["c", "csharp"], default="c")
    noise.add_argument("--lines", type=int, default=24)
    noise.set_defaults(func=_cmd_generate_noise)

    manifest_create = sub.add_parser("create-manifest", help="Create signed update manifest")
    manifest_create.add_argument("--version", required=True)
    manifest_create.add_argument("--private-key", required=True)
    manifest_create.add_argument("--out", required=True)
    manifest_create.add_argument("--file", action="append", required=True, help="File path (repeat for multiple files)")
    manifest_create.set_defaults(func=_cmd_create_manifest)

    manifest_verify = sub.add_parser("verify-manifest", help="Verify signed update manifest")
    manifest_verify.add_argument("--manifest", required=True)
    manifest_verify.add_argument("--public-key", required=True)
    manifest_verify.set_defaults(func=_cmd_verify_manifest)

    policy = sub.add_parser("init-policy", help="Create security policy config file")
    policy.add_argument("--out", required=True)
    policy.add_argument("--require-tpm-if-present", action="store_true")
    policy.add_argument("--exe-hash-grace-hours", type=int, default=72)
    policy.add_argument("--baseline-learning-days", type=int, default=30)
    policy.add_argument("--disable-anomaly-enforcement", action="store_true")
    policy.add_argument(
        "--machine-behavior-probe",
        action="store_true",
        help="Persist use_machine_behavior_probe=true so L6 uses CPU/RAM/GPU snapshot",
    )
    policy.set_defaults(func=_cmd_init_policy)

    watchdog = sub.add_parser("watchdog-supervise", help="Supervise verifier heartbeat health")
    watchdog.add_argument("--heartbeat", required=True)
    watchdog.add_argument("--heartbeat-key", required=True)
    watchdog.add_argument("--timeout-seconds", type=int, default=60)
    watchdog.add_argument("--poll-seconds", type=int, default=5)
    watchdog.add_argument("--max-checks", type=int)
    watchdog.set_defaults(func=_cmd_watchdog_supervise)

    obfuscate = sub.add_parser("obfuscate-source", help="Apply Agile.NET-style obfuscation to a C source file")
    obfuscate.add_argument("--input", required=True, help="Input .c file")
    obfuscate.add_argument("--out", required=True, help="Output obfuscated .c file")
    obfuscate.add_argument("--seed", type=int, default=0, help="Random seed")
    obfuscate.add_argument("--intensity", type=int, default=3, choices=[1,2,3,4,5],
                           help="Obfuscation intensity 1-5 (default: 3)")
    obfuscate.set_defaults(func=_cmd_obfuscate_source)

    confuserex = sub.add_parser("confuserex-protect", help="Apply ConfuserEx protection to a .NET assembly")
    confuserex.add_argument("--input", required=True, help="Path to .exe or .dll")
    confuserex.add_argument("--out", required=True, help="Output directory for protected assembly")
    confuserex.add_argument("--confuserex", help="Path to Confuser.CLI.exe (auto-detected if in PATH)")
    confuserex.set_defaults(func=_cmd_confuserex_protect)

    vm = sub.add_parser("generate-vm", help="Generate a polymorphic VM protection layer (C header)")
    vm.add_argument("--out", required=True, help="Output .h header file")
    vm.add_argument("--seed", type=int, default=42, help="Random seed for ISA generation")
    vm.set_defaults(func=_cmd_generate_vm)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

