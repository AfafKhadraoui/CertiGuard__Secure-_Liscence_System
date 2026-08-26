# CertiGuard SDK — Software Development Methodology

## Document Purpose

This document describes the software development methodology used to design and implement **CertiGuard SDK**, an offline-first Python security SDK for protecting on-premise software licenses with ten defense layers.

It is written for a hackathon audience: judges, technical mentors, and engineering stakeholders who need to understand **why** decisions were made, **how** they were implemented, and **how** they were validated.

---

## Project Summary

CertiGuard SDK secures license validation in fully offline environments using 10 integrated security layers:

1. Ed25519 cryptographic signing and verification
2. Hardware fingerprint binding
3. Installation DNA and anti-rollback timeline checks
4. Separate verifier process and challenge-response validation
5. Anti-debug checks
6. Dead Man's Switch with Proof-of-Work heartbeat
7. Honeypot license fields (tripwire)
8. Isolation Forest behavioral AI detection
9. Per-customer license watermarking
10. Hash-chained tamper-evident audit log

The guiding objective is practical: **raise attack cost, detect tampering early, and preserve forensic evidence**, while keeping integration simple for host applications.

---

## 1. Development Approach

### 1.1 Why We Chose Python (not C, not Java)

For a hackathon setting, we optimized for **delivery speed + architectural completeness** rather than low-level micro-optimization.

**Reasons for Python:**

- **Rapid implementation velocity**: enabled fast prototyping and iteration of multiple security layers in parallel.
- **Strong ecosystem fit**:
   - `cryptography` for reliable Ed25519 workflows
  - `scikit-learn` for Isolation Forest anomaly detection
  - `Flask` for lightweight audit dashboard and APIs
- **Readable codebase for judges**: clear Python modules made architecture easier to evaluate live.
- **Cross-platform practicality**: Python allowed us to unify Windows/Linux flows with modest branching.

**Why not C (for this phase):**

- Higher implementation complexity and slower iteration under hackathon time constraints.
- Security mistakes in memory management can overshadow core architecture quality.
- Judge scoring emphasized design robustness, defense layering, and demonstrability over raw runtime speed.

**Why not Java (for this phase):**

- Heavier project scaffolding and deployment overhead for a compact SDK demo.
- Less direct leverage of our chosen ML and scripting workflows for rapid local testing.

### 1.2 Why SDK Architecture (not wrapper, not standalone tool)

We selected an **embeddable SDK** because product teams need protection inside their own runtime, not just as an external checker.

**SDK benefits:**

- **3-line integration path** for host apps
- Language/runtime agnostic deployment model at system level (any app can call into protected flow)
- Reusable primitives (license verification, audit, heartbeat, policy) across multiple products
- Better long-term maintainability than one-off wrapper scripts

**Why not a wrapper-only model:**

- Wrappers are easier to bypass and usually fragile across product updates.
- Harder to integrate deep runtime checks and telemetry-like signals.

**Why not a standalone command-only tool:**

- Strong for ops, weak for in-process security orchestration and developer UX.
- Would force host products into awkward process choreography for every validation step.

### 1.3 Why Offline-First Design

CertiGuard targets B2B on-premise environments where internet access is constrained or prohibited.

**Offline-first was a requirement, not a preference:**

- Air-gapped systems are common in regulated sectors and critical infrastructure.
- Runtime enforcement cannot depend on cloud calls to remain available.
- Security guarantees must survive network outages and disconnected deployments.

**Design implication:** every layer (crypto, binding, DNA, heartbeat, anomaly scoring, and audit integrity) runs locally and deterministically.

---

## 2. Technology Stack

| Component | Technology | Reason | Alternative Considered |
|---|---|---|---|
| Ed25519 signing | `cryptography` Ed25519 | Production-tested, modern elliptic-curve signatures, robust verification semantics | RSA (rejected: larger keys/signatures, slower operations, unnecessary legacy complexity for this use case) |
| AI detection | scikit-learn IsolationForest | Works without labeled fraud data, lightweight for offline anomaly scoring | Supervised ML (rejected: no high-quality labeled fraud dataset for training in hackathon scope) |
| Dashboard/API | Flask | Lightweight, fast setup, easy local hosting for demo and audit visualization | Django (rejected: overkill for MVP dashboard and increased setup overhead) |
| Hardware reading | `platform` + `subprocess` + OS probes | Practical cross-platform collection path with graceful fallbacks | WMI-only (rejected: Windows-only and non-portable) |
| Audit log integrity | Custom hash chain (`prev_hash`/`entry_hash`) | Minimal dependency surface, tamper-evident by design, easy to verify offline | SQLite (rejected: excellent storage engine but not inherently tamper-evident against file edits/replacements without extra controls) |

