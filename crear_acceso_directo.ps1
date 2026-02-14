# Obtener la ruta absoluta de la carpeta donde reside este script
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$targetScript = Join-Path $projectDir "start_voz_silent.vbs"

if (-not (Test-Path $targetScript)) {
    Write-Host "[ERROR] No se encontro start_voz_silent.vbs en: $projectDir" -ForegroundColor Red
    pause
    exit 1
}

$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "Voice Stall.lnk"
$iconPath = Join-Path $projectDir "voice_stall_icon.ico"

# Crear el objeto WScript.Shell para gestionar el acceso directo
$wsh = New-Object -ComObject WScript.Shell
$shortcut = $wsh.CreateShortcut($shortcutPath)

# IMPORTANTE: Usamos wscript.exe para ejecutar el .vbs de forma silenciosa
$shortcut.TargetPath = "wscript.exe"
$shortcut.Arguments = "`"$targetScript`""

# Esta es la clave de la portabilidad: establecer el WorkingDirectory a la carpeta actual
$shortcut.WorkingDirectory = $projectDir
$shortcut.Description = "Voice Stall - Dictado Local Inteligente"

if (Test-Path $iconPath) {
    $shortcut.IconLocation = "$iconPath,0"
}

$shortcut.Save()

Write-Host "------------------------------------------------" -ForegroundColor Cyan
Write-Host "¡Voice Stall actualizado correctamente!" -ForegroundColor Green
Write-Host "Ubicacion actual: $projectDir"
Write-Host "Acceso directo creado/reparado en el Escritorio."
Write-Host "------------------------------------------------" -ForegroundColor Cyan
# No cerramos inmediatamente para que el usuario vea el mensaje de éxito
Start-Sleep -Seconds 2
