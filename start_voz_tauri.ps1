param()

$ErrorActionPreference = 'Stop'
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$tauriAppDir = Join-Path $projectDir 'tauri-app'
$logPath = Join-Path $tauriAppDir 'tauri-launch.log'

function Resolve-TauriCliPath {
    $localTauri = Join-Path $tauriAppDir 'node_modules\.bin\tauri.cmd'
    if (Test-Path $localTauri) { return $localTauri }

    $cmd = Get-Command tauri -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }

    return $null
}

try {
    if (-not (Test-Path $tauriAppDir)) {
        throw "No se encontro tauri-app en: $tauriAppDir"
    }

    $tauriCliPath = Resolve-TauriCliPath
    if (-not $tauriCliPath) {
        throw 'No se encontro el CLI de Tauri. Ejecuta npm install dentro de tauri-app.'
    }

    $cargoBin = Join-Path $env:USERPROFILE '.cargo\bin'
    if (Test-Path (Join-Path $cargoBin 'cargo.exe')) {
        $env:PATH = "$cargoBin;$env:PATH"
    }

    Set-Location $tauriAppDir
    & "$tauriCliPath" dev
    exit $LASTEXITCODE
}
catch {
    $_.Exception.Message | Set-Content -Path $logPath -Encoding UTF8
    Write-Host "[ERROR] $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Presiona cualquier tecla para ver los detalles del log..."
    $null = [Console]::ReadKey()
    Start-Process -FilePath 'powershell.exe' -ArgumentList '-NoExit','-Command',"Get-Content -Path '$logPath'"
    exit 1
}
