param()

$ErrorActionPreference = 'Stop'
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$tauriAppDir = Join-Path $projectDir 'tauri-app'
$logPath = Join-Path $tauriAppDir 'tauri-launch.log'

function Resolve-NpmPath {
    $cmd = Get-Command npm -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }

    $fallbacks = @(
        (Join-Path $env:ProgramFiles 'nodejs\npm.cmd'),
        (Join-Path $env:APPDATA 'npm\npm.cmd')
    )
    foreach ($f in $fallbacks) {
        if (Test-Path $f) { return $f }
    }
    return $null
}

try {
    if (-not (Test-Path $tauriAppDir)) {
        throw "No se encontro tauri-app en: $tauriAppDir"
    }

    $npmPath = Resolve-NpmPath
    if (-not $npmPath) {
        throw 'npm no esta disponible. Instala Node.js y aseguralo en PATH.'
    }

    $cargoBin = Join-Path $env:USERPROFILE '.cargo\bin'
    if (Test-Path (Join-Path $cargoBin 'cargo.exe')) {
        $env:PATH = "$cargoBin;$env:PATH"
    }

    Set-Location $tauriAppDir
    & $npmPath run tauri -- dev
    exit $LASTEXITCODE
}
catch {
    $_.Exception.Message | Set-Content -Path $logPath -Encoding UTF8
    Start-Process -FilePath 'powershell.exe' -ArgumentList '-NoExit','-Command',"Get-Content -Path '$logPath'"
    exit 1
}
