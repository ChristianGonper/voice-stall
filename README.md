# Voice Stall

<p align="center">
  <img src="voice_stall_icon.png" alt="Voice Stall Logo" width="180" />
</p>

Aplicación local de dictado para Windows con `faster-whisper`, hotkey global y pegado automático.

## Estado actual

- Aplicación activa: `tauri-app/` (Tauri + React + sidecar Python).
- Backend local: `python_backend.py`.
- Flujo principal: grabación -> transcripción STT -> diccionario -> pegado automático.
- Lanzamiento habitual en Windows: acceso directo que apunta a `start_voz_tauri_silent.vbs`.

## Requisitos

- Windows 10/11
- Python `>=3.12`
- `uv` en `PATH`
- Node.js 20+
- Rust toolchain estable
- GPU NVIDIA + CUDA recomendada; si no hay CUDA, el motor cae a CPU `int8`

## Instalación

```powershell
uv sync
cd tauri-app
npm install
```

## Ejecutar la aplicación

Desarrollo:

```powershell
cd tauri-app
npm run tauri dev
```

Lanzadores locales:

```powershell
.\start_voz_tauri.cmd
.\start_voz_tauri_silent.vbs
.\crear_acceso_directo_v2.ps1
```

## Configuración y datos locales

- Plantilla versionada: `config.default.json`
- Configuración local: `config.json`
- Historial local: `dictation_history.json`
- Logs de timing: `timings.log`

`config.json` no se genera al arrancar. Se crea cuando la aplicación guarda ajustes por primera vez.

## Tests

Backend Python:

```powershell
uv run python -m pytest -q
```

Frontend Tauri:

```powershell
cd tauri-app
npm test -- --run
```

## Benchmark local

```powershell
uv run python benchmarks/run_benchmark.py --iterations 2000
```

Salida local generada:

- `benchmarks/benchmark_latest.json`
- `benchmarks/benchmark_latest.md`

Estos archivos se generan bajo demanda y no forman parte del estado versionado normal.

## Guías adicionales

- Selección de modelo e idioma: `docs/model_language_guide.md`

## Estructura

- `python_backend.py`: sidecar Python persistente para Tauri
- `tauri-app/`: shell Tauri (Rust) + frontend React/TypeScript
- `dictation_service.py`: orquestación del ciclo de dictado
- `app_storage.py`: configuración, historial y timings locales
- `engine.py`: STT, perfiles, prompt y diccionario
- `recorder.py`: captura de audio y WAV temporal
- `tests/`: tests de backend

## Privacidad

- Audio y texto se procesan localmente.
- `temp_audio.wav` se borra tras procesar.
- Historial y métricas se guardan solo en local.
