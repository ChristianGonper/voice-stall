@echo off
setlocal
cd /d "%~dp0"

set "TAURI_APP_DIR=%~dp0tauri-app"
set "TAURI_EXE=%TAURI_APP_DIR%\src-tauri\target\debug\voice-stall-tauri.exe"
set "TAURI_MARKER=%TAURI_APP_DIR%\.tauri_debug_built.marker"
set "LAUNCH_LOG=%TAURI_APP_DIR%\tauri-launch.log"

set "NPM_CMD="
for /f "delims=" %%I in ('where npm.cmd 2^>nul') do (
  set "NPM_CMD=%%I"
  goto :npm_found
)
if exist "%ProgramFiles%\nodejs\npm.cmd" set "NPM_CMD=%ProgramFiles%\nodejs\npm.cmd"
if not defined NPM_CMD if exist "%AppData%\npm\npm.cmd" set "NPM_CMD=%AppData%\npm\npm.cmd"

:npm_found
if not defined NPM_CMD (
  echo [ERROR] npm no esta disponible. Instala Node.js y aseguralo en PATH. > "%LAUNCH_LOG%"
  start "Voice Stall Tauri - Error" cmd /k "type \"%LAUNCH_LOG%\""
  exit /b 1
)

set "CARGO_BIN=%USERPROFILE%\.cargo\bin"
if exist "%CARGO_BIN%\cargo.exe" set "PATH=%CARGO_BIN%;%PATH%"

set "NEED_BUILD=1"
if exist "%TAURI_EXE%" if exist "%TAURI_MARKER%" (
  powershell -NoProfile -Command "$exe=Get-Item '%TAURI_EXE%'; $mk=Get-Item '%TAURI_MARKER%'; if($exe.LastWriteTimeUtc -le $mk.LastWriteTimeUtc){exit 0}else{exit 1}" >nul 2>nul
  if not errorlevel 1 set "NEED_BUILD=0"
)

if "%NEED_BUILD%"=="0" (
  start "" "%TAURI_EXE%"
  exit /b 0
)

cd /d "%TAURI_APP_DIR%"
"%NPM_CMD%" run build > "%LAUNCH_LOG%" 2>&1
set "exit_code=%errorlevel%"
if not "%exit_code%"=="0" (
  echo [ERROR] Fallo frontend build (codigo %exit_code%). >> "%LAUNCH_LOG%"
  start "Voice Stall Tauri - Error" cmd /k "type \"%LAUNCH_LOG%\""
  exit /b %exit_code%
)

cd /d "%TAURI_APP_DIR%\src-tauri"
cargo build >> "%LAUNCH_LOG%" 2>&1
set "exit_code=%errorlevel%"
if not "%exit_code%"=="0" (
  echo [ERROR] Fallo cargo build (codigo %exit_code%). >> "%LAUNCH_LOG%"
  start "Voice Stall Tauri - Error" cmd /k "type \"%LAUNCH_LOG%\""
  exit /b %exit_code%
)

echo %DATE% %TIME%> "%TAURI_MARKER%"

if exist "%TAURI_EXE%" (
  start "" "%TAURI_EXE%"
  exit /b 0
)

echo [ERROR] No se encontro voice-stall-tauri.exe despues del build. > "%LAUNCH_LOG%"
start "Voice Stall Tauri - Error" cmd /k "type \"%LAUNCH_LOG%\""
exit /b 1
