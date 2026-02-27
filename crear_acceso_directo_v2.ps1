# Crea/repara accesos directos de Voice Stall (silencioso + debug)
# en Escritorio y Menu Inicio para busqueda de Windows.

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$silentScript = Join-Path $projectDir "start_voz_tauri_silent.vbs"
$debugScript = Join-Path $projectDir "start_voz_tauri.cmd"
$iconPath = Join-Path $projectDir "voice_stall_icon.ico"

if (-not (Test-Path $silentScript)) {
    Write-Host "[ERROR] No se encontro start_voz_tauri_silent.vbs en: $projectDir" -ForegroundColor Red
    pause
    exit 1
}
if (-not (Test-Path $debugScript)) {
    Write-Host "[ERROR] No se encontro start_voz_tauri.cmd en: $projectDir" -ForegroundColor Red
    pause
    exit 1
}

$desktopDir = [Environment]::GetFolderPath("Desktop")
$startMenuPrograms = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs"
$startMenuDir = Join-Path $startMenuPrograms "Voice Stall"

$wsh = New-Object -ComObject WScript.Shell
$includeStartMenu = $false

$shortcutDefs = @(
    @{
        Name = "Voice Stall.lnk"
        Kind = "silent"
        Description = "Voice Stall - inicio silencioso"
    },
    @{
        Name = "Voice Stall Debug.lnk"
        Kind = "debug"
        Description = "Voice Stall - inicio debug visible"
    }
)

$targetRoots = @($desktopDir)
try {
    if (-not (Test-Path $startMenuDir)) {
        New-Item -ItemType Directory -Path $startMenuDir -Force -ErrorAction Stop | Out-Null
    }
    $targetRoots += $startMenuDir
    $includeStartMenu = $true
}
catch {
    Write-Host "[WARN] No se pudo preparar carpeta de Menu Inicio: $startMenuDir" -ForegroundColor Yellow
    Write-Host "       $($_.Exception.Message)" -ForegroundColor Yellow
}

function Set-ShortcutTarget {
    param($shortcut, $kind, $silentScriptPath, $debugScriptPath)

    if ($kind -eq "silent") {
        $shortcut.TargetPath = "wscript.exe"
        $shortcut.Arguments = "`"$silentScriptPath`""
    }
    else {
        $shortcut.TargetPath = "cmd.exe"
        $shortcut.Arguments = "/c `"$debugScriptPath`""
    }
}

foreach ($root in $targetRoots) {
    foreach ($def in $shortcutDefs) {
        $shortcutPath = Join-Path $root $def.Name
        $shortcut = $wsh.CreateShortcut($shortcutPath)
        Set-ShortcutTarget -shortcut $shortcut -kind $def.Kind -silentScriptPath $silentScript -debugScriptPath $debugScript
        $shortcut.WorkingDirectory = $projectDir
        $shortcut.Description = $def.Description
        if (Test-Path $iconPath) {
            $shortcut.IconLocation = "$iconPath,0"
        }
        try {
            $shortcut.Save()
            Write-Host "Acceso directo creado/reparado: $shortcutPath" -ForegroundColor Green
        }
        catch {
            Write-Host "[WARN] No se pudo guardar: $shortcutPath" -ForegroundColor Yellow
            Write-Host "       $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
}

Write-Host "------------------------------------------------" -ForegroundColor Cyan
Write-Host "Listo:" -ForegroundColor Green
Write-Host "- Voice Stall.lnk (silencioso)" -ForegroundColor Green
Write-Host "- Voice Stall Debug.lnk (visible)" -ForegroundColor Green
if ($includeStartMenu) {
    Write-Host "Destino: Escritorio y Menu Inicio." -ForegroundColor Green
}
else {
    Write-Host "Destino: Escritorio (Menu Inicio no disponible en este entorno)." -ForegroundColor Yellow
}
Write-Host "------------------------------------------------" -ForegroundColor Cyan
Start-Sleep -Seconds 2
