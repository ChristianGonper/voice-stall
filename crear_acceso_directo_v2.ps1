# Crea/repara accesos directos para nombre clasico y nombre v2.
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$legacyTargetScript = Join-Path $projectDir "start_voz_silent.vbs"
$qtTargetScript = Join-Path $projectDir "start_voz_qt_silent.vbs"

if (-not (Test-Path $legacyTargetScript)) {
    Write-Host "[ERROR] No se encontro start_voz_silent.vbs en: $projectDir" -ForegroundColor Red
    pause
    exit 1
}

if (-not (Test-Path $qtTargetScript)) {
    Write-Host "[ERROR] No se encontro start_voz_qt_silent.vbs en: $projectDir" -ForegroundColor Red
    pause
    exit 1
}

$desktop = [Environment]::GetFolderPath("Desktop")
$iconPath = Join-Path $projectDir "voice_stall_icon.ico"
$wsh = New-Object -ComObject WScript.Shell

$shortcuts = @(
    @{
        Name = "Voice Stall.lnk"
        Script = $legacyTargetScript
        Description = "Voice Stall - Dictado Local Inteligente"
    },
    @{
        Name = "Voice Stall v2.lnk"
        Script = $qtTargetScript
        Description = "Voice Stall v2 - UI Qt moderna"
    }
)

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
Write-Host "------------------------------------------------" -ForegroundColor Cyan
Start-Sleep -Seconds 2
