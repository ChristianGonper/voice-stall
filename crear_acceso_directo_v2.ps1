# Crea/repara accesos directos de Tauri: principal silencioso + debug visible.
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$tauriVisibleScript = Join-Path $projectDir "start_voz_tauri.cmd"
$tauriSilentScript = Join-Path $projectDir "start_voz_tauri_silent.vbs"
$qtTargetScript = Join-Path $projectDir "start_voz_qt_silent.vbs"

if (-not (Test-Path $tauriVisibleScript)) {
    Write-Host "[ERROR] No se encontro start_voz_tauri.cmd en: $projectDir" -ForegroundColor Red
    pause
    exit 1
}

if (-not (Test-Path $tauriSilentScript)) {
    Write-Host "[ERROR] No se encontro start_voz_tauri_silent.vbs en: $projectDir" -ForegroundColor Red
    pause
    exit 1
}

if (-not (Test-Path $qtTargetScript)) {
    Write-Host "[WARN] No se encontro start_voz_qt_silent.vbs en: $projectDir" -ForegroundColor Yellow
    Write-Host "Se crearan solo los accesos de Tauri." -ForegroundColor Yellow
}

$desktop = [Environment]::GetFolderPath("Desktop")
$iconPath = Join-Path $projectDir "voice_stall_icon.ico"
$wsh = New-Object -ComObject WScript.Shell

$shortcuts = @(
    @{
        Name = "Voice Stall v2.lnk"
        Script = $tauriSilentScript
        Description = "Voice Stall v2 - Tauri (silencioso)"
    },
    @{
        Name = "Voice Stall v2 Debug.lnk"
        Script = $tauriVisibleScript
        Description = "Voice Stall v2 - Tauri (debug visible)"
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
    $ext = [IO.Path]::GetExtension($item.Script).ToLowerInvariant()
    if ($ext -eq ".vbs") {
        $shortcut.TargetPath = "wscript.exe"
        $shortcut.Arguments = "`"$($item.Script)`""
    } elseif ($ext -eq ".cmd" -or $ext -eq ".bat") {
        $shortcut.TargetPath = "cmd.exe"
        $shortcut.Arguments = "/c `"$($item.Script)`""
    } else {
        $shortcut.TargetPath = $item.Script
        $shortcut.Arguments = ""
    }
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
Write-Host "Principal: Voice Stall v2.lnk (Tauri silencioso)" -ForegroundColor Green
Write-Host "Debug: Voice Stall v2 Debug.lnk (con consola)" -ForegroundColor Green
Write-Host "------------------------------------------------" -ForegroundColor Cyan
Start-Sleep -Seconds 2
