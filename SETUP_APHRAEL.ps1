$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$aphraelPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $aphraelPython)) {
    $aphraelBase = Get-Command python -ErrorAction SilentlyContinue
    if (-not $aphraelBase) { throw 'Install Python 3.12 or newer for Windows with PATH enabled, then rerun this script.' }
    & $aphraelBase.Source -c 'import sys; sys.exit(0 if sys.version_info >= (3,12) else 1)'
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.12 or newer is required. Install it with PATH enabled, then rerun this script.' }
    & $aphraelBase.Source -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Could not create the Python environment.' }
}
& $aphraelPython -m pip install -e '.[dev]'
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed. Check network access, then rerun SETUP_APHRAEL.ps1.' }
Write-Host 'Setup complete. Run .\START_APHRAEL.ps1'
