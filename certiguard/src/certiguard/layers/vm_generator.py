"""
CertiGuard Virtual Machine (CG-VM) Generator
-------------------------------------------
This script generates a unique, polymorphic instruction set (ISA) 
for every build. It turns critical logic into 'Bytecode' that only 
the generated C-Interpreter can understand.
"""

import random
from pathlib import Path

def generate_vm_layer(out_header: Path, seed: int = 42):
    rng = random.Random(seed)
    
    # 1. Generate a RANDOM mapping for this specific build
    all_bytes = list(range(0, 256))
    rng.shuffle(all_bytes)
    
    mapping = {
        "LOAD":  all_bytes[0],
        "XOR":   all_bytes[1],
        "CMP":   all_bytes[2],
        "EXIT":  all_bytes[3],
        "NOISE": all_bytes[4:15] 
    }

    # 2. Create the 'Secret Bytecode' logic
    xor_key = 0x1F
    target_val = ord('a') ^ xor_key 
    
    # 3. Assemble instructions (keeping opcode + operand pairs together)
    instructions = [
        [mapping["XOR"], xor_key],
        [mapping["CMP"], target_val],
        [mapping["EXIT"], 0x00] # Exit also has a dummy operand for alignment
    ]
    
    # 4. Inject RANDOM NOISE between instructions
    final_bytecode = []
    for inst in instructions:
        if rng.random() > 0.5:
            final_bytecode.append(rng.choice(mapping["NOISE"]))
            final_bytecode.append(rng.randint(0, 255))
        final_bytecode.extend(inst)

    # 5. Encrypt the final bytecode
    build_key = rng.randint(1000, 999999)
    def encrypt_bytecode(data, key):
        state = key
        res = []
        for b in data:
            res.append(b ^ (state & 0xFF))
            state = (state * 31 + 17)
        return res
    
    encrypted_bytecode = encrypt_bytecode(final_bytecode, build_key)

    # 6. Generate the C Header with Obfuscated Logic
    xor_mask = rng.randint(0x10, 0xFF)
    add_mask = rng.randint(0x01, 0x64)
    hex_bytes = ", ".join(hex(x) for x in encrypted_bytecode)
    
    c_code = f"""
#ifndef CERTIGUARD_VM_H
#define CERTIGUARD_VM_H

#include <stdio.h>
#include <stdint.h>

/* [MUTANT VM] Every build uses a different internal math logic */
#define VM_OP_LOAD  {mapping['LOAD']}
#define VM_OP_XOR   {mapping['XOR']}
#define VM_OP_CMP   {mapping['CMP']}
#define VM_OP_EXIT  {mapping['EXIT']}
#define VM_DECRYPT_KEY {build_key}
#define VM_OBFUSC_XOR {xor_mask}
#define VM_OBFUSC_ADD {add_mask}

static const uint8_t cg_bytecode[] = {{ {hex_bytes} }};

static inline uint8_t vm_decrypt_byte(uint8_t b, uint32_t *state) {{
    uint8_t decrypted = b ^ (*state & 0xFF);
    *state = (*state * 31 + 17);
    return decrypted;
}}

static int certiguard_vm_execute(unsigned char input_val) {{
    // Internal state is scrambled from the start
    int reg0 = (input_val ^ VM_OBFUSC_XOR) + VM_OBFUSC_ADD; 
    uint32_t state = VM_DECRYPT_KEY;
    int pc = 0;
    
    while (pc < sizeof(cg_bytecode)) {{
        uint8_t op = vm_decrypt_byte(cg_bytecode[pc++], &state);
        uint8_t arg = vm_decrypt_byte(cg_bytecode[pc++], &state);
        
        if (op == VM_OP_LOAD) {{
            reg0 = (arg ^ VM_OBFUSC_XOR) + VM_OBFUSC_ADD;
        }} else if (op == VM_OP_XOR) {{
            reg0 ^= arg;
        }} else if (op == VM_OP_CMP) {{
            if (reg0 == ((arg ^ VM_OBFUSC_XOR) + VM_OBFUSC_ADD)) return 1;
        }} else if (op == VM_OP_EXIT) {{
            return 0;
        }}
    }}
    return 0;
}}

#endif
"""
    out_header.write_text(c_code, encoding="utf-8")
    return mapping

if __name__ == "__main__":
    import sys
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 42
    generate_vm_layer(Path("certiguard_vm.h"), seed)
    print(f"[*] Unique VM Layer generated with seed: {seed}")
