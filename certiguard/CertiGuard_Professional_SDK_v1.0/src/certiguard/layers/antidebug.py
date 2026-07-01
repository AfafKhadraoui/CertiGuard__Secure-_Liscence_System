from __future__ import annotations

import ctypes
import ctypes.wintypes
import platform
import random
import sys
import time
from pathlib import Path

import psutil

DEBUGGER_NAMES = {"x64dbg", "ida", "ida64", "windbg", "gdb", "ghidra"}

# --- Windows specific structs and constants ---
if platform.system() == "Windows":
    kernel32 = ctypes.windll.kernel32
    ntdll = ctypes.windll.ntdll

    ThreadHideFromDebugger = 17
    CONTEXT_DEBUG_REGISTERS = 0x00010010

    class CONTEXT(ctypes.Structure):
        _pack_ = 16
        _fields_ = [
            ("P1Home", ctypes.c_ulonglong),
            ("P2Home", ctypes.c_ulonglong),
            ("P3Home", ctypes.c_ulonglong),
            ("P4Home", ctypes.c_ulonglong),
            ("P5Home", ctypes.c_ulonglong),
            ("P6Home", ctypes.c_ulonglong),
            ("ContextFlags", ctypes.wintypes.DWORD),
            ("MxCsr", ctypes.wintypes.DWORD),
            ("SegCs", ctypes.wintypes.WORD),
            ("SegDs", ctypes.wintypes.WORD),
            ("SegEs", ctypes.wintypes.WORD),
            ("SegFs", ctypes.wintypes.WORD),
            ("SegGs", ctypes.wintypes.WORD),
            ("SegSs", ctypes.wintypes.WORD),
            ("EFlags", ctypes.wintypes.DWORD),
            ("Dr0", ctypes.c_ulonglong),
            ("Dr1", ctypes.c_ulonglong),
            ("Dr2", ctypes.c_ulonglong),
            ("Dr3", ctypes.c_ulonglong),
            ("Dr6", ctypes.c_ulonglong),
            ("Dr7", ctypes.c_ulonglong),
            # Other fields omitted for brevity as we only need debug registers
        ]

def _windows_is_debugger_present() -> bool:
    try:
        return bool(kernel32.IsDebuggerPresent())
    except Exception:
        return False

def _windows_check_remote_debugger() -> bool:
    try:
        is_debugger_present = ctypes.wintypes.BOOL()
        kernel32.CheckRemoteDebuggerPresent(kernel32.GetCurrentProcess(), ctypes.byref(is_debugger_present))
        return bool(is_debugger_present.value)
    except Exception:
        return False

def _windows_peb_being_debugged() -> bool:
    try:
        # In Python, accessing the PEB directly via TEB without writing C code or shellcode is tricky.
        # We can try to use NtQueryInformationProcess
        ProcessBasicInformation = 0
        class PROCESS_BASIC_INFORMATION(ctypes.Structure):
            _fields_ = [
                ("ExitStatus", ctypes.c_void_p),
                ("PebBaseAddress", ctypes.POINTER(ctypes.c_byte)),
                ("AffinityMask", ctypes.c_void_p),
                ("BasePriority", ctypes.c_void_p),
                ("UniqueProcessId", ctypes.c_void_p),
                ("InheritedFromUniqueProcessId", ctypes.c_void_p)
            ]
        
        pbi = PROCESS_BASIC_INFORMATION()
        return_length = ctypes.wintypes.ULONG()
        status = ntdll.NtQueryInformationProcess(
            kernel32.GetCurrentProcess(),
            ProcessBasicInformation,
            ctypes.byref(pbi),
            ctypes.sizeof(pbi),
            ctypes.byref(return_length)
        )
        
        if status == 0 and pbi.PebBaseAddress:
            # The BeingDebugged flag is at offset 2 in the PEB on both x86 and x64
            being_debugged = pbi.PebBaseAddress[2]
            return being_debugged != 0
            
    except Exception:
        pass
    return False

def _windows_hardware_breakpoints() -> bool:
    try:
        context = CONTEXT()
        context.ContextFlags = CONTEXT_DEBUG_REGISTERS
        thread_handle = kernel32.GetCurrentThread()
        
        # GetThreadContext might fail if not called properly, but we attempt it
        if kernel32.GetThreadContext(thread_handle, ctypes.byref(context)):
            if context.Dr0 != 0 or context.Dr1 != 0 or context.Dr2 != 0 or context.Dr3 != 0:
                return True
    except Exception:
        pass
    return False

def _windows_hide_thread():
    try:
        # Attempts to detach debugger by hiding the thread
        ntdll.NtSetInformationThread(
            kernel32.GetCurrentThread(),
            ThreadHideFromDebugger,
            0,
            0
        )
    except Exception:
        pass

def _timing_analysis() -> bool:
    # A very simple timing check. If a debugger is stepping, time between instructions is huge.
    start = time.perf_counter_ns()
    
    # Do some dummy work
    x = 0
    for _ in range(10000):
        x += 1
        
    end = time.perf_counter_ns()
    
    # If the simple loop took more than 50ms (50,000,000 ns), it's highly suspicious
    # (Usually it takes < 1ms)
    return (end - start) > 50_000_000

def _linux_tracerpid() -> bool:
    status = Path("/proc/self/status")
    if not status.exists():
        return False
    for line in status.read_text(encoding="utf-8").splitlines():
        if line.startswith("TracerPid:"):
            return int(line.split(":")[1].strip()) != 0
    return False

def _sys_trace() -> bool:
    return sys.gettrace() is not None

def _debug_processes_running() -> bool:
    for proc in psutil.process_iter(attrs=["name"]):
        name = (proc.info.get("name") or "").lower()
        if any(dbg in name for dbg in DEBUGGER_NAMES):
            return True
    return False

def debugger_detected() -> bool:
    # Run generic checks
    checks = [_sys_trace(), _debug_processes_running(), _timing_analysis()]
    
    if platform.system() == "Windows":
        _windows_hide_thread() # Proactive defense
        checks.extend([
            _windows_is_debugger_present(),
            _windows_check_remote_debugger(),
            _windows_peb_being_debugged(),
            _windows_hardware_breakpoints()
        ])
    else:
        checks.append(_linux_tracerpid())
        
    # Evaluate all checks
    if any(checks):
        time.sleep(random.uniform(2.0, 5.0))
        return True
        
    return False

