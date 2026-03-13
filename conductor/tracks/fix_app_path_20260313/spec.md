# Track fix_app_path_20260313: Fix application not opening

## Description
The application fails to launch after being moved from `C:\Users\chris\Documents\Voz` to `C:\Users\chris\Documents\Proyectos\Voz`. This track focuses on identifying and fixing hardcoded paths to restore functionality.

## Context
- **Indicator:** User reported the app does not open.
- **Old Path:** `C:\Users\chris\Documents\Voz`
- **New Path:** `C:\Users\chris\Documents\Proyectos\Voz`

## Requirements
- [ ] Scan all project files for the old absolute path.
- [ ] Update PowerShell scripts (`.ps1`) and batch files (`.cmd`).
- [ ] Check `config.default.json` and `config.json` for path references.
- [ ] Ensure the Tauri sidecar configuration is path-independent.

## Success Criteria
- [ ] Application opens successfully using `start_voz_tauri.cmd`.
- [ ] Shortcut creation script works without referencing old paths.
- [ ] Python sidecar starts correctly.
