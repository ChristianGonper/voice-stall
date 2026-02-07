$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$targetScript = Join-Path $projectDir "start_voz_silent.vbs"

if (-not (Test-Path $targetScript)) {
    Write-Error "No se encontro start_voz_silent.vbs en: $projectDir"
    exit 1
}

$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "Voice Stall.lnk"
$iconPath = Join-Path $projectDir "voice_stall_icon.ico"

$wsh = New-Object -ComObject WScript.Shell
$shortcut = $wsh.CreateShortcut($shortcutPath)
$shortcut.TargetPath = "wscript.exe"
$shortcut.Arguments = "`"$targetScript`""
$shortcut.WorkingDirectory = $projectDir
$shortcut.Description = "Abrir Voice Stall"
if (Test-Path $iconPath) {
    $shortcut.IconLocation = "$iconPath,0"
}
$shortcut.Save()

Write-Output "Acceso directo creado en: $shortcutPath"
if (Test-Path $iconPath) {
    Write-Output "Icono configurado: $iconPath"
}