---

## 3. Architecture Decisions (ADRs — Architecture Decision Records)

### ADR-001: Ed25519 over RSA
**Status:** Accepted  
**Context:** We need to sign license files that will be verified offline.  
**Decision:** Use Ed25519 (Curve25519/EdDSA) signatures.  
**Rationale:** Smaller key/signature sizes than classic RSA, strong modern security margin, deterministic behavior that avoids nonce-misuse classes seen in other signature families, and broad production credibility (TLS ecosystems, SSH, Signal-adjacent crypto practices).  
**Consequences:** Adds crypto dependency management, but with a mature, audited implementation path.

### ADR-002: Separate Verifier Process over In-Binary VM
**Status:** Accepted  
**Context:** Core verification logic should be harder to patch than a single direct in-process function call.  
**Decision:** Support a separate verifier process + IPC challenge-response flow where feasible; use safe fallback where platform limits apply.  
**Rationale:** Process separation increases attacker effort, enables tighter control points, and improves forensic observability around verification outcomes.  
**Consequences:** Extra orchestration complexity (startup, IPC, error handling), but significantly better practical hardening than a purely monolithic check.

### ADR-003: Offline-First AI over Real-Time Alerts
**Status:** Accepted  
**Context:** Target deployments are frequently air-gapped; cloud scoring cannot be mandatory.  
**Decision:** Run Isolation Forest anomaly detection locally and persist baseline/drift state on device.  
**Rationale:** Delivers behavioral risk detection even with zero connectivity and avoids dependency on cloud latency/availability.  
**Consequences:** Model quality depends on local feature design; no centralized model retraining loop in the MVP.

### ADR-004: Installation DNA over Mandatory TPM
**Status:** Accepted  
**Context:** TPM availability is inconsistent across customer hardware and environments.  
**Decision:** Make installation DNA + boot timeline checks the baseline control; keep TPM as optional premium reinforcement when available.  
**Rationale:** Ensures broad compatibility while preserving anti-clone value. Avoids excluding valid customers lacking TPM access or permissions.  
**Consequences:** Baseline assurance is software-rooted; highest assurance still benefits from stronger TPM attestation in future production phases.

### ADR-005: Hash-Chained Audit Log over Database
**Status:** Accepted  
**Context:** We need forensic evidence that remains meaningful in offline settings and can be verified independently.  
**Decision:** Use append-only JSON lines with hash chaining (`prev_hash` -> `entry_hash`).  
**Rationale:** Lightweight, transparent, and tamper-evident without running a DB service. Easy to export, inspect, and verify during incident review.  
**Consequences:** Strong detection of selective tampering, but not full prevention of total file deletion/replacement without additional external anchoring.

---

## 4. Testing Strategy

Our testing strategy combines unit tests, scenario attacks, and live integration demonstrations. The objective is not only correctness but also **attack visibility** for judges.

### 4.1 Unit Tests (what each test checks)

| Test Name | Layer Tested | Attack Simulated | Expected Result |
|---|---|---|---|
| `test_valid_license_accepted` | L1 | None | Returns payload dict |
| `test_tampered_max_users` | L1 | Edit `max_users` field | `LicenseVerificationError: SIGNATURE_INVALID` |
| `test_honeypot_premium_unlock` | L7 | Set `PREMIUM_UNLOCK=True` | `LicenseVerificationError: HONEYPOT_TRIGGERED` |
| `test_wrong_machine` | L2 | Different hardware FP | `check_hardware_binding` returns `False` |
| `test_expired_license` | L1 | `valid_until` in past | `LicenseVerificationError: LICENSE_EXPIRED` |
| `test_stale_heartbeat` | L6 | Old timestamp in heartbeat | `verify_heartbeat` returns `(False, STALE)` |
| `test_audit_chain_valid` | L10 | None | `verify_chain` returns `(True, "Chain valid")` |
| `test_audit_chain_tampered` | L10 | Modify entry content | `verify_chain` returns `(False, "HASH_INVALID")` |
| `test_normal_session_ai` | L8 | Normal 40-user session | `is_anomalous=False` |
| `test_fraud_session_ai` | L8 | 4500 users at 3am | `is_anomalous=True` |

**Note for reviewers:** naming in test narratives maps to presentation-layer labels. Some runtime internals use module/function names rather than these exact symbolic error strings.

### 4.2 Integration Test — The Demo App

The integration demo uses a simulated on-prem application (e.g., **SecureInvoice**) wired to CertiGuard in minimal lines:

```python
from certiguard.license_client import CertiGuardClient
client = CertiGuardClient(state_dir)
result = client.verify_runtime(...)
```

