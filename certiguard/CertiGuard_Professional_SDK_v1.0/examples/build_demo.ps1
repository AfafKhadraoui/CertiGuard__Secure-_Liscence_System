# CertiGuard — Automated Build & Demo Script
# This script runs the FULL pipeline:
#   Step 1: Generate unique noise (Python)
#   Step 2: Compile demo app with noise (GCC)
#   Step 3: Test the binary with valid and invalid licenses
#   Step 4: Show the noise is actually in the binary

param(
    [string]$Mode = "smart",
    [int]$Seed = 0
)

$ErrorActionPreference = "Stop"

# Set working directory to certiguard root
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  CertiGuard Build Pipeline" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# ── Step 1: Generate a unique seed from timestamp if not provided ──────────
if ($Seed -eq 0) {
    $Seed = [int](Get-Date -UFormat %s)
}
Write-Host ""
Write-Host "[Step 1] Generating noise (Mode: $Mode, Seed: $Seed)..." -ForegroundColor Yellow
$env:PYTHONPATH = "src"
python -m certiguard.cli generate-noise `
    --mode $Mode `
    --lang c `
    --seed $Seed `
    --out examples/certiguard_noise.h

Write-Host "         Noise header written to: examples/certiguard_noise.h" -ForegroundColor Green

# ── Step 1c: Generate the Virtual Machine (VM) Layer ──────────────────────
Write-Host ""
Write-Host "[Step 1c] Generating Polymorphic VM Layer (ISA)..." -ForegroundColor Yellow
python -m certiguard.cli generate-vm `
    --out examples\certiguard_vm.h `
    --seed $Seed

Write-Host "         VM Header generated: examples/certiguard_vm.h" -ForegroundColor Green

# ── Step 1b: Obfuscate the C source (Agile.NET-style) ─────────────────────
Write-Host ""
Write-Host "[Step 1b] Applying source-level obfuscation to demo_app.c..." -ForegroundColor Yellow
python -m certiguard.cli obfuscate-source `
    --input examples\demo_app.c `
    --out examples\demo_app_obfuscated.c `
    --seed $Seed `
    --intensity 3

if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] Obfuscation step failed, using original source." -ForegroundColor Yellow
    Copy-Item examples\demo_app.c examples\demo_app_obfuscated.c
}
Write-Host "         Obfuscated source written to: examples/demo_app_obfuscated.c" -ForegroundColor Green

# ── Step 2: Compile obfuscated application ────────────────────────────────
Write-Host ""
Write-Host "[Step 2] Compiling demo_app_obfuscated.c with GCC..." -ForegroundColor Yellow
gcc `
    -O2 `
    -I examples `
    -o examples\demo_app.exe `
    examples\demo_app_obfuscated.c `
    -lm

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] GCC compilation failed. See errors above." -ForegroundColor Red
    exit 1
}
Write-Host "         Binary compiled: examples\demo_app.exe" -ForegroundColor Green

# ── Step 3: Test the binary ────────────────────────────────────────────────
Write-Host ""
Write-Host "[Step 3] Testing binary with INVALID license..." -ForegroundColor Yellow
Write-Host "---"
& .\examples\demo_app.exe "WRONG_KEY_HERE"
Write-Host "---"

Write-Host ""
Write-Host "[Step 3] Testing binary with VALID license..." -ForegroundColor Yellow
Write-Host "---"
& .\examples\demo_app.exe "a3f9c2d8"
Write-Host "---"

# ── Step 4: Prove the noise is in the binary ──────────────────────────────
Write-Host ""
Write-Host "[Step 4] Proving noise is baked into the binary..." -ForegroundColor Yellow
Write-Host "         Searching for noise variable names inside demo_app.exe..."
# The compiled binary will contain string representations of variable names
# that exist in the compiled code's symbol/debug info or visible as data
$binaryContent = [System.IO.File]::ReadAllBytes("examples/demo_app.exe")
$binaryString = [System.Text.Encoding]::ASCII.GetString($binaryContent)
$found = ($binaryString -match "certiguard_dynamic_noise")
if ($found) {
    Write-Host "         CONFIRMED: 'certiguard_dynamic_noise' found inside the binary!" -ForegroundColor Green
} else {
    Write-Host "         NOTE: Symbol not visible in ASCII scan (optimized away or stripped)." -ForegroundColor Yellow
    Write-Host "         Use: objdump -d examples/demo_app.exe | grep -A5 'certiguard'" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[Step 4] Binary size breakdown:" -ForegroundColor Yellow
$size = (Get-Item "examples/demo_app.exe").Length
Write-Host "         demo_app.exe: $size bytes" -ForegroundColor Green

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Build pipeline complete!" -ForegroundColor Cyan
Write-Host "  To verify noise in binary: " -ForegroundColor Cyan
Write-Host "  objdump -d examples/demo_app.exe" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
