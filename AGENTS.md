# Voz repo-specific notes

- Two runnable UIs coexist:
  - PySide fallback: `main_qt.py`
  - Primary migration target: `tauri-app/` + `python_backend.py`
- Tauri dev uses port `1430` (`vite.config.ts` + `src-tauri/tauri.conf.json`).
- Tauri Rust side always calls project venv Python when present:
  - `.venv/Scripts/python.exe` (Windows)
  - `.venv/bin/python` (Unix)
- If Tauri starts but sidecar fails, inspect lines prefixed with `[python-sidecar]` in terminal output.
- Desktop shortcut script `crear_acceso_directo_v2.ps1` points `Voice Stall v2.lnk` to Tauri and keeps a Qt fallback shortcut.
- Runtime local files used by this directory:
  - `config.json`
  - `dictation_history.json`
  - `timings.log`
