@
# Implementation Plan - Track legacy_cleanup_20260228

## Phase 1: Identification and Safekeeping
- [ ] Task: List all legacy files for final confirmation
    - [ ] Identify all non-Tauri related scripts (main_qt.py, start_voz_qt.*, etc.).
    - [ ] Verify which files are currently being used by the Tauri sidecar.
- [ ] Task: Create a temporary backup of key legacy files (optional but recommended)

## Phase 2: Removal of Legacy Assets
- [ ] Task: Delete legacy Python scripts and launchers
    - [ ] Remove main_qt.py.
    - [ ] Remove start_voz_qt.cmd, start_voz_qt_silent.vbs, and legacy .lnk files.
- [ ] Task: Cleanup root artifacts
    - [ ] Delete timings.log, backup_dictado.txt, and other legacy run artifacts.

## Phase 3: Dependency Update
- [ ] Task: Update pyproject.toml
    - [ ] Remove PySide6 from dependencies.
    - [ ] Run uv sync to update the lock file.
- [ ] Task: Verify Tauri application health
    - [ ] Launch the Tauri app and verify dictation flow is intact.
    - [ ] Verify that no "file not found" errors occur in the sidecar console.
@
