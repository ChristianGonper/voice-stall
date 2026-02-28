# Tech Stack - Voice Stall

## Language & Runtime
- **Python**: 3.12+
- **Package Manager**: [uv](https://docs.astral.sh/uv/)

## Core Libraries (STT & Audio)
- **faster-whisper**: Motor de transcripción optimizado basado en CTranslate2.
- **torch**: 2.5.1+cu121 (Soporte CUDA 12.1 para aceleración por GPU).
- **PyAudio**: Captura de audio desde el micrófono.

## UI Framework
- **Tauri + React**: Framework moderno para aplicaciones de escritorio (Rust + React/TypeScript) con backend sidecar en Python.
- **PySide6**: UI secundaria/opcional (en proceso de migración).

## Automation & System Integration
- **pynput**: Escucha de atajos de teclado globales.
- **pyautogui**: Simulación de pulsaciones de teclas (Pegado automático).
- **pyperclip**: Gestión del portapapeles.
- **ctypes**: Integración profunda con la API de Windows (visibilidad en barra de tareas, estilos de ventana).

## Dependencies Management
- Definidas en `pyproject.toml` y bloqueadas con `uv.lock`.
- Índice específico de PyTorch para CUDA configurado.

## Storage
- **JSON**: Configuración de diccionario y ajustes de motor (`config.json`).
- **WAV**: Almacenamiento temporal de audio (`temp_audio.wav`).
- **TXT**: Respaldo de texto (`backup_dictado.txt`).
