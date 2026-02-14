# Implementation Plan - Add Unit Tests

## Phase 1: Environment Setup
- [ ] Instalar `pytest` y `pytest-mock` usando `uv add --dev pytest pytest-mock`.
- [ ] Crear estructura de carpetas `tests/`.

## Phase 2: Core Engine Mocks
- [ ] Crear `tests/test_engine.py`.
- [ ] Mockear `faster_whisper.WhisperModel` para evitar carga de modelos.
- [ ] Probar método `transcribe` con diferentes entradas simuladas.
- [ ] Probar lógica de reemplazo de diccionario (si aplica en el engine).

## Phase 3: Recorder Mocks
- [ ] Crear `tests/test_recorder.py`.
- [ ] Mockear `pyaudio.PyAudio` y sus streams.
- [ ] Verificar que `start_recording` y `stop_recording` gestionan correctamente los hilos y el archivo temporal.

## Phase 4: Integration Check
- [ ] Ejecutar suite completa y verificar limpieza de archivos temporales generados durante tests.
