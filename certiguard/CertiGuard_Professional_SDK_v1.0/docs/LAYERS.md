# CertiGuard — Complete implementation reference (slide & audit source)

**Purpose of this document:** Single source of truth for **what is implemented** in `nothingggg_us/certiguard/`, mapped to security layers, CLI, APIs, tests, and **slide-deck structure**. Copy sections verbatim into presentations; tables are designed for one-slide-per-block export.

**Audience:** Engineering, product, judges, internal audits.

**Canonical code root:** `nothingggg_us/certiguard/src/certiguard/`  
**Hackathon narrative / pseudo-code:** [`nothingggg_us/docs/CertiGuard_Final_Implementation.md`](../../docs/CertiGuard_Final_Implementation.md)  
**Demo runbook:** [`DEMO_TEST_METHODOLOGY.md`](./DEMO_TEST_METHODOLOGY.md)  
**Hands-on testing (harness + dashboard):** [`HOW_TO_TEST.md`](./HOW_TO_TEST.md)

---

## How to turn this file into slides (recommended deck order)

| Slide # | Section in this doc |
|--------:|----------------------|
| 1 | Title + Executive summary |
| 2 | Problem framing (use Final Implementation doc Part 1 or README) |
| 3 | “10-layer” diagram — use **Alignment: hackathon vs repo** |
| 4 | Repository tree + dependencies |
| 5 | Layer quick reference table |
| 6–14 | One slide per layer **L1–L7, L9, L10** (use **Slide bullets** under each) |
| 15 | Cross-cutting: ShieldWrap, manifest, noise, storage |
| 16 | Runtime orchestration order |
| 17 | CLI command matrix |
| 18 | Client `state_dir` artifacts |
| 19 | Dashboard API + UI |
| 20 | Audit events + verification codes |
| 21 | Testing & CI commands |
| 22 | Roadmap / honest limits |

---

## Alignment: hackathon diagram vs this repository

The **Final Implementation** guide labels **L6 = Dead Man’s Switch + PoW** and **L8 = Behavioral AI**. This **repository** orders operations to match `CertiGuardClient.verify_runtime`:

| Guide (slide) | Implemented in repo |
|---------------|---------------------|
| **L5** Anti-debug + integrity + grace | **`layers/antidebug.py`** at start of `verify_runtime` + **exe-hash grace** in **`layers/verifier_server.py`** (`integrity_grace.json`) |
| **L6** Dead Man’s Switch + PoW | **`layers/watchdog.py`** (PoW chain + recency) + **`watchdog_supervisor.py`**; invoked **after** L4 challenge in **`license_client.py`** |
| **L8** Behavioral AI | **`layers/anomaly.py`** + **`layers/behavior_probe.py`** — documented here as **L6 (behavioral)** because it shares the **post-heartbeat** block in code |
| **L8 unused** | No separate module; slides may keep “L8” label for ML while code says **L6** |

**L1–L4, L7, L9, L10** align **one-to-one** with the guide at the concept level.

---

## Executive summary (elevator pitch)

CertiGuard is an **offline-first** Python SDK for **on-premise** license protection: **Ed25519** trust (**L1**), **hardware + optional TPM** binding (**L2**), **encrypted install DNA + HMAC boot counter** (**L3**), **challenge–response** with optional **IPC verifier** (**L4**), **anti-debug + PoW heartbeat / dead-man’s switch** (**L5**), **Isolation Forest + drift** with optional **machine probe** (CPU/RAM/GPU heuristics) (**L6 behavioral**), **honeypot JSON tripwires** (**L7**), **signed watermark** (**L9**), **hash-chained audit log** + optional **dashboard sync** (**L10**). **ShieldWrap** encrypts application binaries; **`run_protected_app`** defaults to **full stack before decrypt**. Nothing claims impossible security on a fully compromised host—the design raises **cost** and leaves **evidence**.

---

## Repository layout (`nothingggg_us/certiguard/`)

