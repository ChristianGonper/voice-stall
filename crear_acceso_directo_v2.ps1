# Crear acceso directo "Voice Stall v2" que apunta a la version Qt silenciosa.
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$targetScript = Join-Path $projectDir "start_voz_qt_silent.vbs"

if (-not (Test-Path $targetScript)) {
    Write-Host "[ERROR] No se encontro start_voz_qt_silent.vbs en: $projectDir" -ForegroundColor Red
    pause
    exit 1
}

$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "Voice Stall v2.lnk"
$iconPath = Join-Path $projectDir "voice_stall_icon.ico"

$wsh = New-Object -ComObject WScript.Shell
$shortcut = $wsh.CreateShortcut($shortcutPath)
$shortcut.TargetPath = "wscript.exe"
$shortcut.Arguments = "`"$targetScript`""
$shortcut.WorkingDirectory = $projectDir
$shortcut.Description = "Voice Stall v2 - UI Qt moderna"

if (Test-Path $iconPath) {
    $shortcut.IconLocation = "$iconPath,0"
}

$shortcut.Save()

Write-Host "------------------------------------------------" -ForegroundColor Cyan
Write-Host "Acceso directo Voice Stall v2 creado/reparado." -ForegroundColor Green
Write-Host "Ubicacion: $shortcutPath"
Write-Host "------------------------------------------------" -ForegroundColor Cyan
Start-Sleep -Seconds 2
