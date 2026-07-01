# How to test CertiGuard (layers, harness, dashboard)

This guide matches the **real repo layout** under `certiguard/` (the folder that contains `src/` and `examples/`). Same idea as common offline licensing: **local checks on startup**, a **tamper-evident audit trail**, optional **push to a vendor console**.

---

## Run everything from zero (start here)

### What you are running

| Piece | What it is | How you start it |
|-------|------------|------------------|
| **SDK / CLI** | Python package + `certiguard` command | `pip install -e .` then `certiguard --help` |
| **Vendor dashboard** | Flask app: serves **built** React from `src/certiguard/ui/dist` + `/api/*` | `certiguard dashboard --audit-log "<path>\audit.log" --port 8080` |
| **React dev UI** (optional) | Vite dev server; **`/api` proxied** to Flask on 8080 | `npm run dev` in `src/certiguard/ui` (open the **Vite** URL, e.g. `http://localhost:5173`) |
| **E2E harness** | Fake vendor + customer in one folder | `python examples/cg_e2e_app/run_harness.py …` with `PYTHONPATH=src` |
| **Tests** | Pytest | `pytest tests/` |

The dashboard **must** find `src/certiguard/ui/dist` (run **`npm run build`** in the UI folder once, or you get a 404 message from Flask).

### One-time install

**1) Python (from `certiguard` repo root)**

```powershell
cd c:\path\to\nothingggg_us\certiguard
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

**2) Dashboard UI build (required for `certiguard dashboard`)**

```powershell
cd src\certiguard\ui
npm install
npm run build
cd ..\..\..
```

**3) If `pip install -e .` fails on Windows** (e.g. `certiguard.exe` in use), skip reinstall and use:

```powershell
cd c:\path\to\nothingggg_us\certiguard
$env:PYTHONPATH = "src"
```

You can still run **`python -m certiguard.cli`** only if the package is importable; the harness below uses `PYTHONPATH=src` and does not need the `certiguard` script for the demo path.

---

### Path A — Full demo in two terminals (dashboard + harness)

**Terminal 1 — vendor dashboard**

```powershell
cd c:\path\to\nothingggg_us\certiguard
.\.venv\Scripts\Activate.ps1
# Use the harness default audit file (exists after setup in Terminal 2):
certiguard dashboard --audit-log demo_runs\cg_e2e\client_state\audit.log --port 8080
```

Browser opens **`http://localhost:8080`** (Flask serves the SPA + APIs). If it does not, open that URL manually.

**Terminal 2 — customer / license checks**

```powershell
cd c:\path\to\nothingggg_us\certiguard
$env:PYTHONPATH = "src"
python examples\cg_e2e_app\run_harness.py setup --clean
python examples\cg_e2e_app\run_harness.py verify-ok
python examples\cg_e2e_app\run_harness.py synthetic-audit
```

Refresh the dashboard **Audit Logs** / **Overview**: counts should move.

**Optional: attacks and L6** (same Terminal 2, same `PYTHONPATH`):

```powershell
python examples\cg_e2e_app\run_harness.py warm --times 6
python examples\cg_e2e_app\run_harness.py stress
python examples\cg_e2e_app\run_harness.py setup --clean
python examples\cg_e2e_app\run_harness.py verify-ok
python examples\cg_e2e_app\run_harness.py attack-audit
python examples\cg_e2e_app\run_harness.py verify-ok
# … then setup --clean again for more demos; see attack table below
```

**Print the exact dashboard command for your machine:**

```powershell
python examples\cg_e2e_app\run_harness.py dashboard-hint
```

---

### Path B — Hot-reload UI (Vite) + same Flask API

Use this when you are editing React.

**Terminal 1** — dashboard API + static (you can still use `dist` for accidental hits to 8080):

```powershell
certiguard dashboard --audit-log demo_runs\cg_e2e\client_state\audit.log --port 8080
```

**Terminal 2** — Vite (proxies `/api` → `http://127.0.0.1:8080` per `vite.config.ts`):

```powershell
cd src\certiguard\ui
npm run dev
```

Open the URL Vite prints (typically **`http://localhost:5173`**), **not** 8080, so client-side routing and HMR work while API calls go to Flask.

**Terminal 3** — harness (generate / push audit lines as in Path A).

---

### Path C — CLI only (manual vendor + customer)

Full copy-paste flow is in the repo **[`README.md`](../README.md)** (`gen-keys` → `gen-request` → `issue-license` → `certiguard verify`). File names there use `license.certiguard.json`; the harness uses `license.lic` — both are valid license paths as long as the CLI points at the real file.

---

### Path D — Collector push (optional)

1. Start dashboard on port **8080** (ingest is **`POST /api/logs/ingest`** on the same server).
2. In the harness terminal:

```powershell
$env:CERTIGUARD_COLLECTOR_URL = "http://127.0.0.1:8080"
python examples\cg_e2e_app\run_harness.py setup --clean --collector http://127.0.0.1:8080
python examples\cg_e2e_app\run_harness.py verify-ok
```

Each successful `verify_runtime` tries to flush unsynced lines to the dashboard.

---

### Troubleshooting

| Problem | Fix |
|---------|-----|
| `UI dist directory not found` | `cd src\certiguard\ui` → `npm install` → `npm run build` |
| `pip install -e .` WinError 32 | Close processes using `certiguard.exe`; or use `$env:PYTHONPATH="src"` only |
| Dashboard empty | Run harness **`setup`** then **`verify-ok`**; confirm `--audit-log` path matches `demo_runs\cg_e2e\client_state\audit.log` |
| Vite UI cannot load data | Flask must be on **8080**; check Vite proxy in `vite.config.ts` |

---

## Detailed topics (below)

