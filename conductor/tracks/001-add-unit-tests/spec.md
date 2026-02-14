# Specification - Add Unit Tests

## Problem
Actualmente el proyecto no tiene pruebas automatizadas. Esto dificulta la detección de regresiones al modificar el motor de audio (`recorder.py`) o el motor de transcripción (`engine.py`). Además, probar manualmente requiere grabar voz constantemente, lo cual es ineficiente.

## Proposed Solution
Crear una suite de pruebas unitarias usando `pytest`. Dado que dependemos de hardware (micrófono) y modelos pesados (Whisper), usaremos **Mocks** extensivamente para:
- Simular la entrada de audio en `AudioRecorder`.
- Simular la transcripción en `STTEngine` sin cargar realmente el modelo en memoria/GPU.

## Requirements
- Configurar `pytest` en el proyecto.
- Test para `AudioRecorder`: verificar que inicia/detiene grabación y genera archivos.
- Test para `STTEngine`: verificar la lógica de transcripción y el uso del diccionario.
- Asegurar que los tests se ejecuten rápidamente y sin dependencias externas.

## Success Criteria
- Ejecución exitosa de `pytest` con cobertura inicial en los módulos core.
- No se requiere micrófono físico ni GPU para pasar los tests.
