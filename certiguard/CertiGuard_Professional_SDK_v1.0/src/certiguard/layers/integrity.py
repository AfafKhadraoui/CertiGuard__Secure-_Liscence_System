from __future__ import annotations

import hashlib
import time
from pathlib import Path

# Grace period is 72 hours (in seconds)
GRACE_PERIOD_SECONDS = 72 * 60 * 60

# We keep track of when the hash mismatch first occurred
_mismatch_start_time: float | None = None

def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()

def check_integrity(executable_path: Path, expected_hash: str) -> bool:
    """
    Checks the binary integrity.
    Returns False if the integrity check fails AND the 72-hour grace window has expired.
    Returns True otherwise.
    """
    global _mismatch_start_time
    
    current_hash = file_sha256(executable_path)
    
    if current_hash != expected_hash:
        if _mismatch_start_time is None:
            # First time mismatch detected, start the 72-hour grace window timer
            _mismatch_start_time = time.time()
            # In a real system, you would log this to the audit log (Layer 10)
            print(f"[WARNING] Integrity check failed. 72-hour grace window started.")
            return True
        else:
            time_elapsed = time.time() - _mismatch_start_time
            if time_elapsed > GRACE_PERIOD_SECONDS:
                # Grace window expired
                print("[ERROR] 72-hour grace window expired. Integrity check failed.")
                return False
            else:
                # Still within grace window
                hours_left = (GRACE_PERIOD_SECONDS - time_elapsed) / 3600
                print(f"[WARNING] Integrity mismatch. Grace window active. {hours_left:.2f} hours remaining.")
                return True
    else:
        # Hash matches, reset any existing timer
        _mismatch_start_time = None
        return True

