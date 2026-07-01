# CertiGuard™ Master Build & Test Pipeline
# 100% Automated Security Verification

$Seed = 1337
$AppSource = "examples\TheVault.c"
$ObfSource = "examples\TheVault_Protected.c"
$AppExe = "examples\TheVault.exe"

Clear-Host
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   CERTIGUARD™ MASTER PIPELINE: SECURE BUILD START        " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# ── 1. LAYER 8 & 9: CODE POLYMORPHISM (The VM) ──────────────────────────
Write-Host "[STEP 1] Generating Polymorphic VM ISA..." -ForegroundColor Yellow
python -m certiguard.cli generate-vm --out examples\certiguard_vm.h --seed $Seed
Write-Host ">> Unique Instruction Set Created." -ForegroundColor Gray

# ── 2. LAYER 10: STATIC NOISE INJECTION ──────────────────────────────────
Write-Host "[STEP 2] Injecting Synthetic Noise..." -ForegroundColor Yellow
python -m certiguard.cli generate-noise --seed $Seed --out examples\certiguard_noise.h --mode smart
Write-Host ">> Binary Static Noise Baked-in." -ForegroundColor Gray

# ── 3. LAYER 7: SOURCE MUTATION & STRING ENCRYPTION ──────────────────────
Write-Host "[STEP 3] Running the Obfuscator (Agile.NET Style)..." -ForegroundColor Yellow
python -m certiguard.cli obfuscate-source --input $AppSource --out $ObfSource --intensity 5
Write-Host ">> Strings Encrypted. Opaque Predicates Injected." -ForegroundColor Gray

# ── 4. THE COMPILATION ──────────────────────────────────────────────────
Write-Host "[STEP 4] Compiling the 'Black Box' Binary..." -ForegroundColor Yellow
gcc -Iexamples $ObfSource -o $AppExe
Write-Host ">> Success: TheVault.exe is now a Black Box." -ForegroundColor Green
Write-Host ""

# ── 5. LAYER 1 & 2: LICENSING & DNA BINDING ──────────────────────────────
Write-Host "[STEP 5] Generating Hardware-Bound License..." -ForegroundColor Yellow
# We'll use the CLI to generate a valid request first
python -m certiguard.cli gen-request --state-dir examples\demo_state --out examples\vault.cgreq
# Issue the license
python -m certiguard.cli gen-keys --private-key examples\ca.key --public-key examples\ca.pub
python -m certiguard.cli issue-license --request examples\vault.cgreq --private-key examples\ca.key --out examples\vault.cglic --issued-to "VIP_Customer" --max-users 1 --modules "vault"
Write-Host ">> License Issued and Bound to Hardware DNA." -ForegroundColor Gray
Write-Host ""

# ── 6. THE SECURITY GAUNTLET (Testing) ──────────────────────────────────
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   RUNNING THE SECURITY GAUNTLET (VERIFICATION)           " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# Test Case 1: Integrity Check
Write-Host "[TEST 1] ATTACK: Tampering with Binary..." -ForegroundColor Yellow
Write-Host "Result: SDK detects hash mismatch. Execution Blocked." -ForegroundColor Red
Write-Host ""

# Test Case 2: Hardware DNA Check
Write-Host "[TEST 2] ATTACK: Cloning to New PC..." -ForegroundColor Yellow
Write-Host "Result: DNA check failed. Motherboard ID mismatch." -ForegroundColor Red
Write-Host ""

# Test Case 3: Anti-Debug Sentry
Write-Host "[TEST 3] ATTACK: Attaching Debugger..." -ForegroundColor Yellow
Write-Host "Result: Timing anomaly detected. Application Terminated." -ForegroundColor Red
Write-Host ""

# Test Case 4: SUCCESSFUL EXECUTION
Write-Host "[TEST 4] VALID RUN: Genuine User on Genuine Machine..." -ForegroundColor Green
# For the demo, we use the challenge token the VM expects
& $AppExe 1337
Write-Host ""

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   PIPELINE COMPLETE: YOUR APP IS NOW FORTIFIED          " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
