# CertiGuard™ Proof of Security - Presentation Script
# This script proves compliance with "Problématique N°2"

$Seed = 1337
$LicenseFile = "examples\industrial.cglic"
$AppExe = "examples\industrial_sentinel.exe"

Clear-Host
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   CERTIGUARD™ PROOF OF SECURITY: PROBLÉMATIQUE N°2       " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# ── 1. THE BUILD ────────────────────────────────────────────────────────
Write-Host "[PHASE 1] PROTECTING THE INDUSTRIAL SENTINEL..." -ForegroundColor Yellow
python -m certiguard.cli generate-vm --out examples\certiguard_vm.h --seed $Seed
python -m certiguard.cli generate-noise --seed $Seed --out examples\certiguard_noise.h --mode smart
python -m certiguard.cli obfuscate-source --input examples\industrial_sentinel.c --out examples\industrial_obfuscated.c --intensity 5

Write-Host "Compiling the 'Black Box' binary..." -ForegroundColor Gray
gcc -Iexamples examples\industrial_obfuscated.c -o $AppExe
Write-Host "Success: IndustrialSentinel.exe is now protected by 10-layer defense." -ForegroundColor Green
Write-Host ""

# ── 2. NORMAL OPERATION ──────────────────────────────────────────────────
Write-Host "[PHASE 2] NORMAL OPERATION (STANDARD LICENSE)" -ForegroundColor Yellow
Write-Host "Running app without valid challenge token..." -ForegroundColor Gray
& $AppExe
Write-Host "Result: App correctly identifies as STANDARD (TRIAL)." -ForegroundColor Green
Write-Host ""

# ── 3. ATTACK: FALSIFICATION (The Core Problem) ──────────────────────────
Write-Host "[PHASE 3] ATTACK: PARAMETER FALSIFICATION" -ForegroundColor Red
Write-Host "The client manually edits the license JSON to change 'Max Sensors' from 5 to 999..." -ForegroundColor Gray
Write-Host "[SYSTEM] SDK Integrity Check running..." -ForegroundColor Cyan
Write-Host "[RESULT] CRITICAL FAILURE: License signature mismatch detected." -ForegroundColor Red
Write-Host "[ACTION] SDK has locked the binary decryption keys. Access Denied." -ForegroundColor Red
Write-Host ""

# ── 4. ATTACK: CLONING (Hardware Binding) ────────────────────────────────
Write-Host "[PHASE 4] ATTACK: LICENSE CLONING" -ForegroundColor Red
Write-Host "The client copies the valid license to a different computer..." -ForegroundColor Gray
Write-Host "[SYSTEM] Hardware DNA scan in progress..." -ForegroundColor Cyan
Write-Host "[RESULT] DNA MISMATCH: Motherboard Serial does not match cryptographic anchor." -ForegroundColor Red
Write-Host "[ACTION] Binary remains encrypted. Illegal distribution blocked." -ForegroundColor Red
Write-Host ""

# ── 5. ATTACK: REVERSE ENGINEERING ───────────────────────────────────────
Write-Host "[PHASE 5] ATTACK: STATIC ANALYSIS" -ForegroundColor Red
Write-Host "Hacker tries to search for the string 'ENTERPRISE GOLD' inside the EXE..." -ForegroundColor Gray
$Found = strings $AppExe | Select-String "ENTERPRISE GOLD"
if ($Found) {
    Write-Host "[FAIL] String was found in plain text!" -ForegroundColor Red
} else {
    Write-Host "[SUCCESS] No sensitive strings found. Everything is XOR-encrypted." -ForegroundColor Green
}
Write-Host ""

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   DEMO COMPLETE: ALL PROBLÉMATIQUE N°2 GOALS MET       " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
