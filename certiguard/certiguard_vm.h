
#ifndef CERTIGUARD_VM_H
#define CERTIGUARD_VM_H

#include <stdio.h>
#include <stdint.h>

/* [MUTANT VM] Every build uses a different internal math logic */
#define VM_OP_LOAD  234
#define VM_OP_XOR   9
#define VM_OP_CMP   103
#define VM_OP_EXIT  60
#define VM_DECRYPT_KEY 64556
#define VM_OBFUSC_XOR 119
#define VM_OBFUSC_ADD 94

static const uint8_t cg_bytecode[] = { 0x1f, 0xbd, 0x45, 0x5a, 0xb, 0x5b, 0x89, 0x37, 0x90, 0xe5 };

static inline uint8_t vm_decrypt_byte(uint8_t b, uint32_t *state) {
    uint8_t decrypted = b ^ (*state & 0xFF);
    *state = (*state * 31 + 17);
    return decrypted;
}

static int certiguard_vm_execute(unsigned char input_val) {
    // Internal state is scrambled from the start
    int reg0 = (input_val ^ VM_OBFUSC_XOR) + VM_OBFUSC_ADD; 
    uint32_t state = VM_DECRYPT_KEY;
    int pc = 0;
    
    while (pc < sizeof(cg_bytecode)) {
        uint8_t op = vm_decrypt_byte(cg_bytecode[pc++], &state);
        uint8_t arg = vm_decrypt_byte(cg_bytecode[pc++], &state);
        
        if (op == VM_OP_LOAD) {
            reg0 = (arg ^ VM_OBFUSC_XOR) + VM_OBFUSC_ADD;
        } else if (op == VM_OP_XOR) {
            reg0 ^= arg;
        } else if (op == VM_OP_CMP) {
            if (reg0 == ((arg ^ VM_OBFUSC_XOR) + VM_OBFUSC_ADD)) return 1;
        } else if (op == VM_OP_EXIT) {
            return 0;
        }
    }
    return 0;
}

#endif
