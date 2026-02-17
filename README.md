# Voice Stall

<p align="center">
  <img src="voice_stall_icon.png" alt="Voice Stall Logo" width="180" />
</p>

Dictado local para Windows con `faster-whisper`, hotkey global y pegado automático en la ventana activa.

## Estado actual

- Versión: `2.0.0` (**Voice Stall v2** con interfaz PySide6)
- Motor STT local (sin APIs externas para transcribir)
- Idioma por defecto: `auto` (detecta español/inglés)
- Perfiles de dictado: `fast`, `balanced`, `accurate`
- Hotkey configurable desde la UI
- Historial local de últimos 5 dictados
- Modo diagnóstico opcional con métricas de tiempos
- Versión legacy v1 (Tkinter) disponible en carpeta `v1/`

## Flujo

1. Activa con hotkey (por defecto `Ctrl + Alt + S`)
2. Vuelve a pulsar para detener
3. Se transcribe `temp_audio.wav`
4. Se pega el texto vía portapapeles + `Ctrl+V`

## Configuración (`config.json`)

Bloques principales:

- `engine`
  - `model_size`: `large-v3-turbo` o `base`
  - `language`: `auto`, `es`, `en`
  - `profile`: `fast`, `balanced`, `accurate`
  - `initial_prompt`
  - `use_llm`
- `app`
  - `hotkey`
  - `history_limit` (actualmente 5)
  - `timing_log_max_kb`
  - `diagnostic_mode`
- `dictionary`
  - Reglas de reemplazo personalizado

## Modo diagnóstico

Puedes activarlo de dos formas:

1. Desde Ajustes: botón `Diag` (`ON/OFF`)
2. Por flag al arrancar:

```powershell
uv run main.py --diag
```

Cuando está activo:

- Escribe métricas en `timings.log` (con rotación a `timings.log.1`)
- Muestra promedio de tiempos (últimos 5 dictados) en la ventana de ajustes

Cuando está desactivado:

- No escribe métricas en `timings.log`

## Requisitos

- Windows 10/11
- Python `>=3.12`
- `uv` en `PATH`
- GPU NVIDIA + CUDA recomendada (fallback automático a CPU `int8`)

## Instalación y ejecución

```powershell
uv sync
uv run main.py
```

Interfaz moderna (PySide6, fase inicial):

```powershell
uv run main_qt.py
```

Opcional:

```powershell
.\start_voz_qt.cmd
```

Accesos directos en escritorio:

```powershell
.\crear_acceso_directo_v2.ps1   # Voice Stall v2 (Qt)
```

Build legacy v1 (mantenida en carpeta separada):

```powershell
.\v1\start_voz.cmd
.\v1\crear_acceso_directo.ps1
```

## Tests

```powershell
uv run pytest -q
```

## Estructura

- `main.py`: UI, hotkey, historial, diagnóstico, pegado
- `engine.py`: STT, perfiles, prompt, diccionario
- `recorder.py`: captura de audio y WAV temporal
- `tests/`: unit tests

## Privacidad

- Audio y texto se procesan localmente
- `temp_audio.wav` se borra tras procesar
- Historial y métricas se guardan solo en local (si están activos)