Sections **1–3** cover **pytest**, every **harness** command, dashboard **same-file vs ingest**, and a **checklist**. Install steps are in **One-time install** above; edge cases in **Troubleshooting**. Full **CLI** walkthrough (`gen-keys`, `issue-license`, `verify`): **[`README.md`](../README.md)**.

## Three ways to test

| Method | What it proves | When to use |
|--------|----------------|-------------|
| **pytest** | Unit/integration of crypto, PoW, watermark, layers | CI and quick regression |
| **E2E harness** (`examples/cg_e2e_app/run_harness.py`) | Full `verify_runtime` path, audit chain, L6/L7 simulators | Demo and manual “does the stack hang together?” |
| **Dashboard** (`certiguard dashboard` or Flask + Vite UI) | Reading the **same** `audit.log` or **ingesting** pushed lines | Operator / vendor view |

## 1. Automated tests

```powershell
cd c:\path\to\nothingggg_us\certiguard
pytest tests\ -q
```

Important files: `tests/test_all_layers.py`, `tests/test_behavior_probe.py`, plus existing integrity / PoW / watermark tests.

## 2. End-to-end harness (generated data, no external services)

The harness creates its own **vendor keypair**, **bootstrap request**, **signed license**, **`client_state/`** (DNA, counter, policy, audit), and runs scenarios.

All commands assume **`certiguard`** as current directory and:

```powershell
$env:PYTHONPATH = "src"
```

### Fresh environment

```powershell
python examples\cg_e2e_app\run_harness.py setup --clean
```

Optional flags on `setup`:

- `--learning-days N` — L6 baseline length before enforcement (default 4).
- `--machine-probe-policy` — persist `use_machine_behavior_probe` in `policy.json`.
- `--collector http://127.0.0.1:8080` — store collector URL in the client (same effect as env for `push_audit_logs_now` after each verify).

### Happy path (L4 + L5 + L6 learning, app-supplied features)

```powershell
python examples\cg_e2e_app\run_harness.py verify-ok
python examples\cg_e2e_app\run_harness.py status
```

### L6 after learning (drift / anomaly)

Default policy uses **four** application metrics (`--features`). Run enough successful verifies to finish learning, then stress:

```powershell
python examples\cg_e2e_app\run_harness.py warm --times 6
python examples\cg_e2e_app\run_harness.py stress
```

Expect the stress step to return **`ok: false`** with code **`L6_ANOMALY`** once `learning_complete` is true and the feature vector is far from the learned mean.

### Machine probe path (six dimensions)

```powershell
python examples\cg_e2e_app\run_harness.py verify-probe
```

**Note:** L6 state is dimension-specific. If you already warmed a **4-D** baseline, the first **6-D** probe session resets the stored baseline shape (by design). For a clean probe-only demo, run `setup --clean` before `verify-probe` repeats.

### Synthetic audit lines (dashboard richness)

Requires a valid chain (empty file is valid; else run `verify-ok` first):

```powershell
python examples\cg_e2e_app\run_harness.py synthetic-audit
python examples\cg_e2e_app\run_harness.py status
```

### Attack simulators

| Command | Expected outcome |
|---------|------------------|
| `attack-audit` | Tamper an `audit.log` row (payload vs `entry_hash` mismatch); next `verify-ok` → **`AUDIT_TAMPER`** |
| `attack-honeypot` | Fake license with `PREMIUM_UNLOCK: true` in JSON suffix → verifier rejects (**`L1_L4_REJECT`**, message mentions honeypot / `L7`) |
| `attack-signature` | Flips a byte in the real license signature → **`L1_L4_REJECT`**; **re-run `setup --clean`** to restore a good license |

Order for audit attack:

```powershell
python examples\cg_e2e_app\run_harness.py verify-ok
python examples\cg_e2e_app\run_harness.py attack-audit
python examples\cg_e2e_app\run_harness.py verify-ok
```

## 3. Dashboard: same file vs ingest

### A) Single-file dashboard (simplest)

1. Print the exact path the harness uses:

```powershell
python examples\cg_e2e_app\run_harness.py dashboard-hint
```

2. In another terminal, start the dashboard pointing at that **`audit.log`** (adjust path from the hint):

```powershell
certiguard dashboard --audit-log "FULL\PATH\TO\client_state\audit.log" --port 8080
```

3. Run `verify-ok`, `synthetic-audit`, or attacks in the first terminal; refresh the browser (**`http://localhost:8080`**).

### B) Client push (collector / ingest)

1. Start dashboard with ingest API (same port as your collector URL).
2. Set **`CERTIGUARD_COLLECTOR_URL`** (PowerShell):

```powershell
$env:CERTIGUARD_COLLECTOR_URL = "http://127.0.0.1:8080"
```

3. Run harness with `--collector` on `setup` or `verify-ok` so the client is configured; each `verify_runtime` ends with a **best-effort** push of unsynced lines.

For the **React** UI served by Vite, use the repo’s documented proxy to Flask (`vite.config.ts` → `/api`) so the browser calls the same backend as the CLI collector.

## Quick checklist

- [ ] `pytest tests\` passes.
- [ ] `setup --clean` then `verify-ok` → `ok: true`, `code: OK`.
- [ ] `warm` then `stress` → `L6_ANOMALY` when policy enforces after learning.
- [ ] `attack-audit` → subsequent verify → `AUDIT_TAMPER`.
- [ ] `attack-honeypot` → verify fails before a valid signature is needed (L7).
- [ ] Dashboard shows new rows when pointed at the harness `audit.log` or after ingest.

## See also

- `docs/LAYERS.md` — slide-oriented layer reference.
- `docs/DEMO_TEST_METHODOLOGY.md` — demo narrative and methodology.
- `examples/demo_host_app.py` — smaller host-app style sample.
