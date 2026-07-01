# Examples

| Path | Purpose |
|------|---------|
| [`cg_e2e_app/run_harness.py`](cg_e2e_app/run_harness.py) | End-to-end harness: keys, license, `verify_runtime`, L6 warm/stress, attack simulators, synthetic audit lines. |
| [`demo_host_app.py`](demo_host_app.py) | Small “host app” driver (`ping`, `warm`, `stress`) for demos. |

## CLI workflow (manual keys)

```bash
certiguard gen-keys --private-key keys/private.pem --public-key keys/public.pem
certiguard gen-request --state-dir runtime/clientA --out runtime/clientA/clientA.cgreq.json
certiguard issue-license --request runtime/clientA/clientA.cgreq.json --private-key keys/private.pem --out runtime/clientA/license.certiguard.json --issued-to ACME --max-users 50 --modules hr,invoicing --valid-days 365 --exe-hash deadbeef
certiguard verify --state-dir runtime/clientA --license runtime/clientA/license.certiguard.json --public-key keys/public.pem --heartbeat-key local-secret --features 30,9,3,42
certiguard renewal-export --state-dir runtime/clientA --out runtime/clientA/renewal_request.json
```

## Documentation

- Runbook and dashboard: [`../docs/HOW_TO_TEST.md`](../docs/HOW_TO_TEST.md), [`../docs/DEMO_TEST_METHODOLOGY.md`](../docs/DEMO_TEST_METHODOLOGY.md)
