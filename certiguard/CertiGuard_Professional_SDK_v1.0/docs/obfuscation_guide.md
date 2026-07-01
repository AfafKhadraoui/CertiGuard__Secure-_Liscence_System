# CertiGuard Obfuscation & Noise Guide

CertiGuard provides advanced dynamic noise generation to protect your binary against pattern-based reverse engineering.

## Noise Modes

### 1. Rule-Based (`--mode rule`)
Generates simple math and loop operations. Good for basic confusion but might be detectable by advanced static analysis scripts.

### 2. Smart (AI-Inspired) (`--mode smart`)
Generates code that looks like real validation logic, using bitwise operations, math functions, and fake "dispatch" calls. This is designed to confuse human reversers into thinking they've found the "real" license check.

### 3. Polymorphic (`--mode polymorphic`)
Generates code where variables (state, buffer, key, nonce) change roles in every block. This mimics the behavior of a Polymorphic VM, making it extremely difficult to track data flow across different versions of the software.

## Usage

Run the following command to generate a noise header for your C/C++ project:

```bash
certiguard generate-noise --mode smart --seed 1234 --out certiguard_noise.h
```

Then, include it in your main application and call it at random points:

```c
#include "certiguard_noise.h"

void some_function() {
    certiguard_dynamic_noise(); // Injected garbage logic
    // ... real code ...
}
```

## Integration with .NET (Confuser.CLI)

If you are protecting a **.NET application**, you should use CertiGuard for the licensing logic and then apply a secondary layer of obfuscation using [ConfuserEx](https://github.com/yck1509/ConfuserEx) or `Confuser.CLI`.

**Recommended Pipeline:**
1. Build your .NET app with CertiGuard SDK integration.
2. Run `certiguard generate-noise` to create dynamic resources if needed.
3. Use `Confuser.CLI` to obfuscate the final assembly.
4. Sign the final binary with CertiGuard's `create-manifest` tool.
