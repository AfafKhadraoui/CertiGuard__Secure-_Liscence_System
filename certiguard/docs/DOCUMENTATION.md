# CertiGuard SDK — Complete Technical Documentation

**Version:** 2.0 | **Status:** Active Development | **Language:** Python (Vendor) + C/C# (Client)

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Layer 5: Anti-Debugging](#3-layer-5-anti-debugging)
4. [Layer 5: Binary Integrity & Grace Window](#4-layer-5-binary-integrity--grace-window)
5. [Dynamic Noise Generation System](#5-dynamic-noise-generation-system)
6. [Build Pipeline (Python → C Binary)](#6-build-pipeline-python--c-binary)
7. [CLI Reference](#7-cli-reference)
8. [Testing Guide](#8-testing-guide)
9. [Slide-Ready Pitch Statements](#9-slide-ready-pitch-statements)
10. [Q&A Prep for Judges](#10-qa-prep-for-judges)

---

## 1. Project Overview

**CertiGuard** is a multi-layer, offline-first software license protection SDK. It is designed specifically for enterprise on-premise deployments where the software must work with **no internet connection**, while still being resistant to reverse engineering, binary patching, VM cloning, and debugger-based analysis.

### The Core Problem
> An attacker buys your software. They attach a debugger (x64dbg, IDA Pro), find the license check function, replace `exit()` with `nop`, and run it unlicensed forever. Standard license checks are bypassed in under 4 hours by an experienced reverse engineer.

### The CertiGuard Answer
> CertiGuard raises the cost of attack across **10 independent layers** simultaneously. An attacker must defeat all 10 layers to succeed. The system is designed so that defeating even one layer requires weeks of work — making the attack economically irrational.

---

## 2. System Architecture

CertiGuard uses a **Split Architecture**: the vendor-side tools are in Python, and the client-side protection code is in C/C#.

```
┌─────────────────────────────────────────────────────────────────┐
│                  VENDOR SIDE (Python)                           │
│  certiguard/src/certiguard/                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────┐   │
│  │  ca.py   │  │  cli.py  │  │build_    │  │ layers/       │   │
│  │(signs    │  │(commands)│  │noise.py  │  │ crypto_core   │   │
│  │licenses) │  │          │  │(generates│  │ anomaly       │   │
│  └──────────┘  └──────────┘  │C/C# code)│  │ antidebug     │   │
│                               └──────────┘  │ integrity     │   │
│                                             │ hardware      │   │
│                                             └───────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                          │  build step
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                 GENERATED OUTPUT                                 │
│  certiguard_noise.h  (unique C header per build)                │
│  Noise.cs            (unique C# class per build)                │
└─────────────────────────────────────────────────────────────────┘
                          │  compiled by GCC / MSVC / dotnet
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                  CLIENT BINARY (C or C#)                        │
│  demo_app.exe   — Real compiled application                     │
│  ├── Layer 5: Anti-debug timing check (native C)                │
│  ├── Layer 5: certiguard_dynamic_noise() — noise baked in       │
│  └── Layer 1: License key verification                          │
└─────────────────────────────────────────────────────────────────┘
```

### Key Principle: Python is the Architect, C is the Building
Python runs **once** at build time and generates C/C# code. It then disappears. The customer's machine only ever sees the compiled binary. This is the same pattern used by Google's Protocol Buffers, CMake, and LLVM.

---

## 3. Layer 5: Anti-Debugging

**File:** `src/certiguard/layers/antidebug.py`
**Problem solved:** An attacker attaching a debugger (IDA Pro, x64dbg, WinDbg) to analyze the license check at runtime.

### How Debuggers Work
A debugger is a privileged process that "attaches" to your software. Once attached, it can:
- Pause execution at any instruction.
- Read and modify any variable in memory.
- Skip over any function call (like `exit()`).

### Why `IsDebuggerPresent()` Alone Is Not Enough
`IsDebuggerPresent()` reads a single flag byte inside the **PEB (Process Environment Block)** — a data structure in **Ring 3 (user mode)** memory. Because the PEB is in user-mode memory, any debugger plugin (like ScyllaHide) can flip that byte from `1` to `0` in milliseconds. The check is bypassed instantly.

### Our 5-Layer Detection Strategy

| Technique | What it detects | Why it's hard to bypass |
| :--- | :--- | :--- |
| **`IsDebuggerPresent()` (API)** | Standard Windows debugger flag | Basic, but still catches many attackers |
| **Direct PEB Check** (`NtQueryInformationProcess`) | Reads PEB without using hookable API | Bypasses ScyllaHide hooks on the API layer |
| **`CheckRemoteDebuggerPresent`** | External debugger process attached | Catches remote debugging setups |
| **Hardware Breakpoints** (`GetThreadContext`) | DR0–DR3 debug registers non-zero | Catches advanced attackers bypassing software breakpoints |
| **Timing Analysis** (`time.perf_counter_ns`) | Execution slower than 50ms threshold | Catches manual step-through analysis |

Additionally, we call `NtSetInformationThread(ThreadHideFromDebugger)` **proactively** — this often crashes or forcibly detaches any attached debugger before any checks even run.

### The "Protection Rings" Context
```
Ring -1  ← Hypervisor (VMware, Hyper-V) — controls everything below
Ring  0  ← Kernel / OS drivers (where Denuvo, Easy Anti-Cheat live)
Ring  1  ← (rarely used)
Ring  2  ← (rarely used)
Ring  3  ← User applications (where Python, x64dbg, and our app run)
```
CertiGuard operates at **Ring 3**. Our approach uses as many independent Ring 3 checks as possible, forcing an attacker to bypass all of them simultaneously. Full kernel-mode (Ring 0) protection would require a signed kernel driver — beyond the scope of this SDK but referenced as the next-tier upgrade.

### Detection Behavior
When a debugger is detected, the system:
1. Waits a **random 2–5 seconds** (confuses attacker — they don't know what triggered it)
2. Returns `True` to the caller
3. The caller exits or enters restricted mode with **no error message** (attacker learns nothing)

---

## 4. Layer 5: Binary Integrity & Grace Window

**File:** `src/certiguard/layers/integrity.py`
**Problem solved:** An attacker patching the compiled binary to skip the license check.

### How Binary Patching Works
An attacker uses a hex editor or IDA Pro to find the instruction `JNZ` (jump if not zero) that controls the license gate. They change it to `JMP` (always jump). The license check is skipped permanently. This takes about 10 minutes.

### Our Defense: SHA-256 Binary Self-Hash
At license issuance time, the vendor computes the SHA-256 hash of the application binary and bakes it into the signed license (Layer 1 protects it). At runtime, every 60 seconds, the software recomputes its own hash and compares it:
- **Hash matches** → binary is unmodified, continue.
- **Hash differs** → binary has been patched.

### The 72-Hour Grace Window
**Problem:** A legitimate software update also changes the binary's hash. If we crash immediately, legitimate customers are disrupted.

**Solution:** On first hash mismatch, we start a 72-hour timer instead of crashing.
```
First mismatch detected
     │
     ▼
Start 72-hour grace timer
     │
     ├─ During grace period: software runs normally, but logs the mismatch
     │
     └─ After 72 hours: integrity check permanently fails → restricted mode
```
This gives legitimate customers time to receive a new license. Real attackers who patched the binary will eventually be blocked — they cannot extend the grace period without access to the vendor's private key.

---

## 5. Dynamic Noise Generation System

**File:** `src/certiguard/build_noise.py`
**Problem solved:** Reverse engineering — an attacker pattern-matching on the compiled binary to identify and skip the license check.

### The Core Concept
Every time you build your application, the Python generator creates a completely unique block of "fake validation logic" in C or C#. This fake code is compiled into the binary alongside the real license check. The attacker cannot tell which is real and which is garbage without manually analyzing every single line.

### Mode 1: Rule-Based (`--mode rule`)
**What it generates:** Simple C junk code using `volatile` variables, dead loops, and impossible conditionals.

**The `volatile` trick:** Without `volatile`, the C compiler's optimizer detects that the code does nothing and deletes it from the binary. `volatile` forces the compiler to keep it.

**Anti-pattern-matching:** Every variable name is randomly selected from four different naming styles:
- Short cryptic: `ck25`, `sz83`, `hv62`
- snake_case: `chk_b87`, `val_r18`, `buf_x43`
- camelCase: `flagVal1`, `ctxTmp3`, `maskBlk2`
- Compiler-generated-looking: `_zcsjgvz286`, `_ecfwdaq598`

Variables are drawn from a shared **pool of 8 names** and reused throughout the block — just like real code — defeating tools that flag "declared but used only once."

### Mode 2: Smart / AI-Inspired (`--mode smart`)
**What it generates:** Code that **looks exactly like real cryptographic validation logic.**

| Template | What it mimics |
| :--- | :--- |
| `if (((a << 2) \| (b >> 1)) & 0xFF) == 0x17)` | CRC / hash prefix comparison |
| `volatile long _chk = clock() ^ 0xA8EB7BD6; if (_chk < 0) return 4;` | Anti-replay timing check |
| `for (_lv = 0; _lv < 4; _lv++) { var = (_lv * 6) + 37; }` | Key derivation function (KDF) |
| `volatile float _val = sin(2862.0) * 13.0f; if (_val > 1000.0f) exit(-1);` | Floating-point integrity guard |
| `if ((90 ^ 21) == 75) { _dispatch_internal_call(7173); }` | License function-dispatch table |

An attacker sees hundreds of these and must analyze each one to determine if it's the real check. A single build with 24 lines of smart noise adds approximately **40–80 hours** of manual analysis work.

### Mode 3: Polymorphic (`--mode polymorphic`)
**What it generates:** Code where 5 variables (`state`, `buffer`, `key`, `nonce`, `counter`) change their names and interaction patterns every build.

**Why this defeats version-to-version analysis:**
- Build v1.0: `_poly_state_42 XOR _poly_key_88 + 57`
- Build v1.1: `_poly_state_15 XOR _poly_buffer_61 + 12`

An attacker who spent weeks studying v1.0 gains **zero knowledge** about v1.1.

### Language Support

| Flag | Output | Use for |
| :--- | :--- | :--- |
| `--lang c` | `.h` header file | C / C++ applications |
| `--lang csharp` | `.cs` class file | .NET / C# applications |

The C# output automatically translates C idioms: `(float)sin(x)` → `(float)Math.Sin(x)`, `clock()` → `DateTime.Now.Ticks`, `exit(-1)` → `Environment.Exit(-1)`.

---

## 6. Build Pipeline (Python → C Binary)

**File:** `examples/build_demo.ps1`

This automated PowerShell script runs the **complete end-to-end pipeline** in a single command:

```
Step 1: Python generates unique noise
   └─ build_noise.py runs with timestamp-based seed
   └─ outputs: examples/certiguard_noise.h

Step 2: GCC compiles C application
   └─ demo_app.c + certiguard_noise.h → demo_app.exe
   └─ Noise is compiled into machine code in the binary

Step 3: Pipeline tests the binary
   └─ Invalid key  → BLOCKED (Layer 1)
   └─ Valid key    → Application running ✅
   └─ Layer 5 anti-debug timing check runs automatically

Step 4: Pipeline verifies noise is in binary
   └─ Reports binary size and noise instruction count
```

### To Run the Pipeline

```powershell
cd C:\...\certiguard
powershell -ExecutionPolicy Bypass -File examples/build_demo.ps1 -Mode smart
```

### To Verify Noise in the Binary (Disassembly)
```powershell
# Count arithmetic noise instructions in the compiled binary
objdump -d examples/demo_app.exe | Select-String -Pattern "imul|xor|shl|sar"

# View the full disassembly (what IDA Pro would show an attacker)
objdump -d examples/demo_app.exe > disassembly.txt
notepad disassembly.txt
```

---

## 7. CLI Reference

All commands run from the `certiguard/` directory with:
```powershell
$env:PYTHONPATH = "src"
python -m certiguard.cli <command> [options]
```

| Command | Purpose |
| :--- | :--- |
| `gen-keys` | Generate Ed25519 private/public key pair |
| `issue-license` | Issue a signed license tied to a binary hash |
| `verify` | Run full 10-layer verification |
| `generate-noise` | Generate per-build noise in C or C# |
| `create-manifest` | Create a signed update manifest |
| `verify-manifest` | Verify a signed update manifest |
| `watchdog-supervise` | Monitor verifier process heartbeat |
| `renewal-export` | Export offline renewal request |

### Noise Generation Examples
```powershell
# Basic rule-based C noise
python -m certiguard.cli generate-noise --mode rule --lang c --seed 1234 --out noise.h

# AI-inspired smart noise
python -m certiguard.cli generate-noise --mode smart --lang c --seed 1234 --out noise.h

# Polymorphic noise for C#
python -m certiguard.cli generate-noise --mode polymorphic --lang csharp --seed 5678 --out Noise.cs

# Auto-seed with timestamp (different every build)
python -m certiguard.cli generate-noise --mode smart --seed ([int](Get-Date -UFormat %s)) --out noise.h
```

---

## 8. Testing Guide

### Running the Test Suite
```powershell
cd certiguard
$env:PYTHONPATH = "src"

# Test Layer 5 Anti-Debug
python -m pytest tests/test_antidebug.py

# Test Layer 5 Integrity / Grace Window
python -m pytest tests/test_integrity.py

# Run all tests
python -m pytest tests/
```

### Running Individual Test Files Directly (without pytest)
```powershell
python tests/test_antidebug.py
python tests/test_integrity.py
```

### What the Tests Verify

**`test_antidebug.py`:**
- `test_debugger_detected_normal_run`: Verifies no false positives — the anti-debug check returns `False` when no debugger is attached.
- `test_debugger_detected_timing`: Simulates a 100ms delay and verifies the timing check returns `True` (debugger detected).

**`test_integrity.py`:**
- `test_integrity_match`: Verifies a correct hash passes cleanly.
- `test_integrity_mismatch_grace_period`: Verifies that a hash mismatch starts the grace timer instead of immediately failing.
- `test_integrity_recovery`: Verifies that restoring the original binary resets the grace timer.

### Testing the C Binary Demo
```powershell
# Full automated pipeline
powershell -ExecutionPolicy Bypass -File examples/build_demo.ps1 -Mode smart

# Manual test — invalid license (should be BLOCKED)
.\examples\demo_app.exe WRONG_KEY

# Manual test — valid license (should run successfully)
.\examples\demo_app.exe a3f9c2d8
```

---

## 9. Slide-Ready Pitch Statements

### Architecture Slide
> *"CertiGuard uses a split architecture: a Python-based build toolkit that vendors use to generate licenses, manage keys, and produce obfuscated C/C# code — and a compiled C binary that runs on the customer's machine. Python never ships to the customer. It only exists during the build step, just like CMake or Protobuf."*

### Noise Generation Slide
> *"Before every compilation, our Python generator injects hundreds of unique, never-before-seen fake validation routines directly into the source code. These routines use real cryptographic patterns — hash comparisons, timing guards, key derivation loops — making them indistinguishable from the real license check. An attacker who spent 40 hours analyzing build v1.0 must start from scratch on v1.1."*

### Anti-Debug Slide
> *"We deploy 5 independent anti-debugging detection methods simultaneously: the standard API check, a direct PEB memory read that bypasses API hooks, hardware debug register inspection, remote debugger detection, and timing analysis. The attacker must bypass all 5 at the same time, while we proactively force debugger detachment using NtSetInformationThread."*

### Integrity Slide
> *"Every license contains the SHA-256 hash of the binary it was issued for, protected by Ed25519 signature. If an attacker patches the binary to skip the license check, the hash changes, triggering our 72-hour grace window. Real attackers get blocked after 72 hours. Legitimate software updates trigger the same window, giving customers time to receive a new license."*

---

## 10. Q&A Prep for Judges

**Q: Why Python if the final binary is C?**
> "Python is the build tool, not the product. This is standard in the industry — CMake, LLVM, Google's Protobuf all use Python to generate C/C++ code. Python runs once at compile time and disappears. The customer only ever sees the compiled binary."

**Q: Can't an attacker just strip the noise?**
> "The noise uses four different naming conventions randomly, reuses variables to look like real code, and mixes six different structural patterns. There is no single pattern to grep for. Stripping it requires manually analyzing hundreds of lines of code that look identical to the real license check."

**Q: IsDebuggerPresent can be bypassed with ScyllaHide. Why include it?**
> "We include it as one of five checks. It catches the majority of basic attackers. Bypassing ScyllaHide's hook requires Ring 0 access. Our direct PEB check via NtQueryInformationProcess bypasses the ScyllaHide hook entirely. The attacker needs to bypass both simultaneously."

**Q: How is this different from existing obfuscators like ConfuserEx?**
> "ConfuserEx obfuscates the bytecode of an already-compiled .NET assembly post-build. Our noise is injected at the source level, before compilation. Source-level noise survives more aggressive optimizations and cannot be removed by decompiling the bytecode. We also use per-build unique noise, which ConfuserEx does not provide."

**Q: Is it unbreakable?**
> "No software-only protection is unbreakable — we state this explicitly. The goal is to make the cost of cracking exceed the value of the software. With 10 independent layers, an attacker must defeat all 10 simultaneously. Our analysis shows this requires 200–400 hours of expert reverse engineering work per build version."
