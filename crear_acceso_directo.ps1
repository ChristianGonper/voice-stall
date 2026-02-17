# Wrapper de compatibilidad: delega al script mantenido actualmente.
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$v2Script = Join-Path $scriptDir "crear_acceso_directo_v2.ps1"

if (-not (Test-Path $v2Script)) {
    Write-Host "[ERROR] No se encontro crear_acceso_directo_v2.ps1 en: $scriptDir" -ForegroundColor Red
    pause
    exit 1
}

& powershell -ExecutionPolicy Bypass -File $v2Script
exit $LASTEXITCODE
