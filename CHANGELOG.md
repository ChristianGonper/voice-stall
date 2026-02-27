# Changelog

## 2.2.0 - 2026-02-27

### Migración a Tauri (fase de implementación)
- Nuevo sidecar Python persistente: `python_backend.py`.
- Nuevo shell Tauri + React/TypeScript en `tauri-app/`.
- Bridge Rust para requests/responses por `id` y eventos (`status`, `diag`) desde sidecar.
- Nuevos comandos Tauri:
  - `init_app`
  - `toggle_dictation`
  - `save_settings`
  - `set_hotkey`
  - `get_history`
  - `get_metrics`
- Convivencia temporal mantenida: `main_qt.py` sigue disponible como fallback.

### Pruebas
- Nueva suite para sidecar Python: `tests/test_python_backend.py`.

## 2.1.0 - 2026-02-27

### Cambios de arquitectura
- Nueva capa de orquestación: `dictation_service.py`.
- Nueva capa de persistencia: `app_storage.py`.
- Nuevo modelo tipado de salida de transcripción: `transcription_models.py`.
- `main_qt.py` reducido en acoplamiento: UI + acciones de interacción.

### Simplificación funcional
- Eliminada la detección/ejecución de comandos por voz tipo `abre ...`.
- Eliminado el refinado con LLM/Ollama y su configuración asociada.
- Flujo de dictado consolidado a una sola pasada: STT -> diccionario -> pegado.

### Calidad y pruebas
- Suite de tests actualizada para el nuevo alcance.
- Nuevas pruebas para almacenamiento (`tests/test_app_storage.py`) y servicio de dictado (`tests/test_dictation_service.py`).
- Nuevas pruebas de flujo del ciclo principal (`tests/test_main_qt_flow.py`).

### Rendimiento y evaluación técnica
- Runner de benchmark reproducible: `benchmarks/run_benchmark.py`.
- Artefactos de benchmark generados en `benchmarks/benchmark_latest.{json,md}`.
- Evaluación de framework documentada en `docs/framework_evaluation_2026-02-27.md`.

## 2.0.0 - 2026-02-17

**Voice Stall v2.0** - Interfaz moderna con PySide6

### Nuevo en v2
- Interfaz completamente rediseñada con PySide6
  - Diseño "Neo Control Panel" oscuro con acento azul/cian
  - Estados visuales claros: IDLE, REC, PROC, AI, ERR
  - Panel de configuración integrado (modelo, idioma, perfil, LLM, hotkey, diagnóstico)
  - Editor de diccionario en la UI
  - Métricas de rendimiento visuales
  - Microinteracciones y transiciones pulidas
- Archivos v2:
  - `main_qt.py`: aplicación PySide6
  - `start_voz_qt.cmd`: launcher Windows
  - `start_voz_qt_silent.vbs`: inicio silencioso
  - `crear_acceso_directo_v2.ps1`: script de acceso directo
- Documentación actualizada:
  - `README.md` con instrucciones para v2
  - `REDESIGN_PYSIDE6_2026.md` con detalles de arquitectura UI
  - `AGENTS.md` con directrices de desarrollo
- `.gitignore` reforzado para archivos de runtime

### Mantenido del motor
- Motor STT `faster-whisper` sin cambios
- Backend de grabación `recorder.py` sin cambios
- Lógica de perfiles y diccionario preservada
- Tests (11 pasando)

## 0.2.0 - 2026-02-14

- Idioma `auto` para mejorar mezcla ES/EN.
- Prompt ajustado para evitar cierres espurios tipo "gracias".
- Perfiles de transcripción: `fast`, `balanced`, `accurate`.
- Cache de configuración por `mtime` en motor STT.
- Diccionario con patrones precompilados para menor coste por dictado.
- Hotkey configurable desde la UI.
- Historial local de últimos 5 dictados.
- Logging de tiempos con rotación.
- Visor en ajustes con promedio de últimos 5 dictados.
- Limpieza de archivos locales/sensibles fuera del repositorio remoto.
