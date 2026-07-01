"""L5 PoW heartbeat chain (migrated from repo-root test_pow.py)."""

from __future__ import annotations

from pathlib import Path

import pytest

from certiguard.layers.watchdog import verify_heartbeat_recent, write_heartbeat


def test_pow_heartbeat_chain(tmp_path: Path) -> None:
    path = tmp_path / "pow_heartbeat.json"
    write_heartbeat(path, "ignored_key")
    write_heartbeat(path, "ignored_key")
    assert verify_heartbeat_recent(path, "ignored_key", timeout_seconds=60)
