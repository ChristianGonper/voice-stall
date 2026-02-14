# Historial de Cambios: Sesión de Optimización Premium

Este documento resume las mejoras críticas realizadas en Voice Stall para transformar el prototipo en una herramienta de ingeniería robusta y portátil.

## 🛠️ Portabilidad y Estabilidad
- **Rutas Agnósticas:** Se han sustituido todas las rutas relativas por rutas absolutas calculadas dinámicamente (`os.path.dirname(__file__)`). Ahora la carpeta se puede mover (ej. de Downloads a Documents) sin romper la app.
- **Reparador de Acceso Directo:** El script `crear_acceso_directo.ps1` ahora detecta su ubicación actual y actualiza el acceso directo del escritorio automáticamente con un solo clic.
- **Arreglo de Caracteres Especiales:** Se migró de `pyautogui.write` al portapapeles (`pyperclip`). Ahora las **tildes, la "ñ" y los símbolos técnicos** se pegan perfectamente.

## ⚡ Rendimiento Ultra-Rápido
- **Carga bajo Demanda (Lazy Loading):** La aplicación ahora abre de forma instantánea. El motor de IA solo se carga la primera vez que se pulsa el atajo de teclado para dictar.
- **Optimización de Imports:** Las librerías pesadas se importan dentro de hilos secundarios para no bloquear la interfaz.
- **VAD (Detección de Silencio):** Se ajustó el filtro de voz a **400ms** para que el dictado sea más ágil al terminar las frases.

## 🧠 Inteligencia y Personalización
- **Diccionario Visual:** Nueva interfaz integrada (⚙) para mapear palabras (ej. "kiwin" -> "Qwen"). Los reemplazos se hacen por Regex para mayor precisión.
- **Integración con Qwen 2.5 Coder:** Soporte opcional para refinamiento semántico vía Ollama. Incluye un sistema de "pegado en dos pasos" (Whisper instantáneo -> Refinado posterior).
- **Control Total:** Añadido botón de **"Guardar y Aplicar Cambios"** para evitar cargas accidentales de modelos pesados.
- **Modos de Idioma:**
    - **Español (Spanglish):** Modo por defecto optimizado para ingenieros que mezclan español e inglés técnico.
    - **Inglés:** Modo estricto para máxima precisión en lengua inglesa.

## 🎨 Interfaz de Usuario
- **Rediseño Minimal Modern:** Nueva paleta de colores "Deep Dark", animaciones de estado (Azul: Procesando, Morado: Refinando, Rojo: Grabando) y tipografía refinada.
- **Feedback Visual:** La app ahora confirma explícitamente cuando se aplican los cambios de configuración.
