param(
    [string]$HermesRoot = (Join-Path $env:USERPROFILE '.hermes'),
    [string]$Workspace = (Join-Path $env:USERPROFILE 'AphraelWorkspace'),
    [string]$Model = 'gpt-5.5'
)
$ErrorActionPreference = 'Stop'
$aphraelPin = '49c6d4a9e0dddc64d6333c5b1fcc9d911463a8fd'
$aphraelInstall = Join-Path $HermesRoot 'hermes-agent'
$aphraelPython = Join-Path $aphraelInstall 'venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $aphraelPython)) {
    $aphraelInstaller = Join-Path ([System.IO.Path]::GetTempPath()) 'aphrael-official-hermes-install.ps1'
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/NousResearch/hermes-agent/$aphraelPin/scripts/install.ps1" -OutFile $aphraelInstaller
    & $aphraelInstaller -Commit $aphraelPin -SkipSetup -SkipComputerUse -NonInteractive -HermesHome $HermesRoot -InstallDir $aphraelInstall
    if (-not (Test-Path -LiteralPath $aphraelPython)) { throw 'Official Hermes installation did not finish. See its error above; rerun setup after resolving it.' }
}
$aphraelVersion = & $aphraelPython -c 'from hermes_cli import __version__; print(__version__)'
if ($LASTEXITCODE -ne 0 -or $aphraelVersion.Trim() -ne '0.21.2') { throw 'This distribution is tested with Hermes 0.21.2. Use the documented official installer recovery before updating.' }
$env:HERMES_HOME = $HermesRoot
$env:HERMES_KANBAN_HOME = Join-Path $HermesRoot 'aphrael-board'
$env:HERMES_KANBAN_BOARD = 'aphrael'
$env:PYTHONIOENCODING = 'utf-8'
& $aphraelPython (Join-Path $PSScriptRoot 'scripts\aphrael_profile.py') install --root $HermesRoot --source $PSScriptRoot --workspace $Workspace --model $Model
if ($LASTEXITCODE -ne 0) { throw 'Aphrael profile setup failed. Existing user state was not deleted; see the error above.' }
Write-Host 'Aphrael profile setup complete. Run .\START_APHRAEL.ps1'
Write-Host 'Provider: OpenAI Codex through supported ChatGPT OAuth. No credentials are stored in this repository.'
