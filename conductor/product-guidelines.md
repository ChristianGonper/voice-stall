# Product Guidelines - Voice Stall

## User Experience (UX)
- **Immediate Response**: El feedback visual (cambio de color en el overlay) debe ser instantáneo al pulsar el atajo.
- **Topmost & Non-Intrusive**: La ventana debe estar siempre encima pero ser lo suficientemente pequeña para no estorbar.
- **Zero Configuration**: La app debe funcionar "out-of-the-box" con valores sensatos para la mayoría de usuarios.

## User Interface (UI) Design
- **Color Palette**:
    - Fondo: `#07090C` (Casi negro).
    - Acentos: `#70A1FF` (Marca), `#FF4757` (Grabación), `#54A0FF` (Procesamiento).
    - Texto: `#F1F2F6` (Blanco suave).
- **Typography**: Bahnschrift (SemiBold y estándar) para un look técnico y limpio.
- **Visual Cues**: Uso de indicadores circulares de colores para representar estados (Idle, Rec, Proc, Loading).

## Error Handling
- Informar al usuario a través del texto de estado en la UI si algo falla (ej: "Error de Micrófono").
- Fallback silencioso a CPU si la GPU falla, pero registrando el evento para depuración.
- Asegurar la limpieza de archivos temporales (`.wav`) incluso si la app se cierra inesperadamente.
