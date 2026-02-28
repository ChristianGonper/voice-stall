# Specification - Model Selection (Large vs Base)

## Problem
El modelo `large-v3-turbo` ofrece la mejor calidad pero requiere hardware potente (especialmente VRAM). En equipos con menos recursos o cuando se prioriza la velocidad extrema sobre la precisión, el usuario no tiene forma de cambiar al modelo `base` sin editar el código.

## Proposed Solution
Añadir una opción en la ventana de configuración para alternar entre el modelo "Precisión (Large)" y "Velocidad (Base)". La aplicación debe guardar esta preferencia y recargar el motor de STT cuando el cambio sea aplicado.

## Requirements
- Opción visual en la ventana de ajustes (`open_dictionary_editor`).
- Persistencia de la elección en `config.json`.
- Lógica en `engine.py` para cargar el modelo seleccionado.
- Feedback en la UI indicando que se está recargando el motor.

## Success Criteria
- El usuario puede cambiar a "Base" desde la UI.
- La aplicación recuerda la elección tras reiniciar.
- El motor carga correctamente el modelo elegido (verificable por el tiempo de carga y logs).
