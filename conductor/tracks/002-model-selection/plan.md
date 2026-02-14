# Implementation Plan - Model Selection

## Phase 1: Configuration Updates
- [ ] Actualizar `config.json` para incluir un campo `selected_model` si no existe.
- [ ] Asegurar que `STTEngine.load_config` lea este nuevo parámetro.

## Phase 2: Engine Logic
- [ ] Modificar `STTEngine` para permitir la recarga del modelo sin reiniciar toda la app.
- [ ] Actualizar el constructor para usar el modelo guardado en la configuración.

## Phase 3: UI Implementation
- [ ] Añadir un selector de modelo en `open_dictionary_editor` (en `main.py`).
- [ ] Implementar la lógica de "Guardar y Aplicar" para que notifique al motor el cambio de modelo.
- [ ] Mostrar el estado "LOADING" en la UI mientras el nuevo modelo se carga en memoria.

## Phase 4: Verification
- [ ] Verificar que el cambio de modelo se refleja en `config.json`.
- [ ] Comprobar que el motor usa menos recursos (VRAM/CPU) al seleccionar el modelo `base`.
