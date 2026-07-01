"""
CertiGuard Violation Demo
-------------------------
This application is designed to FAIL. It demonstrates how different 
attacks trigger the CertiGuard security layers.
"""

import time
import sys
from pathlib import Path

# Add src to path
_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from certiguard.layers.audit import append_event
from certiguard.layers.antidebug import debugger_detected

def run_violations():
    # Setup - Point to the SAME log the dashboard is watching
    log_path = Path("demo_runs/cg_e2e/client_state/audit.log")

    print("--- CertiGuard Security Violation Demo ---")

    # 1. Trigger Layer 5 (Anti-Debug)
    print("\n[Violation 1] Simulating Debugger Attachment...")
    if debugger_detected(): 
        print("!! ALARM: Debugger detected. Event logged to dashboard.")
    else:
        print("No real debugger found, but let's log a 'Simulated Debug' event.")
        append_event(log_path, "debug_detected", {"method": "manual_simulation"})

    # 2. Trigger Layer 7 (Honeypot / Tripwire)
    print("\n[Violation 2] Attempting to use a Blacklisted (Honeypot) License...")
    print("Using key: 'LEAKED_KEY_2026_X'")
    append_event(log_path, "license_reject", {"reason": "honeypot_tripwire", "key": "LEAKED_KEY_2026_X"})

    # 3. Trigger Layer 6 (Behavioral Anomaly)
    print("\n[Violation 3] Simulating High-Frequency Brute Force...")
    for i in range(10):
        append_event(log_path, "behavior_check", {"api_call_count": 1000 + (i*100)})
    
    print("\nDone! Check your dashboard at http://localhost:8080 to see the results.")

if __name__ == "__main__":
    run_violations()
