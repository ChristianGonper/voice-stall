@echo off
setlocal
cd /d "%~dp0"

set "TAURI_EXE=%~dp0tauri-app\src-tauri\target\debug\voice-stall-tauri.exe"
if exist "%TAURI_EXE%" (
  start "" "%TAURI_EXE%"
  exit /b 0
)

where npm >nul 2>nul
if errorlevel 1 (
  echo [ERROR] npm no esta disponible en PATH.
  pause
  exit /b 1
)

set "CARGO_BIN=%USERPROFILE%\.cargo\bin"
if exist "%CARGO_BIN%\cargo.exe" set "PATH=%CARGO_BIN%;%PATH%"

cd /d "%~dp0tauri-app"
call npm run tauri -- build --debug
set "exit_code=%errorlevel%"
if not "%exit_code%"=="0" (
  echo [ERROR] Fallo build debug de Tauri (codigo %exit_code%).
  pause
  exit /b %exit_code%
)

if exist "%TAURI_EXE%" (
  start "" "%TAURI_EXE%"
  exit /b 0
)

echo [ERROR] No se encontro voice-stall-tauri.exe despues del build.
pause
exit /b 1
