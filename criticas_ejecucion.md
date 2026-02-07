# Críticas de Ejecución (Abogado del Diablo)

Fecha: 2026-02-07

## Hallazgos críticos

1. Posible excepción al borrar archivo temporal si la grabación falla
- Archivo: `main.py:156`
- Riesgo: `audio_file` puede ser `None` (por ejemplo, si `stop_recording()` devuelve `None`) y `os.path.exists(None)` lanza `TypeError`.
- Impacto: el hilo de postprocesado puede romperse y dejar estado inconsistente de UI.

2. Falta de limpieza explícita de recursos de audio y hotkey global
- Archivos: `main.py:161`, `recorder.py:57`
- Riesgo: no se llama `recorder.cleanup()` ni se detiene el listener global al cerrar.
- Impacto: fugas de recursos (PyAudio abierto), hotkeys huérfanos, comportamiento errático tras reinicios.

## Hallazgos altos

1. Lectura de audio sin tolerancia a overflow
- Archivo: `recorder.py:26`
- Riesgo: `stream.read(self.chunk)` puede lanzar excepción por overflow dependiendo de carga del sistema.
- Impacto: grabación interrumpida y caída silenciosa del hilo de captura.

2. Sin control de errores en apertura de dispositivo de entrada
- Archivo: `recorder.py:19`
- Riesgo: si no hay micrófono válido o está ocupado, el hilo de grabación falla al abrir stream.
- Impacto: la app entra en estado “grabando” pero realmente no captura audio.

3. Inicialización de modelo pesada en arranque sin feedback de progreso
- Archivo: `engine.py:19`
- Riesgo: `WhisperModel(...)` puede tardar notablemente y bloquear percepción de arranque.
- Impacto: sensación de congelamiento y abandono por parte del usuario.

## Hallazgos medios

1. Uso de `beam_size=5` fijo para todos los escenarios
- Archivo: `engine.py:36`
- Riesgo: prioriza calidad sobre latencia de forma rígida.
- Impacto: mala experiencia en hardware limitado o en casos donde prima velocidad.

2. Dependencia de pegado automático sin validación de foco
- Archivo: `main.py:151`
- Riesgo: el texto puede pegarse en ventana equivocada.
- Impacto: fuga de información accidental y errores operativos.

3. Sin trazas estructuradas ni niveles de log
- Archivos: `main.py`, `recorder.py`, `engine.py`
- Riesgo: diagnóstico reactivo difícil en producción.
- Impacto: mayor tiempo de resolución de incidencias.

## Hallazgos bajos

1. Mensajería de consola informal
- Archivo: `main.py:87`
- Impacto: falta de consistencia para entorno profesional.

## Recomendaciones priorizadas

1. Blindar ciclo de vida de archivo temporal (`None`-safe) y cleanup garantizado en shutdown.
2. Añadir manejo robusto de errores de audio (open/read, overflow, mic no disponible).
3. Implementar cierre limpio (`WM_DELETE_WINDOW`): stop hotkey listener + `recorder.cleanup()`.
4. Introducir logging estructurado y códigos de error accionables.
5. Parametrizar calidad/latencia de transcripción (`beam_size`, modelo, dispositivo) vía config.

## Resumen ejecutivo

La app es funcional para demos locales, pero su ejecución actual tiene fragilidad en rutas de error y manejo de recursos. En condiciones reales (micrófono ocupado, overflow, cierre abrupto, foco incorrecto) hay alta probabilidad de comportamiento no determinista o interrupciones de flujo.
