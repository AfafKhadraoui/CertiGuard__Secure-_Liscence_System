from __future__ import annotations
import json
import os
import platform
from pathlib import Path

import requests


def _default_machine_id() -> str:
    return (
        os.environ.get("COMPUTERNAME")
        or os.environ.get("HOSTNAME")
        or platform.node()
        or "unknown"
    )


class SyncManager:
    """
    Handles the 'Offline-to-Online' synchronization of audit logs.
    It tracks which logs have already been sent and attempts to push new ones 
    whenever a connection to the dashboard collector is available.
    """
    def __init__(self, state_dir: Path, collector_url: str = "http://localhost:8080"):
        self.state_dir = state_dir
        self.collector_url = collector_url
        self.sync_meta_path = state_dir / "sync_meta.json"
        
    def _get_last_synced_line(self) -> int:
        if not self.sync_meta_path.exists():
            return 0
        try:
            data = json.loads(self.sync_meta_path.read_text(encoding="utf-8"))
            return data.get("last_line", 0)
        except Exception:
            return 0
            
    def _save_last_synced_line(self, line_num: int):
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.sync_meta_path.write_text(json.dumps({"last_line": line_num}), encoding="utf-8")

    def sync_now(self, audit_log_path: Path) -> bool:
        """
        Attempts to sync logs to the central dashboard.
        Returns True if sync was successful, False otherwise.
        """
        if not audit_log_path.exists():
            return False
            
        try:
            # 1. Read current logs
            lines = audit_log_path.read_text(encoding="utf-8").splitlines()
            last_line = self._get_last_synced_line()
            
            if last_line >= len(lines):
                return True # Nothing new to sync
                
            new_lines = lines[last_line:]
            logs_to_send = [json.loads(l) for l in new_lines]
            
            # 2. Attempt to push to dashboard
            # Note: The /api/logs/ingest endpoint would be on a remote server 
            # or the local dashboard server.
            response = requests.post(
                f"{self.collector_url.rstrip('/')}/api/logs/ingest",
                json={
                    "machine_id": _default_machine_id(),
                    "logs": logs_to_send,
                },
                timeout=10,
            )
            
            if response.status_code == 403:
                rdata = response.json()
                if rdata.get("action") == "REVOKE_IMMEDIATE":
                    print("\n[!!!] SECURITY ALERT: This installation has been REMOTELY REVOKED.")
                    print("[!!!] Deleting local security tokens and locking application...")
                    for f in ["dna.json", "counter.json", "policy.json"]:
                        p = self.state_dir / f
                        if p.exists(): p.unlink()
                    import sys
                    sys.exit(66) # Exit with unique security code

            if response.status_code == 200:
                self._save_last_synced_line(len(lines))
                return True
                
        except Exception:
            # Silent fail - likely offline
            pass
            
        return False
