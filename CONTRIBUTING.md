# Contributing to Voice Stall

Gracias por contribuir.

## Flujo de trabajo

1. La rama principal del proyecto es `version-2.0`.
2. No trabajes directamente sobre `version-2.0`.
3. Crea una rama de trabajo desde `version-2.0`:
   - `feat/...` para nuevas funcionalidades
   - `fix/...` para correcciones
   - `docs/...` para documentación
   - `chore/...` para mantenimiento
4. Abre una Pull Request hacia `version-2.0`.

## Requisitos antes de abrir PR

1. Ejecuta tests:
   ```powershell
   uv run python -m pytest -q
   ```
2. Verifica que no estás subiendo archivos locales por error (`config.json`, logs, historial, etc.).
3. Mantén los commits claros y en imperativo:
   - `feat: ...`
   - `fix: ...`
   - `docs: ...`
   - `chore: ...`

## Estilo del proyecto

- Python 3.12+
- Convenciones PEP 8
- `snake_case` para funciones/variables
- `PascalCase` para clases

## Estructura actual

- v2 principal: `main_qt.py`
- motor STT: `engine.py`
- grabación: `recorder.py`
- tests: `tests/`

## Configuración local

- Plantilla versionada: `config.default.json`
- Archivo local no versionado: `config.json`

Si `config.json` no existe, la app lo genera automáticamente desde la plantilla.
