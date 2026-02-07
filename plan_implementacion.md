# Plan de Implementación: App de Dictado Local (Voz-a-Texto)

Este proyecto busca crear una herramienta de dictado profesional que funcione 100% localmente, con baja latencia y puntuación inteligente, optimizada para un equipo con 16GB de RAM.

## 1. Stack Tecnológico Seleccionado
*   **Motor STT:** `faster-whisper`. Es significativamente más rápido que el Whisper original y permite usar modelos como `large-v3-turbo` de forma eficiente.
*   **Procesamiento de Audio:** `PyAudio` para la captura en tiempo real.
*   **Interfaz:** `Tkinter` para un overlay minimalista y transparente.
*   **Control Global:** `pynput` para detectar atajos de teclado (ej. Ctrl+Alt+V) y capturar/detener el dictado.
*   **Inserción de Texto:** `pykeyboard` o `pyautogui` para simular la escritura en cualquier aplicación activa.

## 2. Características Principales
*   **Modo Toggle:** Presionar una tecla para empezar a grabar, presionar de nuevo para transcribir e insertar.
*   **Feedback Visual:** Un pequeño indicador en pantalla (LED virtual) que cambie de color según el estado (Grabando, Procesando, Listo).
*   **Puntuación Inteligente:** Uso de `large-v3-turbo` con un "prompt" inicial en español para forzar un estilo formal y puntuado.
*   **Multilingüe:** Optimizado para Español (España).

## 3. Estructura de Archivos
*   `main.py`: Punto de entrada y lógica de la GUI.
*   `engine.py`: Clase que maneja el modelo de AI (`faster-whisper`).
*   `recorder.py`: Gestión del micrófono y búfer de audio.
*   `config.py`: Parámetros configurables (tecla de atajo, modelo, idioma).

## 4. Próximos Pasos
1. Investigar la viabilidad de `faster-whisper` con el modelo `large-v3-turbo` en el entorno local.
2. Implementar el prototipo básico de grabación y transcripción.
3. Añadir la funcionalidad de "teclado virtual" para insertar el texto.
