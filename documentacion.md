# Documentación Voice Stall (Dictado Pro Local)

Herramienta de dictado inteligente diseñada para ingenieros, optimizada para funcionar localmente con una NVIDIA A5070.

## 🚀 Inicio Rápido
1. **Atajo:** `Ctrl + Alt + S` para dictar. El primer dictado cargará el motor de IA (tardará unos segundos).
2. **Configuración (⚙):** Haz clic en el engranaje para personalizar el diccionario o activar el LLM.
3. **Guardar:** Usa siempre el botón "Guardar y Aplicar" para confirmar tus ajustes.

## 🧠 Características Especiales
- **Modo Spanglish:** Configurado para entender términos técnicos en inglés dentro de frases en español.
- **IA Refinamiento (Opcional):** Si activas **Qwen LLM**, la app pulirá tu texto automáticamente tras pegarlo. Requiere [Ollama](https://ollama.com) con el modelo `qwen2.5-coder:3b`.
- **Modo Inglés:** Fuerza la precisión en inglés técnico cuando lo necesites.

## 🛠️ Mantenimiento y Portabilidad
- **Mover la carpeta:** Si mueves la carpeta del proyecto, ejecuta `crear_acceso_directo.ps1` (Clic derecho -> Ejecutar con PowerShell) para reparar el acceso directo del escritorio.
- **Diccionario:** Puedes añadir términos como "kiwin" -> "Qwen" para que la app nunca se equivoque con nombres propios o marcas.
- **Privacidad:** Nada sale de tu ordenador. Todo el audio y texto se procesan en local.

## 📦 Dependencias (Gestión con UV)
Para añadir paquetes o limpiar:
```powershell
uv add <paquete> --index-strategy unsafe-best-match
```
