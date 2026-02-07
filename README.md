# Voice Stall

Aplicación de dictado local (voz a texto) para Windows, con transcripción en español mediante `faster-whisper`, atajo global y pegado automático en la app que tengas enfocada.

## Resumen

Voice Stall captura audio desde el micrófono, lo transcribe localmente con Whisper y pega el resultado en el campo activo usando portapapeles + `Ctrl+V`.

Flujo operativo:

1. `Ctrl + Alt + S` inicia grabación.
2. `Ctrl + Alt + S` detiene grabación.
3. Se transcribe el WAV temporal.
4. Se copia el texto al portapapeles y se pega automáticamente.

## Características

- Ejecución local del motor STT (sin API de terceros en tiempo de ejecución).
- Optimización para GPU NVIDIA con CUDA (`torch` + `faster-whisper`).
- Fallback automático a CPU (`int8`) si CUDA no está disponible.
- Overlay de estado siempre visible (idle, recording, processing).
- Atajo global del sistema: `Ctrl + Alt + S`.
- Guardado de respaldo del último dictado en `backup_dictado.txt`.
- Limpieza automática del archivo temporal `temp_audio.wav`.
- Script para crear acceso directo de escritorio en Windows.

## Arquitectura

- `main.py`: UI (Tkinter), hotkey global, orquestación del flujo de dictado y pegado.
- `recorder.py`: captura de audio (PyAudio), buffer en memoria y guardado WAV.
- `engine.py`: carga del modelo Whisper y transcripción en español.
- `start_voz.cmd`: arranque estándar con `uv`.
- `start_voz_silent.vbs`: arranque silencioso (sin consola).
- `crear_acceso_directo.ps1`: crea `Voice Stall.lnk` en el escritorio.

## Requisitos

### Sistema operativo

- Soporte objetivo: Windows 10/11 (64-bit).
- El comportamiento de barra de tareas está implementado específicamente para Windows.

### Runtime

- Python `>= 3.12`.
- [uv](https://docs.astral.sh/uv/) instalado y en `PATH`.

### Dependencias Python

Definidas en `pyproject.toml`:

- `faster-whisper>=1.2.1`
- `torch==2.5.1` (índice CUDA 12.1 configurado)
- `pyaudio>=0.2.14`
- `pynput>=1.8.1`
- `pyautogui>=0.9.54`
- `pyperclip>=1.11.0`
- `pillow>=12.1.0`
- `numpy>=2.4.2`

### Hardware recomendado (2026)

- CPU: 6+ núcleos modernos.
- RAM: 16 GB mínimo (32 GB recomendado).
- GPU: NVIDIA con CUDA para baja latencia (VRAM recomendada: 8 GB+).
- Micrófono estable (USB o integrado con drivers al día).

## Instalación

1. Clona o descarga este repositorio.
2. En la raíz del proyecto, instala dependencias:

```powershell
uv sync
```

3. Ejecuta la aplicación:

```powershell
uv run main.py
```

Alternativa en Windows:

```powershell
.\start_voz.cmd
```

## Uso

1. Abre la aplicación donde quieres insertar texto (Word, navegador, chat, IDE, etc.).
2. Coloca el cursor en el campo de destino.
3. Pulsa `Ctrl + Alt + S` para empezar a dictar.
4. Pulsa `Ctrl + Alt + S` de nuevo para procesar.
5. El texto se pega automáticamente y se añade un espacio final.

## Modelo y comportamiento de transcripción

Configuración actual en código:

- Modelo: `large-v3-turbo`
- Idioma forzado: `es`
- `compute_type`: `float16` en CUDA, `int8` en CPU
- `beam_size`: `1` (prioriza latencia)
- Prompt inicial orientado a puntuación y estilo profesional en español

Nota: en la primera ejecución, el modelo puede descargarse localmente si no existe en caché.

## Privacidad y datos

- Audio y transcripción se procesan localmente.
- Se genera `temp_audio.wav` durante el ciclo de dictado y se elimina al finalizar.
- Se guarda el último resultado en `backup_dictado.txt` como respaldo local.
- El pegado es automático sobre la ventana enfocada: valida el foco antes de detener la grabación.

## Solución de problemas

### No inicia con `start_voz.cmd`

- Verifica que `uv` esté instalado y en `PATH`.
- Ejecuta `uv sync` para resolver dependencias.

### No detecta GPU / usa CPU

- Confirma drivers NVIDIA y disponibilidad CUDA.
- Revisa que la build de `torch` con CUDA esté instalada.
- La app hace fallback automático a CPU si CUDA no está disponible.

### Error con micrófono o grabación vacía

- Comprueba permisos de micrófono en Windows.
- Cierra apps que estén bloqueando el dispositivo de audio.
- Cambia de dispositivo de entrada predeterminado y vuelve a probar.

### Texto pegado en ventana incorrecta

- El pegado se realiza con `Ctrl+V` sobre la ventana activa.
- Antes de finalizar dictado, confirma que el foco esté en el campo correcto.

## Acceso directo de escritorio

Para crear un lanzador silencioso:

```powershell
.\crear_acceso_directo.ps1
```

Genera `Voice Stall.lnk` en el escritorio, apuntando a `start_voz_silent.vbs`.

## Limitaciones conocidas

- No hay diarización de hablantes.
- No hay VAD continuo; el control es manual por toggle.
- No hay historial de dictados dentro de la UI (solo `backup_dictado.txt`).
- No hay suite de tests automatizados en el repositorio actual.

## Desarrollo

Comandos útiles:

```powershell
uv run main.py
uv run python -m pip list
```

Si deseas endurecer el proyecto para producción 2026, prioridades sugeridas:

1. Configuración externa (`.env`/archivo de settings) para modelo, atajo e idioma.
2. Logging estructurado con niveles (`INFO/WARN/ERROR`).
3. Pruebas automáticas para `recorder.py` y `engine.py` con mocks.
4. Opciones de modo latencia/calidad seleccionables desde UI.

## Licencia

Pendiente de definir (`LICENSE`).
