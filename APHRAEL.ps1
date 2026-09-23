param(
    [Parameter(Position=0, Mandatory=$true)]
    [ValidateSet('ask','projects','activity','work-status','work-recent','work-pending','work-claim','work-complete')]
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

if ($Command -eq 'ask') {
    $dispatcherMutex = [System.Threading.Mutex]::new($false, 'Local\AphraelDispatcherStart')
    $hasDispatcherLock = $false
    try {
        $hasDispatcherLock = $dispatcherMutex.WaitOne(10000)
        if (-not $hasDispatcherLock) { throw 'Timed out checking the Aphrael task dispatcher.' }
        $aphraelGateway = Get-CimInstance Win32_Process | Where-Object {
            $_.ExecutablePath -eq $aphraelInstallation.python -and
            $_.CommandLine -like '*aphrael-dispatcher*gateway run*'
        }
        if (-not $aphraelGateway) {
            $aphraelLogDir = Join-Path $aphraelInstallation.root 'profiles\aphrael-dispatcher\logs'
            New-Item -ItemType Directory -Path $aphraelLogDir -Force | Out-Null
            Start-Process -FilePath $aphraelInstallation.python `
                -ArgumentList '-m hermes_cli.main -p aphrael-dispatcher gateway run' `
                -WindowStyle Hidden `
                -RedirectStandardOutput (Join-Path $aphraelLogDir 'launcher.out.log') `
                -RedirectStandardError (Join-Path $aphraelLogDir 'launcher.err.log') | Out-Null
        }
    } finally {
        if ($hasDispatcherLock) { $dispatcherMutex.ReleaseMutex() }
        $dispatcherMutex.Dispose()
    }
}

& $aphraelInstallation.python (Join-Path $PSScriptRoot 'scripts\aphrael_front_door.py') $Command @Arguments
exit $LASTEXITCODE
