"""
L6 machine-side behavior probe (CPU / memory / process landscape / GPU hints).

What this is
------------
The Isolation Forest in ``anomaly.py`` scores a **numeric feature vector**. By default
integrators pass **application-level** metrics (users online, API rate, etc.). This
module optionally supplies a **second mode**: features derived from **this host** using
``psutil`` and light OS queries — useful for demos and for catching **obviously alien**
environments (e.g. nearly idle sandboxes, tiny process sets, or GPU profile mismatches)
once a customer baseline has been learned.

What it is not
--------------
This is **not** a hypervisor or cloud attestation product. GPU "detection" is a **best-effort
heuristic** (adapter names / PCI class strings). Names can be spoofed by a determined
attacker; the value is **raising cost** and **feeding consistent telemetry** into L6
alongside your own app metrics when you choose ``use_machine_behavior_probe``.
"""

from __future__ import annotations

import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import psutil

# Discrete-class GPU heuristics (vendor marketing names in WMI / lspci output).
_DISCRETE_GPU = re.compile(
    r"nvidia|geforce|rtx|gtx|quadro|tesla|amd|radeon|rx |rx5|rx6|arc a|arc b|intel arc|"
    r"firepro|instinct|adreno",
    re.I,
)
_BASIC_RENDER = re.compile(r"microsoft basic render|standard vga|virtualbox|vmware|qemu|cirrus|hyper-v video", re.I)


def _creationflags_no_window() -> int:
    return int(getattr(subprocess, "CREATE_NO_WINDOW", 0))


def _video_adapter_names() -> list[str]:
    names: list[str] = []
    if sys.platform == "win32":
        try:
            proc = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-NoLogo",
                    "-Command",
                    "Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name",
                ],
                capture_output=True,
                text=True,
                timeout=12,
                creationflags=_creationflags_no_window(),
            )
            if proc.returncode == 0 and proc.stdout.strip():
                names = [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]
        except Exception:
            pass
    elif sys.platform.startswith("linux"):
        try:
            proc = subprocess.run(
                ["lspci"],
                capture_output=True,
                text=True,
                timeout=8,
            )
            if proc.returncode == 0:
                for ln in proc.stdout.splitlines():
                    low = ln.lower()
                    if any(k in low for k in ("vga", "3d controller", "display")):
                        names.append(ln.strip())
        except Exception:
            if Path("/sys/class/drm").exists():
                for p in Path("/sys/class/drm").glob("card[0-9]"):
                    if p.is_dir():
                        names.append(p.name)
    elif sys.platform == "darwin":
        try:
            proc = subprocess.run(
                ["system_profiler", "SPDisplaysDataType"],
                capture_output=True,
                text=True,
                timeout=20,
            )
            if proc.returncode == 0:
                for ln in proc.stdout.splitlines():
                    if "Chipset Model:" in ln or "Resolution:" in ln:
                        names.append(ln.strip())
        except Exception:
            pass
    return names


def _nvidia_smi_gpu_count() -> int:
    try:
        proc = subprocess.run(
            ["nvidia-smi", "-L"],
            capture_output=True,
            text=True,
            timeout=4,
            creationflags=_creationflags_no_window(),
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            return 0
        return sum(1 for ln in proc.stdout.splitlines() if ln.strip().lower().startswith("gpu "))
    except Exception:
        return 0


def probe_host_behavior() -> dict[str, Any]:
    """
    Collect a snapshot of host telemetry and human-readable explanations.

    Returns a dict suitable for JSON audit attachments (excluding huge strings).
    """
    cpu_logical = int(psutil.cpu_count(logical=True) or 1)
    # Short sample so the reading is meaningful for “current load” demos.
    cpu_pct = float(psutil.cpu_percent(interval=0.2))
    vm = psutil.virtual_memory()
    mem_pct = float(vm.percent)
    swap_pct = float(psutil.swap_memory().percent)
    try:
        proc_count = len(psutil.pids())
    except Exception:
        proc_count = 0

    adapters = _video_adapter_names()
    nvidia_ct = _nvidia_smi_gpu_count()
    discrete_like = sum(1 for n in adapters if _DISCRETE_GPU.search(n) and not _BASIC_RENDER.search(n))
    basic_like = sum(1 for n in adapters if _BASIC_RENDER.search(n))

    hour = datetime.now().astimezone().hour
    notes: list[str] = [
        f"CPU load ~{cpu_pct:.1f}% over {cpu_logical} logical processors.",
        f"RAM usage ~{mem_pct:.1f}%, swap ~{swap_pct:.1f}%.",
        f"Observed ~{proc_count} processes (high-level sandbox / VM hints are weak signals only).",
    ]
    if adapters:
        notes.append(f"Display adapters reported ({len(adapters)}): {adapters[:4]!r}…")
    else:
        notes.append("No display adapter names collected (OS permissions or headless host).")
    if nvidia_ct:
        notes.append(f"nvidia-smi reports {nvidia_ct} GPU line(s).")
    notes.append(
        f"Heuristic discrete-class adapters ≈ {discrete_like}, basic/virtual-class ≈ {basic_like}."
    )

    return {
        "cpu_percent": round(cpu_pct, 2),
        "cpu_logical": cpu_logical,
        "mem_percent": round(mem_pct, 2),
        "swap_percent": round(swap_pct, 2),
        "process_count": proc_count,
        "display_adapter_count": len(adapters),
        "gpu_discrete_class_hint": int(discrete_like),
        "gpu_basic_virtual_hint": int(basic_like),
        "nvidia_smi_gpu_lines": nvidia_ct,
        "hour_local": hour,
        "explanation": " ".join(notes),
    }


def probe_to_feature_vector(probe: dict[str, Any] | None = None) -> list[float]:
    """
    Map ``probe_host_behavior()`` into a fixed **6-D** float vector for ``BehaviorDetector``.

    Components (rough scales so they sit near the synthetic training ranges):

    0. CPU utilization 0–100
    1. Logical CPU count (capped)
    2. Resident memory pressure 0–100
    3. Process count scaled down (typical desktops hundreds+)
    4. GPU signal: discrete hints + nvidia-smi lines, capped
    5. Local hour 0–23 (drift / “impossible session” style signals when blended with app data)
    """
    p = probe or probe_host_behavior()
    cores = min(float(p.get("cpu_logical", 1)), 128.0)
    procs = min(float(p.get("process_count", 0)) / 5.0, 200.0)
    gpu_signal = min(
        float(p.get("gpu_discrete_class_hint", 0)) * 12.0
        + float(p.get("nvidia_smi_gpu_lines", 0)) * 18.0
        + float(p.get("display_adapter_count", 0)) * 2.0,
        120.0,
    )
    return [
        float(p.get("cpu_percent", 0.0)),
        cores,
        float(p.get("mem_percent", 0.0)),
        procs,
        gpu_signal,
        float(p.get("hour_local", 0)),
    ]
