from __future__ import annotations

import hashlib
import platform
import subprocess
from pathlib import Path


VENDOR_SALT = "certiguard_2026_your_secret"

def _validate_component(name: str, value: str) -> str:
    invalid_values = {"unknown", "unknown-cpu", "unknown-board", "to be filled by o.e.m.", "none", "default string", ""}
    if value.lower() in invalid_values:
        raise RuntimeError(f"Cannot collect hardware info for {name} — run as administrator or unsupported hardware")
    return value
def _safe_command(command: list[str]) -> str:
    try:
        output = subprocess.check_output(command, stderr=subprocess.DEVNULL, text=True).strip()
        return output or "unknown"
    except Exception:
        return "unknown"


def cpu_id() -> str:
    val = "unknown-cpu"
    if platform.system() == "Windows":
        out = _safe_command(["wmic", "cpu", "get", "ProcessorId"])
        lines = [line.strip() for line in out.splitlines() if line.strip() and "ProcessorId" not in line]
        val = lines[0] if lines else platform.processor() or "unknown-cpu"
    else:
        cpuinfo = Path("/proc/cpuinfo")
        if cpuinfo.exists():
            for line in cpuinfo.read_text(encoding="utf-8", errors="ignore").splitlines():
                if line.lower().startswith("model name"):
                    val = line.split(":", 1)[1].strip()
                    break
        if val == "unknown-cpu":
            val = platform.processor() or "unknown-cpu"
    return _validate_component("CPU", val)


def board_serial() -> str:
    val = "unknown-board"
    if platform.system() == "Windows":
        out = _safe_command(["wmic", "baseboard", "get", "serialnumber"])
        lines = [line.strip() for line in out.splitlines() if line.strip() and "SerialNumber" not in line]
        val = lines[0] if lines else "unknown-board"
    else:
        serial_file = Path("/sys/class/dmi/id/board_serial")
        if serial_file.exists():
            val = serial_file.read_text(encoding="utf-8", errors="ignore").strip() or "unknown-board"
    return _validate_component("Motherboard", val)


def hardware_fingerprint() -> str:
    data = f"{cpu_id()}|{board_serial()}|{VENDOR_SALT}".encode("utf-8")
    return hashlib.sha256(data).hexdigest()