```
certiguard/
├── pyproject.toml              # Package metadata + dependencies
├── README.md                   # Quick start, CLI examples
├── .gitignore                  # Ignores demo_runs output, venv, egg-info, node_modules
├── docs/                       # LAYERS, HOW_TO_TEST, DEMO_TEST_METHODOLOGY, …
├── examples/
│   ├── README.md               # Example index + CLI snippet
│   ├── cg_e2e_app/run_harness.py
│   └── demo_host_app.py        # Scripted verify driver (ping / warm / stress)
├── scripts/
│   └── smoke_dashboard.py      # Optional: launch Flask dashboard manually
├── artifacts/noise_samples/    # Sample noise generator outputs (optional)
├── demo_runs/                  # Ephemeral harness output (.gitkeep only in repo)
├── tests/                      # pytest collection
│   ├── test_all_layers.py      # L1 + L7 + L10 aggregate smoke
│   ├── test_pow_heartbeat.py   # L5 PoW chain
│   ├── test_license_watermark.py  # L9 watermark
│   ├── test_honeypot_tripwire.py  # L7 honeypot via verify_runtime
│   ├── test_antidebug.py
│   ├── test_behavior_probe.py
│   └── test_integrity.py
└── src/certiguard/
    ├── __init__.py
    ├── cli.py                  # `certiguard` console entry
    ├── license_client.py       # CertiGuardClient: bootstrap, verify_runtime, run, renewal, sync
    ├── config.py               # SecurityPolicy dataclass + JSON load/save
    ├── models.py               # VerificationResult
    ├── ca.py                   # Vendor: issue_license (+ L9 watermark)
    ├── dashboard.py            # Flask vendor UI + REST + ingest
    ├── verifier_daemon.py      # Unix-socket verifier subprocess entry
    ├── watchdog_supervisor.py  # External heartbeat polling helper
    ├── build_noise.py          # Polymorphic / demo native noise generation
    ├── layers/
    │   ├── __init__.py
    │   ├── crypto_core.py      # L1: Ed25519, HKDF, AES-GCM, sign/verify payload
    │   ├── hardware.py         # L2: CPU + board → SHA-256 fingerprint
    │   ├── tpm.py              # L2: TPM metadata anchor
    │   ├── dna.py              # L3: install UUID, AES-GCM, timeline, session key
    │   ├── counter.py          # L3: monotonic boot counter + HMAC
    │   ├── verifier_server.py  # L4 + L1 verify path + L7 honeypot + grace + HMAC response
    │   ├── verifier_ipc.py     # L4: optional AF_UNIX verifier process
    │   ├── integrity.py        # file_sha256
    │   ├── antidebug.py        # L5: debugger / process / timing heuristics
    │   ├── watchdog.py         # L5: PoW heartbeat chain + DMS recency
    │   ├── anomaly.py          # L6: IsolationForest + baseline + drift
    │   ├── behavior_probe.py   # L6: psutil + GPU/display heuristics → 6-D vector
    │   ├── audit.py            # L10: append_event, verify_chain
    │   ├── sync.py             # L10: offline queue → POST /api/logs/ingest
    │   ├── storage.py          # Atomic JSON writes
    │   ├── protector.py        # ShieldWrap: encrypt exe → app.enc + manifest
    │   └── manifest.py         # Signed update manifests
    └── ui/                     # Vite + React dashboard (build → ui/dist)
        ├── package.json
        ├── vite.config.ts      # Dev proxy /api → Flask
        └── src/…               # Pages: Overview, Clients, Blacklist, Audit Logs, Risk, Settings
```

---

## Dependencies (`pyproject.toml`)

| Package | Role |
|---------|------|
| `cryptography` | Ed25519, AES-GCM, HKDF |
| `psutil` | Machine behavior probe (L6), system metrics |
| `scikit-learn`, `numpy` | IsolationForest (L6) |
| `flask`, `flask-cors` | Vendor dashboard API + static UI host |
| `requests` | Client audit sync to collector (`sync.py`) |

**Python:** `>= 3.10`  
**Console script:** `certiguard` → `certiguard.cli:main`

---

## Layer quick reference (threat → module)

| Layer | Name | Threat focus | Primary paths |
|:-----:|------|----------------|---------------|
| **L1** | Cryptographic core | Forged / altered license | `layers/crypto_core.py`, `ca.py`, `verifier_server` |
| **L2** | Hardware + TPM | License copied to other machine | `layers/hardware.py`, `layers/tpm.py` |
| **L3** | DNA + boot counter | Clone, rollback, replay | `layers/dna.py`, `layers/counter.py` |
| **L4** | Challenge–response | Stale verify, env drift, binary hash | `verifier_server.py`, `verifier_ipc.py`, `verifier_daemon.py` |
| **L5** | Anti-debug + PoW DMS | Debuggers, “verify once” | `antidebug.py`, `watchdog.py`, `watchdog_supervisor.py` |
| **L6** | Behavioral AI (+ probe) | Abuse / odd host profile | `anomaly.py`, `behavior_probe.py` |
| **L7** | Honeypot | Fake unlock keys in JSON | `check_honeypot_tripwire` in `verifier_server.py` |
| **L9** | Watermark | Leaked license attribution | `ca.py` |
| **L10** | Audit chain + sync | Forensics, central visibility | `audit.py`, `license_client.py`, `sync.py`, `dashboard.py` |

