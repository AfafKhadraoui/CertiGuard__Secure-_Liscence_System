"""
Layer 8 — Source-Level Obfuscation
---------------------------------
Confuses decompilers by injecting opaque predicates and dead code.
Now includes Agile.NET-style String Encryption.
"""

import random
import re

from certiguard.layers.honeypot import generate_honeypot_bait

def obfuscate_c_file(source: str, seed: int, intensity: int = 3) -> str:
    """
    Applies multiple layers of C source obfuscation including Honeypots.
    """
    rng = random.Random(seed)
    
    # Inject Honeypot Bait
    bait_code = generate_honeypot_bait(seed)
    source = bait_code + source

    # --- STRING ENCRYPTION HELPER ---
    def encrypt_string_literal(match):
        s = match.group(1)
        if len(s) < 2: return f'"{s}"'
        xor_key = rng.randint(1, 255)
        encrypted = [(ord(c) ^ xor_key) for c in s]
        hex_data = "".join([f"\\x{b:02x}" for b in encrypted])
        return f'certiguard_decrypt_str("{hex_data}", {len(s)}, {xor_key})'

    lines = source.splitlines()
    output_lines: list[str] = []

    # Inject the decryption helper at the very top
    output_lines.append("""
static char* certiguard_decrypt_str(char* data, int len, int key) {
    static char buf[1024];
    for(int i=0; i<len; i++) buf[i] = data[i] ^ key;
    buf[len] = '\\0';
    return buf;
}
""")

    for line in lines:
        stripped = line.strip()
        
        # SKIP INCLUDES AND MACROS
        if stripped.startswith("#"):
            output_lines.append(line)
            continue

        # 1. Apply String Encryption to this line
        processed_line = re.sub(r'"([^"]+)"', encrypt_string_literal, line)

        output_lines.append(processed_line)

        # 2. Inject Opaque Predicates (Complexity)
        if "{" in processed_line and rng.random() < (intensity * 0.1):
            var_name = f"_rt{rng.randint(10, 99)}"
            predicate = f"  volatile int {var_name} = {rng.randint(10, 100)};\n"
            predicate += f"  if (({var_name} * {var_name}) < 0) {{\n"
            predicate += "    /* dead block — opaque predicate guarantees this never runs */\n"
            predicate += "    for(int i=0; i<10; i++) { if(i > 100) return 0; }\n"
            predicate += "  }\n"
            output_lines.append(predicate)

    return "\n".join(output_lines)

def run_confuserex(project_path: str) -> bool:
    """Stub for .NET obfuscation."""
    return True
