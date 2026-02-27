@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_voz_tauri.ps1"
exit /b %errorlevel%