**Not a numbered layer:** ShieldWrap (`protector.py` + `run_protected_app`), signed manifests (`manifest.py`), build noise (`build_noise.py`).

---

## L1 — Cryptographic core

**Purpose:** Mathematical unforgeability of license bytes after issuance.

**Implemented in:** `layers/crypto_core.py`, `ca.py`, `verifier_server.verify_payload` path.

**Mechanics:**

- Payload serialized as **canonical JSON** (`sort_keys=True`, minimal separators).
- On disk: **64-byte Ed25519 signature** ‖ **UTF-8 JSON** (base64-wrapped in `.lic` style files).
- **HKDF-SHA256** + **AES-256-GCM** for ShieldWrap key material and binary decryption.

**Slide bullets**

- Private key **never** ships to customer; only public key verifies.
- Tampering any signed byte invalidates the signature.

**Tests:** `tests/test_all_layers.py` (sign + corrupt), `tests/test_license_watermark.py` (signed payload differs per customer).

**Limits:** Trust anchor is **your** public key distribution (`CERTIGUARD_PUBLIC_KEY_HEX` optional in verifier).

---

## L2 — Hardware fingerprint + TPM anchor

**Purpose:** Bind license to **this machine**.

**Implemented in:** `layers/hardware.py`, `layers/tpm.py`, `verifier_server` (constant-time compare vs `hardware_fingerprint`), `license_client.run_protected_app` (HKDF IKM includes HW + optional TPM).

**Mechanics:**

- Fingerprint = **SHA-256**(`cpu_id | board_serial | VENDOR_SALT`).
- Windows: WMI-style `wmic` queries; Linux: `/proc/cpuinfo`, DMI paths.
- TPM **anchor** = SHA-256 over platform/manufacturer/version strings when TPM exists.

**Slide bullets**

- Casual “copy .lic to laptop” fails at verify.
- Optional TPM strengthens binding when license encodes anchor.

**Limits:** Hardware changes; TPM path is **metadata**, not full attestation.

---

## L3 — Installation DNA + boot counter

**Purpose:** Resist **clone**, **snapshot replay**, **clock games**.

**Implemented in:** `layers/dna.py`, `layers/counter.py`; consumed in `verifier_server` + `verify_challenge_response`.

**Mechanics:**

- Install UUID + snapshots, **AES-GCM** at rest keyed from hardware fingerprint.
- **Timeline validation** on DNA updates.
- Boot counter: **monotonic** with **HMAC-SHA256** over `(count, hw_fp)`.
- Session key derivation feeds **L4** HMAC.

**Slide bullets**

- Three-way binding: license DNA fields vs local encrypted state vs counter.

**Limits:** Host with full control may still attempt targeted attacks; L1/L4 tie policy to signed fields.

---

## L4 — Challenge–response verifier

**Purpose:** Every verification cycle proves **fresh** possession of secrets + license hash.

**Implemented in:** `layers/verifier_server.py` (`verify_license_and_respond`), `layers/verifier_ipc.py`, `verifier_daemon.py`, `license_client.verify_runtime` (challenge + response check).

**Verifier pipeline (high level):**

1. **L7** `check_honeypot_tripwire` on raw bytes.
2. **L1** `verify_payload` → JSON payload.
3. Validity window (`valid_until`, `issued_at`).
4. **L2** hardware fingerprint match (`hmac.compare_digest`).
5. **L3** boot counter ≥ `boot_count_at_issue`; DNA uuid/first-boot match; timeline update.
6. Optional **TPM** match if license encodes anchor.
7. Optional **exe hash** vs `app_binary_path` with **grace** file `integrity_grace.json`.
8. Emit **HMAC-SHA256** over `license_hash ‖ challenge_nonce` using DNA-derived session key.

**Slide bullets**

- Optional **separate process** + Unix socket on platforms with `AF_UNIX`; Windows **in-process** fallback.

**Limits:** IPC isolation is **helper-grade**, not a verified enclave.

---

## L5 — Anti-debug + PoW heartbeat (dead man’s switch)

