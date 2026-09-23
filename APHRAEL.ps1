param(
    [Parameter(Position=0, Mandatory=$true)]
    [ValidateSet('ask','projects','work-status','work-recent')]
    [string]$Command,
    [Parameter(Position=1, ValueFromRemainingArguments=$true)]
    [string[]]$Arguments
)
$ErrorActionPreference = 'Stop'
$aphraelRecord = Join-Path $env:USERPROFILE '.aphrael\installation.json'
if (-not (Test-Path -LiteralPath $aphraelRecord)) {
    throw 'Aphrael is not installed. Run .\SETUP_APHRAEL.ps1 first.'
}
$aphraelInstallation = Get-Content -LiteralPath $aphraelRecord -Raw | ConvertFrom-Json
if (-not (Test-Path -LiteralPath $aphraelInstallation.python)) {
    throw 'Hermes Python is unavailable. Run .\SETUP_APHRAEL.ps1.'
}
$env:HERMES_HOME = $aphraelInstallation.root
$env:HERMES_KANBAN_HOME = Join-Path $aphraelInstallation.root 'aphrael-board'
$env:HERMES_KANBAN_BOARD = 'aphrael'
$env:PYTHONIOENCODING = 'utf-8'
Remove-Item Env:APHRAEL_POLICY_FILE -ErrorAction SilentlyContinue

& $aphraelInstallation.python (Join-Path $PSScriptRoot 'scripts\aphrael_front_door.py') $Command @Arguments
exit $LASTEXITCODE
