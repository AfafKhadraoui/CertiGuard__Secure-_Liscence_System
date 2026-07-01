#!/usr/bin/env python3
"""
Optional manual smoke: starts the Flask dashboard (opens browser).
Requires built UI: npm run build in src/certiguard/ui.

Usage (from certiguard repo root):
  python scripts/smoke_dashboard.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from certiguard.dashboard import review_audit_logs  # noqa: E402


def main() -> None:
    log = _ROOT / "demo_runs" / "smoke_audit.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    if not log.exists():
        log.write_text("", encoding="utf-8")
    review_audit_logs(audit_log_path=str(log), port=int(os.environ.get("PORT", "8080")))


if __name__ == "__main__":
    main()
