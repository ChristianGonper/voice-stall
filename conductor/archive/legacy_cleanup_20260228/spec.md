@
# Specification - Track legacy_cleanup_20260228

## Overview
This track involves cleaning up the project root by removing all files and dependencies associated with the legacy PySide6 (Qt) version of Voice Stall. The goal is to establish the Tauri + React version as the sole architecture.

## Scope
- Remove main_qt.py and any PySide6-specific UI logic.
- Delete legacy launchers and scripts (start_voz_qt.cmd, start_voz_qt_silent.vbs, etc.).
- Remove PySide6 from pyproject.toml and update the dependency lock.
- Cleanup root directory artifacts (old logs, backups, and temporary files).

## Functional Requirements
- Identify and delete all files mentioned in the legacy Qt documentation within the root.
- Update pyproject.toml to remove PySide6.
- Verify that the Tauri sidecar (python_backend.py) and its dependencies (engine.py, recorder.py, etc.) are unaffected.

## Acceptance Criteria
- [ ] main_qt.py is deleted.
- [ ] Legacy .cmd and .vbs files are removed.
- [ ] PySide6 is removed from pyproject.toml.
- [ ] The application remains fully functional via the Tauri interface.
- [ ] Root directory is free of non-essential legacy files.
@
