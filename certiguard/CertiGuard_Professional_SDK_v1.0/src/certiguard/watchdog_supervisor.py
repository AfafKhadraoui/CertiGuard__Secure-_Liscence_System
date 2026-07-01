from __future__ import annotations

import time
from pathlib import Path

from certiguard.layers.watchdog import verify_heartbeat_recent


def supervise_heartbeat_or_fail(
    heartbeat_path: Path,
    heartbeat_key: str,
    timeout_seconds: int = 60,
    poll_seconds: int = 5,
    max_checks: int | None = None,
) -> bool:
    checks = 0
    while True:
        if not verify_heartbeat_recent(heartbeat_path, heartbeat_key, timeout_seconds=timeout_seconds):
            return False
        checks += 1
        if max_checks is not None and checks >= max_checks:
            return True
        time.sleep(poll_seconds)

