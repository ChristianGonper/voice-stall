# Evaluación de Framework (2026-02-27)

## Contexto
- App local, single-user, Windows.
- Flujo actual simplificado: STT -> diccionario -> pegado.
- Hotkey global y ventana compacta siempre visible.

## Criterios de decisión
- Latencia percibida al dictar.
- Riesgo de regresión funcional (hotkey, foco, pegado).
- Complejidad operativa de mantenimiento.
- Coste de migración y tiempo de recuperación.

## Alternativas

### Mantener PySide6 (actual)
- Pros:
  - Sin migración: menor riesgo y entrega continua inmediata.
  - Integración nativa suficiente para app utilitaria local.
  - Coste operativo bajo tras el refactor modular ya aplicado.
- Contras:
  - App principal sigue en un archivo grande (`main_qt.py`) aunque mejoró.

### Migrar a Tauri/WebView
- Pros:
  - UI moderna con tooling web.
  - Binario más ligero que Electron en muchos casos.
- Contras:
  - Reescritura de UI + puente nativo para hotkeys/automatización.
  - Riesgo alto en comportamiento de foco/pegado de teclado.

### Migrar a .NET WPF/WinUI
- Pros:
  - Excelente integración nativa en Windows.
  - Buen soporte para hotkeys y shell integration.
- Contras:
  - Reescritura casi total del frontend y orquestación.
  - Duplicación de stack tecnológico (Python + .NET).

## Recomendación
1. No migrar framework en el corto plazo.
2. Mantener PySide6 y seguir con mejoras incrementales en módulos.
3. Revaluar migración solo si ocurre al menos una condición:
   - Latencia de UI > 100 ms de forma sostenida en acciones básicas.
   - Fallos recurrentes de hotkey/foco que no puedan mitigarse en PySide6.
   - Necesidad explícita de distribución empresarial o UI compleja multipantalla.

## Veredicto técnico
- Para uso personal local, el mejor ROI hoy es **seguir en PySide6**.
- La inversión debe centrarse en performance reproducible y robustez, no en reescritura de framework.
