param(
    [ValidateSet('Chat','Tui','Desktop','Check')][string]$Surface = 'Chat',
    [switch]$NoDispatcher,
    [string]$QueryFile = '',
    [string]$Resume = ''
)
$ErrorActionPreference = 'Stop'
$aphraelRecord = Join-Path $env:USERPROFILE '.aphrael\installation.json'
if (-not (Test-Path -LiteralPath $aphraelRecord)) { & (Join-Path $PSScriptRoot 'SETUP_APHRAEL.ps1') }
$aphraelInstallation = Get-Content -LiteralPath $aphraelRecord -Raw | ConvertFrom-Json
$aphraelPython = $aphraelInstallation.python
$aphraelRoot = $aphraelInstallation.root
if (-not (Test-Path -LiteralPath $aphraelPython)) { throw 'Hermes Python is unavailable. Run SETUP_APHRAEL.ps1.' }
$env:HERMES_HOME = $aphraelRoot
$env:HERMES_KANBAN_HOME = Join-Path $aphraelRoot 'aphrael-board'
$env:HERMES_KANBAN_BOARD = 'aphrael'
$env:PYTHONIOENCODING = 'utf-8'
Remove-Item Env:APHRAEL_POLICY_FILE -ErrorAction SilentlyContinue
& $aphraelPython (Join-Path $PSScriptRoot 'scripts\aphrael_profile.py') check --root $aphraelRoot --source $PSScriptRoot
if ($LASTEXITCODE -ne 0) { throw 'Aphrael startup refused because required configuration is not healthy.' }
if ($Surface -eq 'Check') { return }
Set-Location -LiteralPath $aphraelInstallation.workspace
if (-not $NoDispatcher) {
    $aphraelGatewayArgs = '-m hermes_cli.main -p aphrael-dispatcher gateway run'
    $aphraelLogDir = Join-Path $aphraelRoot 'profiles\aphrael-dispatcher\logs'
    New-Item -ItemType Directory -Path $aphraelLogDir -Force | Out-Null
    $aphraelGateway = Get-CimInstance Win32_Process | Where-Object { $_.ExecutablePath -eq $aphraelPython -and $_.CommandLine -like '*aphrael-dispatcher*gateway run*' }
    if (-not $aphraelGateway) {
        Start-Process -FilePath $aphraelPython -ArgumentList $aphraelGatewayArgs -WindowStyle Hidden -RedirectStandardOutput (Join-Path $aphraelLogDir 'launcher.out.log') -RedirectStandardError (Join-Path $aphraelLogDir 'launcher.err.log') | Out-Null
    }
}
$aphraelArgs = @('-m','hermes_cli.main','-p','aphrael')
switch ($Surface) {
    'Tui' { $aphraelArgs += '--tui' }
    'Desktop' { $aphraelArgs += @('desktop','--cwd',$aphraelInstallation.workspace) }
    default {
        $aphraelArgs += 'chat'
        if ($QueryFile) { $aphraelArgs += @('--query-file',$QueryFile,'-Q') }
        if ($Resume) { $aphraelArgs += @('--resume',$Resume) }
    }
}
& $aphraelPython @aphraelArgs
if ($LASTEXITCODE -ne 0) { throw "Aphrael stopped with exit $LASTEXITCODE. Review the error above." }
