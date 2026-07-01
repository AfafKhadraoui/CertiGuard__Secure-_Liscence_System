"""
Layer 5b — Anti-Virtualization (Anti-VM)
----------------------------------------
Detects if the application is running inside a Virtual Machine.
Checks for VMWare, VirtualBox, Hyper-V, and QEMU artifacts.
"""

import os
import subprocess
import platform

def is_virtual_machine() -> bool:
    # 1. Check for Virtual MAC Prefixes
    # 08:00:27 (VirtualBox), 00:05:69 (VMWare), 00:1C:42 (Parallels)
    try:
        if platform.system() == "Windows":
            out = subprocess.check_output("getmac /FO CSV /V", shell=True).decode()
            if any(x in out.upper() for x in ["VIRTUALBOX", "VMWARE", "HYPER-V"]):
                return True
    except:
        pass

    # 2. Check for System Drivers/Services
    vm_artifacts = [
        "C:\\windows\\System32\\Drivers\\VBoxMouse.sys",
        "C:\\windows\\System32\\Drivers\\vmmouse.sys",
        "C:\\windows\\System32\\Drivers\\vmhgfs.sys",
    ]
    for path in vm_artifacts:
        if os.path.exists(path):
            return True

    # 3. Check System Model via WMI
    try:
        if platform.system() == "Windows":
            out = subprocess.check_output("wmic computersystem get model", shell=True).decode()
            if any(x in out.upper() for x in ["VIRTUALBOX", "VMWARE", "VIRTUAL MACHINE"]):
                return True
    except:
        pass

    return False