**Purpose:** Raise cost of interactive tampering; prove **liveness** after crypto path.

**Implemented in:** `layers/antidebug.py`, `layers/watchdog.py`, `watchdog_supervisor.py`, `license_client.verify_runtime`.

**Mechanics:**

- `debugger_detected()` → fail **`L5_DEBUG`**, audit `debug_detected`.
- Heartbeat file: append-only JSON lines; each line **mines** SHA-256 with **5-hex leading zeros**; **chain** via previous hash; **heartbeat_key** in preimage (v2) + **legacy** verify for old lines.
- `verify_heartbeat_recent(..., timeout_seconds=60)` → **`L5_DMS`** if stale; audit `heartbeat_stale`.

**Slide bullets**

- PoW makes forging the next line CPU-expensive.
- Supervisor CLI polls the same file for ops demos.

**CLI:** `certiguard watchdog-supervise --heartbeat … --heartbeat-key …`

**Tests:** `tests/test_pow_heartbeat.py`

**Limits:** No built-in OS **kill** of protected PID on silence—integrator wires supervisor policy.

---

## L6 — Behavioral AI + machine probe

**Purpose:** Catch **misuse** and coarse **environment weirdness** after crypto passes.

**Implemented in:** `layers/anomaly.py`, `layers/behavior_probe.py`, `license_client.verify_runtime`.

**Modes:**

- **Application features:** 4 floats (e.g. users, hour, machines, API rate) — synthetic IF baseline dim 4.
- **Machine probe:** `--machine-behavior-probe` or `SecurityPolicy.use_machine_behavior_probe` → **6 floats** (CPU%, cores, RAM%, process scale, GPU signal, hour); IF baseline dim 6.
- **Policy:** `baseline_learning_days`, `anomaly_enforcement_after_learning` from `config.py` / `policy.json`.

**Audit:** `behavior_check` JSON includes `feature_source`, `feature_dim`, optional `behavior_probe` summary.

**Slide bullets**

- Same code path for “fraud no signature sees” story.
- Probe is **best-effort** GPU/display strings—not attestation.

**Tests:** `tests/test_behavior_probe.py`, `examples/demo_host_app.py`

---

## L7 — Honeypot tripwire

**Purpose:** Fail closed on **unlock fantasy** keys in the **unsigned** JSON tail.

**Implemented in:** `verifier_server.check_honeypot_tripwire` (before `verify_payload`).

**Keys:** `PREMIUM_UNLOCK`, `ADMIN_OVERRIDE`, `DEBUG_MODE`, `FEATURE_FLAG_XYZ` — reject `true`, non-zero numbers, string truth tokens (`yes`, `1`, …), non-empty `FEATURE_FLAG_XYZ` collections; allow absent key or explicit `false` / `0`.

**Slide bullets**

- Catches “Notepad hero” who toggles booleans before understanding signatures.

**Tests:** `tests/test_all_layers.py`

---

## L9 — License watermarking

**Purpose:** Signed, compact **customer + hardware** fingerprint inside payload.

**Implemented in:** `ca.py` — `watermark` = first 16 hex chars of `SHA-256(issued_to | hardware_fingerprint)`.

**Tests:** `tests/test_license_watermark.py`

**Limits:** Visible in JSON; for attribution not secrecy.

---

## L10 — Tamper-evident audit + dashboard

**Purpose:** Append-only **hash chain** per client; optional **push** to vendor log.

**Implemented in:** `layers/audit.py` (`append_event`, `verify_chain`), `license_client` (many writers), `layers/sync.py`, `dashboard.py`.

**Client → vendor sync:** `CERTIGUARD_COLLECTOR_URL` + `SyncManager` (`sync_meta.json` line cursor); CLI `sync-audit`; ingest `POST /api/logs/ingest`.

**Dashboard severity** (for UI badges): critical / high / medium / info heuristics in `dashboard._classify_severity` including `heartbeat_stale`, `tpm_policy_fail`, etc.

**Slide bullets**

- Same events power **renewal export** for vendor forensics.

**Tests:** `tests/test_all_layers.py`, manual dashboard smoke.

---

## ShieldWrap (binary protection)

**Implemented in:** `layers/protector.py`, `license_client.run_protected_app`, `ca.issue_license` (ShieldWrap fields when issuing protected apps).

**Flow:** Vendor protects exe → `app.enc` + `manifest.json`; license carries seeds/secrets; client derives keys from **HW + TPM + license**; **default `run`** calls **`verify_runtime` first** (exit **2** on layer failure, no decrypt).

