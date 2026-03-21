# Contributing to Voice Stall

## Flujo de trabajo

1. La rama principal del proyecto es `version-2.0`.
2. No trabajes directamente sobre `version-2.0`.
3. Crea una rama desde `version-2.0`:
   - `feat/...`
   - `fix/...`
   - `docs/...`
   - `chore/...`
4. Abre una Pull Request contra `version-2.0`.

## Validación mínima antes de abrir PR

```powershell
uv run python -m pytest -q
cd tauri-app
npm test -- --run
```

Revisa también que no estás subiendo archivos locales por error:

- `config.json`
- `dictation_history.json`
- `timings.log`
- accesos directos `.lnk`
- artefactos generados de benchmark

## Estilo del proyecto

- Python 3.12+
- `uv` para dependencias Python
- PEP 8 en Python
- `snake_case` para funciones y variables Python
- `PascalCase` para clases Python
- TypeScript estricto en `tauri-app/`

## Estructura actual

- app principal: `tauri-app/`
- sidecar backend: `python_backend.py`
- motor STT: `engine.py`
- grabación: `recorder.py`
- persistencia local: `app_storage.py`

## Configuración local

- Plantilla versionada: `config.default.json`
- Archivo local: `config.json`

`config.json` se crea al guardar ajustes desde la aplicación.
