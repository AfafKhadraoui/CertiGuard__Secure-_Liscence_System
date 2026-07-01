"""
Layer 5 — Anti-Debugging (Cross-Platform)
----------------------------------------
Detects if the application is being actively debugged or analyzed.
Supports Windows (PEB/API) and Linux (ptrace/procfs).
"""

import platform
import time
import os

def check_timing_anomaly(threshold_ms: float = 200.0) -> bool:
    """
    Measures execution time of a small block. 
    Debuggers cause significant delays (milliseconds vs nanoseconds).
    """
    start = time.perf_counter()
    # Dummy workload
    for _ in range(100000):
        _ = 1 + 1
    end = time.perf_counter()
    
    elapsed_ms = (end - start) * 1000
    # On most modern CPUs, 100k adds take < 5ms. 
    # If it takes > 200ms, a human is likely stepping through it.
    return elapsed_ms > threshold_ms

def check_windows_debug() -> bool:
    """Windows-specific debugger detection."""
    try:
        import ctypes
        # 1. Standard API check
        if ctypes.windll.kernel32.IsDebuggerPresent():
            return True
        
        # 2. CheckRemoteDebuggerPresent
        is_remote = ctypes.c_bool(False)
        ctypes.windll.kernel32.CheckRemoteDebuggerPresent(
            ctypes.windll.kernel32.GetCurrentProcess(), 
            ctypes.byref(is_remote)
        )
        if is_remote.value:
            return True
    except:
        pass
    return False

def check_linux_debug() -> bool:
    """Linux-specific debugger detection via /proc/self/status."""
    try:
        # Check TracerPid in procfs
        # If TracerPid != 0, someone is debugging us.
        if os.path.exists("/proc/self/status"):
            with open("/proc/self/status", "r") as f:
                for line in f:
                    if line.startswith("TracerPid:"):
                        pid = int(line.split(":")[1].strip())
                        if pid != 0:
                            return True
    except:
        pass
    return False

def debugger_detected() -> bool:
    """Main entry point for Layer 5 detection."""
    system = platform.system()
    
    # OS-Specific Checks
    if system == "Windows":
        if check_windows_debug(): return True
    elif system == "Linux":
        if check_linux_debug(): return True
        
    # Universal Timing Check (Works on all platforms)
    if check_timing_anomaly():
        return True
        
    return False