**CLI:** `certiguard protect`, `certiguard run` (see CLI matrix).

---

## `CertiGuardClient` API (integration surface)

| Method | Role |
|--------|------|
| `bootstrap()` | First-run registration payload (**L2/L3** seeds) |
| `verify_runtime(...)` | Full layer stack; returns `VerificationResult` |
| `run_protected_app(...)` | ShieldWrap unwrap + subprocess; **full verify** unless `skip_layered_verify` |
| `export_renewal_request(...)` | Ships audit + DNA + counter JSON for vendor |
| `push_audit_logs_now()` / `collector_configured()` | Optional **L10** sync |

**Constructor:** `CertiGuardClient(state_dir, collector_url=...)` — collector overrides `CERTIGUARD_COLLECTOR_URL`.

---

## `VerificationResult` codes (for slides / support)

| `code` | Typical cause |
|--------|----------------|
| `OK` | All gated checks passed |
| `L5_DEBUG` | Anti-debug triggered |
| `AUDIT_TAMPER` | `audit.log` chain broken |
| `L1_L4_REJECT` | Verifier exception (signature, binding, expiry, honeypot, DNA, …) |
| `L4_CHALLENGE` | HMAC challenge mismatch |
| `L5_DMS` | Heartbeat missing/stale |
| `L2_TPM` | TPM anchor mismatch |
| `L2_TPM_POLICY` | TPM present but license not TPM-bound when policy requires |
| `L6_ANOMALY` | IsolationForest / drift enforcement after learning |

---

## Audit log event types written by the SDK

| `event` | When |
|---------|------|
| `debug_detected` | Anti-debug positive |
| `license_reject` | Verifier raised (payload in `reason`) |
| `challenge_fail` | HMAC response check failed |
| `heartbeat_stale` | DMS / recency failed |
| `tpm_mismatch` | Runtime TPM vs license |
| `tpm_policy_fail` | Policy requires TPM binding; license not bound |
| `behavior_check` | Every successful L6 scoring pass (includes scores, probe metadata) |

Renewal export embeds full `audit.log` text for vendor review.

---

## CLI command matrix (`certiguard --help`)

| Command | Purpose |
|---------|---------|
| `gen-keys` | Create Ed25519 PEM keypair |
| `gen-request` | Client registration JSON from `state_dir` |
| `issue-license` | Vendor: sign license from `.cgreq` |
| `protect` | ShieldWrap: encrypt `--exe` → `--out-dir` |
| `run` | Decrypt + run protected app (**full verify** by default) |
| `verify` | Run `verify_runtime` once, print JSON |
| `dashboard` | Flask + built React UI on `--port`, `--audit-log` |
| `sync-audit` | Flush local `audit.log` lines to collector |
| `renewal-export` | Write renewal JSON (+ optional customer sign) |
| `init-policy` | Write `policy.json` (grace, learning, TPM, probe flags) |
| `watchdog-supervise` | Poll heartbeat file until fail or max checks |
| `generate-noise` | Build-time noise header/class |
| `create-manifest` / `verify-manifest` | Signed file manifests |

**Notable flags:** `--machine-behavior-probe`, `--skip-layered-verify` (run only), `--collector-url`, verify/run shared heartbeat + features options.

---

## Client `state_dir` artifacts

| File | Layer / role |
|------|----------------|
| `dna.json` | L3 install DNA (encrypted) |
| `counter.json` | L3 boot counter + HMAC |
| `audit.log` | L10 hash-chained events |
| `heartbeat.json` | L5 PoW heartbeat lines (NDJSON) |
| `behavior_baseline.json` | L6 rolling baseline |
| `integrity_grace.json` | L4 exe-hash grace window |
| `policy.json` | `SecurityPolicy` |
| `sync_meta.json` | L10 sync line cursor |
| `license_verifier.sock` | L4 IPC (Unix only, runtime) |

---

## Dashboard REST API + UI

**Server:** `dashboard.py` — serves `ui/dist`, CORS enabled.

| HTTP | Path | Role |
|------|------|------|
| GET | `/api/logs` | NDJSON audit lines as JSON array (newest first) |
| POST | `/api/logs/ingest` | Append client-pushed lines (`machine_id`, `logs[]`) |
| GET | `/api/overview` | Stats + charts + recent events |
| GET | `/api/clients` | Per-fingerprint rollups from logs |
| GET | `/api/blacklist` | Critical/high fingerprint set |
| GET | `/api/risk` | Risk aggregates for charts |
| GET | `/*` | SPA static + `index.html` fallback |