**Demo characteristics:**

- Runs in a loop and emits fake but structured operational metrics.
- Calls CertiGuard each cycle for license/runtime verification.
- Writes events to the tamper-evident audit chain.
- Dashboard displays event stream and security posture in near-real-time.

**Five live demo attacks and expected judge-visible outcome:**

1. **License tampering attack**  
   - Action: Edit signed payload (`max_users`, expiry, or entitlements).  
   - Judge sees: verification failure with signature error path; app access denied.

2. **Machine-clone attack**  
   - Action: Move license/state to another host profile (or mocked alternate fingerprint).  
   - Judge sees: hardware/DNA mismatch failure, no successful authorization.

3. **Honeypot activation attack**  
   - Action: Inject `PREMIUM_UNLOCK` or similar tripwire key into license body.  
   - Judge sees: immediate tripwire-triggered rejection event.

4. **Heartbeat staleness / Dead Man's Switch attack**  
   - Action: Pause verifier or replay stale heartbeat records.  
   - Judge sees: liveness check fails, watchdog path reports invalid/stale heartbeat.

5. **Behavioral fraud simulation**  
   - Action: Send extreme usage vector (e.g., abnormal users/time/rate).  
   - Judge sees: anomaly and/or drift event in audit/dashboard, optional policy enforcement reject.

### 4.3 What Cannot Be Tested Automatically

Some controls are difficult to validate safely in CI and are therefore tested manually or with controlled mocks:

- **Anti-debug checks:** can interfere with the test runner itself and produce unreliable CI behavior.
- **TPM binding:** requires physical TPM capabilities and platform permissions not guaranteed in ephemeral runners.
- **Hardware fingerprint realism in CI:** virtualized environments may not expose stable real-world hardware identifiers.

**Methodology response:** use deterministic mocks for unit confidence, plus manual validation scripts on representative hardware.

---

## 5. Security Validation

### 5.1 What We Proved Works

The following mechanisms were validated through code-level tests and end-to-end exercises:

- **Ed25519 signature verification path** rejects payload tampering.
- **Hash-chained audit integrity** detects mutation/reordering of historical events.
- **Proof-of-Work heartbeat chain** validates liveness and structural integrity.
- **Offline challenge-response workflow** links verification to current local state.
- **Anomaly detection pipeline** can separate normal and extreme synthetic sessions.

### 5.2 What We Validated Against

Behavioral feature design and attack narratives were informed by practical insider-threat and misuse patterns, including references to datasets such as the **CERT Insider Threat Dataset** for scenario realism.

The MVP does not claim benchmark-grade model calibration; instead, it demonstrates a defensible and extensible offline behavioral detection workflow.

### 5.3 Known Limitations

No client-side software protection is unbreakable on a fully controlled endpoint.

Residual risks include:

- Advanced reverse engineering with enough time/resources
- Full file deletion/replacement (beyond selective log tampering)
- Feature poisoning or weak feature engineering for anomaly detection
- Platform-dependent anti-debug evasion techniques

### 5.4 Production Hardening Roadmap

A production deployment would add:

- **HSM-backed key custody** for signing operations
- **Code-signing certificate pipeline** and secure release provenance
- Stronger verifier isolation and stricter policy attestation
- Remote anchoring / SIEM integration for audit snapshots where permitted
- Formal secure SDLC controls (SAST/DAST/dependency scanning/sign-off gates)

---

## 6. Deployment Guide (Demo)

The following flow is designed for a live hackathon demonstration:

1. Install dependencies:

```bash
pip install -e .
```

2. Issue a demo license:

```bash
python vendor_tools/issue_license.py --client "Demo Corp" --users 50 --days 30 --out demo.lic
```

3. Start dashboard:

```bash
python dashboard/server.py
```

Open `http://localhost:5001`.

4. Run protected demo application:

```bash
python demo_app.py
```

5. Execute layer attack showcase:

```bash
python tests/test_all_layers.py
```

Expected result: judges observe acceptance for valid flows and deterministic, explainable failures for tampering/fraud scenarios.

---

## Delivery and Governance Notes

- Development followed short iterative cycles: implement -> attack simulation -> fix -> document.
- Every layer includes a clear owner module and a testable contract.
- Documentation is treated as a first-class artifact to support reproducibility, judging clarity, and post-hackathon transition to production planning.

---

## Conclusion

CertiGuard SDK demonstrates a pragmatic security engineering methodology: prioritize layered controls, validate with adversarial tests, keep integration friction low, and operate fully offline for real B2B environments.

For hackathon goals, this methodology intentionally maximizes architectural clarity and demonstrable resilience while preserving a credible path to production hardening.
