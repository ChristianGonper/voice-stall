# Propuesta de rediseño 2026 (PySide6)

## Objetivo
Modernizar Voice Stall sin perder velocidad de dictado: mantener `engine.py` + `recorder.py`, migrar interfaz a `PySide6` y mejorar experiencia visual y flujo.

## Dirección visual
- Estilo: "Neo Control Panel" (oscuro técnico, alto contraste, acento azul/cian).
- Tipografía: `Segoe UI` (fallback estable en Windows).
- Superficie: tarjeta con gradiente, borde suave y estados con color semántico.
- Estados claros: `IDLE`, `REC`, `PROC`, `AI`, `ERR`.
- Feedback inmediato: botón principal, barra de progreso en inferencia/refinado y etiqueta de hotkey visible.

## Arquitectura UI propuesta
- `main_qt.py`:
  - `VoiceStallQtApp` como ventana principal.
  - `SignalBus` para actualizar UI desde hilos de grabación/STT.
  - Flujo base: cargar motor, iniciar/detener dictado, transcribir, pegar, refinar opcional.
- Mantener backend actual:
  - `engine.py` (faster-whisper + diccionario + LLM opcional).
  - `recorder.py` (captura de audio).

## Fases de migración
1. Fase 1 (implementada): ventana principal PySide6 funcional con hotkey global y ciclo de dictado.
2. Fase 2: panel de ajustes Qt (modelo, idioma, perfil, LLM, hotkey, diagnóstico).
3. Fase 3: historial visual y métricas de rendimiento en tiempo real.
4. Fase 4: microinteracciones (animaciones suaves, transiciones, refinado UX final).

## Componentes y tokens
- Colores:
  - Fondo: `#0b1118`
  - Tarjeta: gradiente `#111926 -> #0e1520`
  - Acento: `#4f8cff`
  - Texto principal: `#d7e4f1`
- Botón primario: radio 12px, hover/pressed definidos.
- Badge de estado: cápsula con color por modo.

## Criterios de éxito
- Arranque estable con `uv run main_qt.py`.
- Hotkey configurable respetada desde `config.json`.
- Tiempo total de ciclo de dictado equivalente o mejor al frontend Tkinter.
