# Implementation Plan: Fix application not opening

## Phase 1: Audit and Analysis
- [ ] Task: Audit scripts for hardcoded paths.
    - [ ] Search for `C:\Users\chris\Documents\Voz` in all project files.
    - [ ] List all files requiring updates.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Audit and Analysis' (Protocol in workflow.md)

## Phase 2: Fix Hardcoded Paths
- [ ] Task: Update PowerShell scripts.
    - [ ] Update `crear_acceso_directo_v2.ps1` to use the current working directory.
    - [ ] Update `start_voz_tauri.ps1` if necessary.
- [ ] Task: Update Batch/VBS scripts.
    - [ ] Update `start_voz_tauri.cmd`.
    - [ ] Update `start_voz_tauri_silent.vbs`.
- [ ] Task: Check configuration files.
    - [ ] Verify `config.json` (if exists) and `config.default.json`.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Fix Hardcoded Paths' (Protocol in workflow.md)

## Phase 3: Verification
- [ ] Task: Verify shortcut creation.
    - [ ] Run `crear_acceso_directo_v2.ps1`.
- [ ] Task: Verify application launch.
    - [ ] Run `start_voz_tauri.cmd`.
- [ ] Task: Verify Python sidecar.
    - [ ] Ensure logs indicate successful startup in the new location.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Verification' (Protocol in workflow.md)
