# Voice Stall

<p align="center">
  <img src="voice_stall_icon.png" alt="Voice Stall Logo" width="180" />
</p>

Aplicación local de dictado para Windows con `faster-whisper`, hotkey global y pegado automático.

## Estado del proyecto

- Rama canónica: `version-2.0`
- App principal (v2): `main_qt.py` (PySide6)

## Requisitos

- Windows 10/11
- Python `>=3.12`
- `uv` en `PATH`
- GPU NVIDIA + CUDA recomendada (fallback automático a CPU `int8`)

## Instalación

```powershell
uv sync
```

## Ejecutar v2 (principal)

```powershell
uv run main_qt.py
```

Opcional:

```powershell
.\start_voz_qt.cmd
.\start_voz_qt_silent.vbs
.\crear_acceso_directo_v2.ps1
```

## Configuración

- Plantilla versionada: `config.default.json`
- Configuración local (no versionada): `config.json`

Al arrancar la app, si `config.json` no existe, se genera automáticamente usando la plantilla.

## Tests

```powershell
uv run python -m pytest -q
```

## Estructura

- `main_qt.py`: UI principal, hotkey, historial, diagnóstico, pegado
- `engine.py`: STT, perfiles, prompt y diccionario
- `recorder.py`: captura de audio y WAV temporal
- `tests/`: tests unitarios

## Privacidad

- Audio y texto se procesan localmente.
- `temp_audio.wav` se borra tras procesar.
- Historial y métricas se guardan en local.
