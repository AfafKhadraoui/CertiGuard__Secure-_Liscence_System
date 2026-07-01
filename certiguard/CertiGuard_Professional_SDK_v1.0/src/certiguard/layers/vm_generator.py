"""
CertiGuard Virtual Machine (CG-VM) Generator
-------------------------------------------
This script generates a unique, polymorphic instruction set (ISA) 
for every build. It turns critical logic into 'Bytecode' that only 
the generated C-Interpreter can understand.
"""

import random
from pathlib import Path

# The 'Universal' Opcodes
OP_LOAD  = 0
OP_XOR   = 1
OP_ADD   = 2
OP_CMP   = 3
OP_JMP   = 4
OP_EXIT  = 5
OP_NOISE = 6

def generate_vm_layer(out_header: Path, seed: int = 42):
    rng = random.Random(seed)
    
    # 1. Generate a RANDOM mapping for this specific build
    # In this build, 0xAF might mean 'XOR', in the next it might mean 'JMP'
    all_bytes = list(range(0, 256))
    rng.shuffle(all_bytes)
    
    mapping = {
        "LOAD":  all_bytes[0],
        "XOR":   all_bytes[1],
        "ADD":   all_bytes[2],
        "CMP":   all_bytes[3],
        "JMP":   all_bytes[4],
        "EXIT":  all_bytes[5],
        "NOISE": all_bytes[6:15] # Multiple bytes for noise
    }

    # 2. Create the 'Secret Bytecode' for a license check
    # Let's say our logic is: (KeyChar XOR 0x1F) == (0x61 XOR 0x1F)
    # 0x61 is 'a' (the first char of our valid key)
    xor_key = 0x1F
    target_val = ord('a') ^ xor_key 
    
    bytecode = [
        mapping["XOR"],  xor_key,       # XOR input with our secret key
        mapping["CMP"],  target_val,    # Compare with pre-computed target
        mapping["EXIT"]                 # Return result
    ]
    
    # 3. Assemble instructions (keeping opcode + operand pairs together)
    instructions = [
        [mapping["XOR"], xor_key],
        [mapping["CMP"], target_val],
        [mapping["EXIT"]]
    ]
    
    # 4. Inject RANDOM NOISE between instructions
    final_bytecode = []
    for inst in instructions:
        # Occasionally insert noise BEFORE an instruction
        if rng.random() > 0.5:
            final_bytecode.append(rng.choice(mapping["NOISE"]))
            final_bytecode.append(rng.randint(0, 255))
        
        final_bytecode.extend(inst)

    # 4. Generate the C Header
    c_code = f"""
#ifndef CERTIGUARD_VM_H
#define CERTIGUARD_VM_H

#include <stdio.h>

/* CertiGuard Dynamic VM ISA - Build Seed: {seed} */
#define VM_OP_LOAD  {mapping['LOAD']}
#define VM_OP_XOR   {mapping['XOR']}
#define VM_OP_ADD   {mapping['ADD']}
#define VM_OP_CMP   {mapping['CMP']}
#define VM_OP_JMP   {mapping['JMP']}
#define VM_OP_EXIT  {mapping['EXIT']}

static const unsigned char cg_bytecode[] = {{ {', '.join(hex(x) for x in final_bytecode)} }};

static int certiguard_vm_execute(unsigned char input_val) {{
    int reg0 = input_val;
    int pc = 0;
    int result = 0;

    while (pc < {len(final_bytecode)}) {{
        unsigned char op = cg_bytecode[pc++];
        
        /* Polmorphic Dispatcher */
        if (op == VM_OP_LOAD) {{
            reg0 = cg_bytecode[pc++];
        }} 
        else if (op == VM_OP_XOR) {{
            reg0 ^= cg_bytecode[pc++];
        }}
        else if (op == VM_OP_CMP) {{
            unsigned char target = cg_bytecode[pc++];
            result = (reg0 == target);
        }}
        else if (op == VM_OP_EXIT) {{
            return result;
        }}
        else {{
            /* Dynamic Noise - skip noise operand */
            pc++; 
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
