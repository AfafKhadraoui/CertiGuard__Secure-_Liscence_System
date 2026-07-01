from __future__ import annotations

import hashlib
import json
import platform
import re
import subprocess
from typing import Any


def _run_ps(command: str) -> str:
    try:
        return subprocess.check_output(
            ["powershell", "-NoProfile", "-Command", command],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except Exception:
        return ""


def _run_cmd(command: list[str]) -> str:
    try:
        return subprocess.check_output(command, stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return ""


def tpm_info() -> dict[str, Any]:
    system = platform.system()
    if system == "Windows":
        raw = _run_ps("Get-Tpm | ConvertTo-Json -Compress")
        if not raw:
            return {"available": False, "platform": "windows"}
        try:
            data = json.loads(raw)
        except Exception:
            return {"available": False, "platform": "windows"}
        if isinstance(data, list):
            data = data[0] if data else {}
        if not isinstance(data, dict):
            return {"available": False, "platform": "windows"}
        present = bool(data.get("TpmPresent", False))
        ready = bool(data.get("TpmReady", False))
        manufacturer = str(data.get("ManufacturerIdTxt", "unknown"))
        version = str(data.get("ManufacturerVersion", "unknown"))
        return {
            "available": bool(present and ready),
            "platform": "windows",
            "present": present,
            "ready": ready,
            "manufacturer": manufacturer,
            "version": version,
        }

    # Linux path (best effort): rely on tpm2-tools if installed.
    getcap = _run_cmd(["tpm2_getcap", "properties-fixed"])
    if not getcap:
        return {"available": False, "platform": "linux"}
    manufacturer = "unknown"
    fw = "unknown"
    for line in getcap.splitlines():
        if "VENDOR_STRING_1" in line or "VENDOR_STRING_2" in line:
            manufacturer = manufacturer + "|" + line.strip()
        if "FIRMWARE_VERSION_1" in line or "FIRMWARE_VERSION_2" in line:
            fw = fw + "|" + line.strip()
    return {
        "available": True,
        "platform": "linux",
        "manufacturer": manufacturer,
        "version": fw,
    }


def tpm_anchor() -> str | None:
    info = tpm_info()
    if not info.get("available"):
        return None
    material = f"{info.get('platform')}|{info.get('manufacturer')}|{info.get('version')}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()

