@echo off
setlocal
cd /d "%~dp0"

where uv >nul 2>nul
if errorlevel 1 (
  echo [ERROR] uv no esta instalado o no esta en PATH.
  echo Instala uv desde: https://docs.astral.sh/uv/
  pause
  exit /b 1
)

uv run main_qt.py
set "exit_code=%errorlevel%"

if not "%exit_code%"=="0" (
  echo.
  echo Voice Stall (Qt) termino con error (codigo %exit_code%).
  pause
)

endlocal
