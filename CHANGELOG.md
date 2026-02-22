# Changelog

## 2.0.0 - 2026-02-17

**Voice Stall v2.0** - Interfaz moderna con PySide6

### Nuevo en v2
- Interfaz completamente rediseñada con PySide6
  - Diseño "Neo Control Panel" oscuro con acento azul/cian
  - Estados visuales claros: IDLE, REC, PROC, AI, ERR
  - Panel de configuración integrado (modelo, idioma, perfil, LLM, hotkey, diagnóstico)
  - Editor de diccionario en la UI
  - Métricas de rendimiento visuales
  - Microinteracciones y transiciones pulidas
- Archivos v2:
  - `main_qt.py`: aplicación PySide6
  - `start_voz_qt.cmd`: launcher Windows
  - `start_voz_qt_silent.vbs`: inicio silencioso
  - `crear_acceso_directo_v2.ps1`: script de acceso directo
- Documentación actualizada:
  - `README.md` con instrucciones para v2
  - `REDESIGN_PYSIDE6_2026.md` con detalles de arquitectura UI
  - `AGENTS.md` con directrices de desarrollo
- `.gitignore` reforzado para archivos de runtime

### Mantenido del motor
- Motor STT `faster-whisper` sin cambios
- Backend de grabación `recorder.py` sin cambios
- Lógica de perfiles y diccionario preservada
- Tests (11 pasando)

## 0.2.0 - 2026-02-14

- Idioma `auto` para mejorar mezcla ES/EN.
- Prompt ajustado para evitar cierres espurios tipo "gracias".
- Perfiles de transcripción: `fast`, `balanced`, `accurate`.
- Cache de configuración por `mtime` en motor STT.
- Diccionario con patrones precompilados para menor coste por dictado.
- Hotkey configurable desde la UI.
- Historial local de últimos 5 dictados.
- Logging de tiempos con rotación.
- Visor en ajustes con promedio de últimos 5 dictados.
- Limpieza de archivos locales/sensibles fuera del repositorio remoto.
