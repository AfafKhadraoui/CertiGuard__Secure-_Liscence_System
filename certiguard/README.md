# CertiGuard SDK

CertiGuard is an offline-first SDK for on-premise software license protection. It combines cryptographic trust, host binding, runtime challenge checks, anti-debug/liveness controls, anomaly detection, and tamper-evident forensics.

## Quick Links

- Test/run guide: [`docs/HOW_TO_TEST.md`](docs/HOW_TO_TEST.md)
- Demo script and narrative: [`docs/DEMO_TEST_METHODOLOGY.md`](docs/DEMO_TEST_METHODOLOGY.md)
- Full layer map (implementation truth): [`docs/LAYERS.md`](docs/LAYERS.md)
- Architecture summary: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- Obfuscation/noise guide: [`docs/obfuscation_guide.md`](docs/obfuscation_guide.md)
- Docs index: [`docs/README.md`](docs/README.md)

## What CertiGuard Provides

- `L1` Ed25519 license signing and verification
- `L2` hardware fingerprint + optional TPM anchor checks
- `L3` installation DNA and anti-rollback counter
- `L4` challenge-response verifier flow (with IPC path where supported)
- `L5` anti-debug + heartbeat recency checks
- `L6` local behavioral anomaly and drift scoring
- `L7` honeypot payload tripwires
- `L9` per-customer watermarking
- `L10` hash-chained audit log + optional dashboard ingest sync

## Repository Structure

| Path | Purpose |
|------|---------|
| `src/certiguard/` | SDK source (`cli.py`, `license_client.py`, `dashboard.py`, `layers/*`) |
| `src/certiguard/ui/` | Vendor dashboard UI (Vite + React) |
| `tests/` | Automated tests |
| `examples/` | E2E harness + demo app scripts |
| `scripts/` | Utility scripts (e.g. smoke dashboard launcher) |
| `docs/` | Canonical docs only |
| `artifacts/noise_samples/` | Optional generated noise examples |
| `demo_runs/` | Ephemeral local demo output |

## Setup

From `certiguard/`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

Build the dashboard UI once:

```powershell
cd src\certiguard\ui
npm install
npm run build
cd ..\..\..
```

## Fast End-to-End Demo

Terminal 1 (dashboard):

```powershell
cd c:\path\to\nothingggg_us\certiguard
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = "src"
python -m certiguard.cli dashboard --audit-log "c:\path\to\nothingggg_us\certiguard\demo_runs\cg_e2e\client_state\audit.log" --port 8080
```

Terminal 2 (harness):

```powershell
cd c:\path\to\nothingggg_us\certiguard
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = "src"
python examples\cg_e2e_app\run_harness.py setup --clean
python examples\cg_e2e_app\run_harness.py verify-ok
python examples\cg_e2e_app\run_harness.py synthetic-audit
```

Open `http://localhost:8080`.

## Tests

```powershell
cd c:\path\to\nothingggg_us\certiguard
$env:PYTHONPATH = "src"
pytest tests\ -q
```

## Main CLI Commands

- `certiguard gen-keys`
- `certiguard gen-request`
- `certiguard issue-license`
- `certiguard verify`
- `certiguard run`
- `certiguard renewal-export`
- `certiguard dashboard`
- `certiguard sync-audit`
- `certiguard init-policy`
- `certiguard create-manifest` / `verify-manifest`
- `certiguard generate-noise`

Use `certiguard --help` for all flags.

