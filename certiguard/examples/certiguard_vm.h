
#ifndef CERTIGUARD_VM_H
#define CERTIGUARD_VM_H

#include <stdio.h>

/* CertiGuard Dynamic VM ISA - Build Seed: 1777099455 */
#define VM_OP_LOAD  227
#define VM_OP_XOR   19
#define VM_OP_ADD   23
#define VM_OP_CMP   156
#define VM_OP_JMP   73
#define VM_OP_EXIT  112

static const unsigned char cg_bytecode[] = { 0x1a, 0x34, 0x13, 0x1f, 0xd1, 0x63, 0x9c, 0x7e, 0x70 };

static int certiguard_vm_execute(unsigned char input_val) {
    int reg0 = input_val;
    int pc = 0;
    int result = 0;

    while (pc < 9) {
        unsigned char op = cg_bytecode[pc++];
        
        /* Polmorphic Dispatcher */
        if (op == VM_OP_LOAD) {
            reg0 = cg_bytecode[pc++];
        } 
        else if (op == VM_OP_XOR) {
            reg0 ^= cg_bytecode[pc++];
        }
        else if (op == VM_OP_CMP) {
            unsigned char target = cg_bytecode[pc++];
            result = (reg0 == target);
        }
        else if (op == VM_OP_EXIT) {
            return result;
        }
        else {
            /* Dynamic Noise - skip noise operand */
            pc++; 
        }
    }
    return 0;
}

#endif
