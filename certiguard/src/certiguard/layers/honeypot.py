"""
Layer 7 — Forensic Honeypots (Bait & Trap)
------------------------------------------
Injects "Bait" data and "Tripwire" functions into the binary to catch
attackers performing static and dynamic analysis.
"""

import random

def generate_honeypot_bait(seed: int) -> str:
    """
    Generates a set of 'bait' C code that looks like sensitive secrets.
    """
    rng = random.Random(seed)
    
    baits = [
        "const char* MASTER_KEY_BACKDOOR = \"0xDEADC0DE\";",
        "const char* DEBUG_OVERRIDE_PWD = \"root1234\";",
        "const char* ADMIN_BYPASS_TOKEN = \"SG9uZXlwb3RfVHJhcA==\";",
        "int IS_DEBUG_MODE_GLOBAL = 0;",
    ]
    
    # Selecting 2 random baits to keep the binary unique
    selected = rng.sample(baits, 2)
    
    c_code = "\n// --- Forensic Honeypot Baits ---\n"
    for b in selected:
        c_code += b + "\n"
        
    # Tripwire function: Looks like a bypass, but is actually a trap
    c_code += """
void check_secret_bypass_path(const char* input) {
    // If an attacker calls this function via a jump or injection,
    // they are flagged as a malicious actor.
    if (input != NULL && strlen(input) > 10) {
        // Trigger silent forensic lockdown
        certiguard_dynamic_noise(); // Junk work to waste time
    }
}
"""
    return c_code
