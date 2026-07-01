# CertiGuard SDK Packaging Script
# This script bundles the entire project into a clean, distributable SDK folder.

$outDir = "CertiGuard_Professional_SDK_v1.0"
if (Test-Path $outDir) { Remove-Item -Recurse -Force $outDir }
New-Item -ItemType Directory -Path $outDir

Write-Host "--- Packaging CertiGuard SDK ---" -ForegroundColor Cyan

# 1. Copy Source Code (Excluding node_modules for a clean SDK)
Write-Host "[1/4] Copying core engine..."
New-Item -ItemType Directory -Path "$outDir\src"
Copy-Item -Recurse "src\*" "$outDir\src" -Exclude "node_modules"

# 2. Copy Documentation
Write-Host "[2/4] Copying manuals and blueprints..."
New-Item -ItemType Directory -Path "$outDir\docs"
Copy-Item -Recurse "docs\*" "$outDir\docs"

# 3. Copy Examples & Build Tools
Write-Host "[3/4] Copying examples and demo apps..."
New-Item -ItemType Directory -Path "$outDir\examples"
Copy-Item "examples\demo_app.c" "$outDir\examples"
Copy-Item "examples\build_demo.ps1" "$outDir\examples"
Copy-Item "examples\violation_demo.py" "$outDir\examples"

# 4. Create Setup Script
Write-Host "[4/4] Creating setup guide..."
$readme = @"
# CertiGuard Professional SDK v1.0

## Getting Started
1. Install dependencies: `pip install -r src/requirements.txt`
2. Run the demo build: `powershell -File examples/build_demo.ps1`
3. Launch your Dashboard: `python -m certiguard.cli dashboard`

## Folder Structure
- /src: The Python Security Engine & CLI
- /docs: Architecture and Development Blueprints
- /examples: The C-Demo app and the VM-Virtualization demo
"@
$readme | Out-File -FilePath "$outDir\README.txt"

Write-Host ""
Write-Host "SUCCESS! Your SDK is ready in: $outDir" -ForegroundColor Green
