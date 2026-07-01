"""
Layer 1b — Hardware Fingerprinting (Cross-Platform)
--------------------------------------------------
Collects unique, non-changing hardware identifiers for DNA binding.
Supports Windows, Linux, and macOS.
"""

import subprocess
import platform
import hashlib
import os

def get_machine_uuid() -> str:
    """Gets the unique hardware UUID of the motherboard/system."""
    system = platform.system()
    
    try:
        if system == "Windows":
            # Windows: WMI unique ID
            cmd = "wmic csproduct get uuid"
            return subprocess.check_output(cmd, shell=True).decode().splitlines()[1].strip()
            
        elif system == "Linux":
            # Linux: DMI Product UUID (Requires root for some, fallback to machine-id)
            if os.path.exists("/sys/class/dmi/id/product_uuid"):
                with open("/sys/class/dmi/id/product_uuid", "r") as f:
                    return f.read().strip()
            if os.path.exists("/etc/machine-id"):
                with open("/etc/machine-id", "r") as f:
                    return f.read().strip()
                    
        elif system == "Darwin": # macOS
            # macOS: IOPlatformUUID
            cmd = "ioreg -rd1 -c IOPlatformExpertDevice | grep IOPlatformUUID"
            out = subprocess.check_output(cmd, shell=True).decode()
            return out.split('=')[-1].replace('"', '').strip()
            
    except Exception:
        pass
        
    return "GENERIC-HARDWARE-ID"

def get_cpu_info() -> str:
    """Gets the CPU model and feature set as part of the DNA."""
    return platform.processor() or "UNKNOWN-CPU"

def generate_hardware_fingerprint() -> str:
    """
    Mixes multiple hardware IDs into a single SHA-256 fingerprint.
    This fingerprint is used as the 'Seed' for all encryption.
    """
    uuid = get_machine_uuid()
    cpu = get_cpu_info()
    node = platform.node() # Machine name
    
    raw_data = f"{uuid}-{cpu}-{node}"
    return hashlib.sha256(raw_data.encode("utf-8")).hexdigest()

if __name__ == "__main__":
    print(f"OS: {platform.system()}")
    print(f"Machine UUID: {get_machine_uuid()}")
    print(f"Final DNA Fingerprint: {generate_hardware_fingerprint()}")
