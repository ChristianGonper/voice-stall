@
# Specification - Track tauri_migration_20260228

## Overview
This track aims to complete the migration of the core dictation flow from the PySide6 (Qt) application to the new Tauri + React frontend. This involves establishing the communication between the React UI and the python_backend.py sidecar.

## Scope
- Establish communication between Tauri frontend and Python backend sidecar.
- Implement the "Dictation" UI state (Idle, Recording, Processing).
- Display transcription results and timing metrics in the React UI.
- Handle global hotkeys for dictation control via the sidecar.

## Success Criteria
- [ ] User can start/stop dictation using a global hotkey or UI button.
- [ ] Real-time status feedback (color indicators and text) matches the "Deep Night Minimalist" design.
- [ ] Transcription results are correctly received from the sidecar and displayed.
- [ ] The application correctly pastes the text into the focused window.
- [ ] Spanish special characters (á, é, í, ó, ú, ñ) are handled correctly throughout the process.
@
