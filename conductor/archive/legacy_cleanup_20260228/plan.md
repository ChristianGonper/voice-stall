@
# Implementation Plan - Track legacy_cleanup_20260228

## Phase 1: Identification and Safekeeping
- [x] Task: List all legacy files for final confirmation
        - [x] Identify all non-Tauri related scripts (main_qt.py, start_voz_qt.*, etc.).
        - [x] Verify which files are currently being used by the Tauri sidecar.
- [x] Task: Create a temporary backup of key legacy files (optional but recommended)

## Phase 2: Removal of Legacy Assets
- [x] Task: Delete legacy Python scripts and launchers
        - [x] Remove main_qt.py.
        - [x] Remove start_voz_qt.cmd, start_voz_qt_silent.vbs, and legacy .lnk files.
- [x] Task: Cleanup root artifacts
        - [x] Delete timings.log, backup_dictado.txt, and other legacy run artifacts.

## Phase 3: Dependency Update
- [x] Task: Update pyproject.toml
        - [x] Remove PySide6 from dependencies.
        - [x] Run uv sync to update the lock file.
- [x] Task: Verify Tauri application health
        - [x] Launch the Tauri app and verify dictation flow is intact.
        - [x] Verify that no "file not found" errors occur in the sidecar console.
@