**UI routes (React):** `/`, `/clients`, `/clients/:id`, `/blacklist`, `/audit-logs`, `/risk-analysis`, `/settings` — API base via `src/app/lib/apiBase.ts` (same-origin or `VITE_DASHBOARD_API_BASE`); Vite dev proxy `/api` → Flask.

**Prerequisite:** `npm run build` in `src/certiguard/ui/` so `ui/dist` exists.

---

## Environment variables

| Variable | Effect |
|----------|--------|
| `CERTIGUARD_COLLECTOR_URL` | Base URL for `sync.py` / `push_audit_logs_now` (`/api/logs/ingest`) |
| `CERTIGUARD_PUBLIC_KEY_HEX` | Optional embedded public key in verifier (else PEM path) |

---

## `SecurityPolicy` JSON (`config.SecurityPolicy`)

| Field | Default | Meaning |
|-------|---------|---------|
| `require_tpm_if_present` | `false` | Fail if TPM exists but license not TPM-bound |
| `exe_hash_grace_hours` | `72` | Grace for exe hash mismatch |
| `baseline_learning_days` | `30` | Sessions before L6 enforcement |
| `anomaly_enforcement_after_learning` | `true` | Enforce L6 only after learning complete |
| `use_machine_behavior_probe` | `false` | Use `behavior_probe` vector instead of CLI `features` |

---

## Threat → layer coverage (slide matrix)

| Attack story | Layers that resist / detect |
|--------------|----------------------------|
| Edit `max_users` in JSON | **L1** signature fail; **L7** if honeypot keys toggled |
| Copy license to new PC | **L2** fingerprint; **L3** DNA decrypt mismatch |
| VM snapshot rollback | **L3** timeline + counter vs license |
| Patch verifier / skip check | **L4** challenge without secrets; IPC story |
| Attach debugger | **L5** antidebug |
| Kill app, leave license “valid” on disk | **L5** DMS next `verify_runtime` |
| Scripted unlock flags | **L7** |
| Abuse within valid license | **L6** |
| Leak `.lic`, deny origin | **L9** watermark |
| Deny an event happened | **L10** chain; vendor **dashboard** |

---

## Testing — run everything (copy-paste)

From `nothingggg_us/certiguard/`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
$env:PYTHONPATH = "src"
python -m pytest tests/ -v
python tests/test_all_layers.py
pytest tests/test_pow_heartbeat.py tests/test_license_watermark.py -q
```

**UI build (dashboard):**

```powershell
cd src\certiguard\ui
npm install
npm run build
cd ..\..\..
certiguard dashboard --audit-log demo_runs\cg_e2e\client_state\audit.log --port 8080
```

All **`pytest tests/`** cases + standalone scripts above should **pass** on a healthy checkout (Windows paths as shown; adjust for bash).

---

## Implementation status (repo truth)

| Area | Status |
|------|--------|
| L1–L4, L7, L9, L10 | Implemented |
| L5 anti-debug + PoW DMS + supervisor | Implemented |
| L6 ML + drift + machine probe + policy | Implemented |
| ShieldWrap protect/run | Implemented (`run` defaults full stack) |
| Dashboard Flask + React + ingest + sync | Implemented |
| Verifier IPC daemon | Unix `AF_UNIX`; Windows in-process fallback |
| HSM, full TPM attestation, SIEM connectors | **Not** implemented (roadmap) |

---

## Roadmap (honest backlog)

- Stronger isolated verifier service (hardened process boundary).
- Full **kill-on-silence** integration (host policy / service wrapper).
- TPM **attestation** (AK/EK flows), HSM-backed issuance.
- Formal SIEM / webhook exporters.
- Single **e2e** pytest that drives `verify_runtime` with temp keys + license (extends `test_all_layers`).

---

## Document maintenance

| Artifact | Path |
|----------|------|
| This reference | `certiguard/docs/LAYERS.md` |
| Demo script | `certiguard/docs/DEMO_TEST_METHODOLOGY.md` |
| Hackathon prose | `nothingggg_us/docs/CertiGuard_Final_Implementation.md` |
| Product README | `certiguard/README.md` |

**Slide tip:** Say once—**guide L6/L8** vs **code L5/L6 behavioral**—then use **this file’s** numbering for the rest of the talk.
