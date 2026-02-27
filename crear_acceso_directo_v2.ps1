# Crea/repara accesos directos y apunta el principal a Tauri.
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$tauriTargetScript = Join-Path $projectDir "start_voz_tauri_silent.vbs"
$qtTargetScript = Join-Path $projectDir "start_voz_qt_silent.vbs"

if (-not (Test-Path $tauriTargetScript)) {
    Write-Host "[ERROR] No se encontro start_voz_tauri_silent.vbs en: $projectDir" -ForegroundColor Red
    pause
    exit 1
}

if (-not (Test-Path $qtTargetScript)) {
    Write-Host "[WARN] No se encontro start_voz_qt_silent.vbs en: $projectDir" -ForegroundColor Yellow
    Write-Host "Se creara solo el acceso directo de Tauri." -ForegroundColor Yellow
}

$desktop = [Environment]::GetFolderPath("Desktop")
$iconPath = Join-Path $projectDir "voice_stall_icon.ico"
$wsh = New-Object -ComObject WScript.Shell

$shortcuts = @(
    @{
        Name = "Voice Stall v2.lnk"
        Script = $tauriTargetScript
        Description = "Voice Stall v2 - Tauri"
    }
)

if (Test-Path $qtTargetScript) {
    $shortcuts += @{
        Name = "Voice Stall Qt (fallback).lnk"
        Script = $qtTargetScript
        Description = "Voice Stall Qt fallback"
    }
}

foreach ($item in $shortcuts) {
    $shortcutPath = Join-Path $desktop $item.Name
    $shortcut = $wsh.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = "wscript.exe"
    $shortcut.Arguments = "`"$($item.Script)`""
    $shortcut.WorkingDirectory = $projectDir
    $shortcut.Description = $item.Description

    if (Test-Path $iconPath) {
        $shortcut.IconLocation = "$iconPath,0"
    }

    $shortcut.Save()
    Write-Host "Acceso directo creado/reparado: $shortcutPath" -ForegroundColor Green
}

Write-Host "------------------------------------------------" -ForegroundColor Cyan
Write-Host "Accesos directos listos." -ForegroundColor Green
Write-Host "Principal: Voice Stall v2.lnk (Tauri)" -ForegroundColor Green
Write-Host "------------------------------------------------" -ForegroundColor Cyan
Start-Sleep -Seconds 2
