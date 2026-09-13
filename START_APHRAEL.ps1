param([int]$Port = 0)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$aphraelPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $aphraelPython)) { & (Join-Path $PSScriptRoot 'SETUP_APHRAEL.ps1') }
& $aphraelPython -c 'import aphrael, fastapi, uvicorn, psutil' 2>$null
if ($LASTEXITCODE -ne 0) { & (Join-Path $PSScriptRoot 'SETUP_APHRAEL.ps1') }
if ($Port -gt 0) { & $aphraelPython -m aphrael --port $Port } else { & $aphraelPython -m aphrael }
if ($LASTEXITCODE -ne 0) { throw 'Aphrael stopped with an error. Check the message above (including port or data-directory conflicts).' }
