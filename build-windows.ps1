$ErrorActionPreference = "Stop"

$python = "python"
$venvPython = ".\.venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    & $python -m venv .venv
}

& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt pyinstaller
& $venvPython -m PyInstaller --clean --noconfirm MCSRAutoPredictions.spec

$artifact = "dist\MCSRAutoPredictions.exe"
if (Test-Path $artifact) {
    Get-FileHash $artifact -Algorithm SHA256
    Write-Host "Built $artifact"
} else {
    throw "Expected build artifact was not created: $artifact"
}
