# Investigación STT y Referencias

Información recopilada sobre modelos y herramientas para dictado local con inteligencia artificial.

## Modelos STT Principales
- **OpenAI Whisper (large-v3 o turbo)**: Modelo open source líder para transcripción local, soporta español nativo con buena inserción automática de comas, puntos y mayúsculas basada en prosodia. Corre offline con bajo WER (error de palabra) en acentos españoles. [modal](https://modal.com/blog/open-source-stt)
- **Faster-Whisper**: Implementación optimizada de Whisper (usa CTranslate2), más rápida (hasta 6x) y ligera para CPU/GPU, ideal para dictado en tiempo real. Mantiene puntuación similar a Whisper original. [aicybr](https://aicybr.com/blog/omnidictate-free-local-ai-dictation-windows)
- **Distil-Whisper**: Versión destilada de Whisper large-v3, 6x más rápida con precisión casi idéntica, aunque limitada a inglés en algunas variantes; usa la multilingual para español. [northflank](https://northflank.com/blog/best-open-source-speech-to-text-stt-model-in-2026-benchmarks)
- **Whisper.cpp**: Puerto C++ de Whisper para ejecución ultraeficiente en cualquier hardware (CPU, GPU, edge), perfecto para apps locales. Integra bien en apps cross-platform. [reddit](https://www.reddit.com/r/LocalLLaMA/comments/1ldvosh/handy_a_simple_opensource_offline_speechtotext/)

## Restauración de Puntuación
Whisper añade puntuación básica, pero para inferencia avanzada:
- **Whisper-Punctuator**: Herramienta zero-shot que usa el propio audio + transcripción de Whisper para insertar puntuación precisa en cualquier idioma, sin entrenamiento extra. [github](https://github.com/jumon/whisper-punctuator)
- **Modelos BERT/EfficientPunct**: Open source para post-procesado de texto sin puntuación. Añaden comas/puntos por contexto gramatical. [arxiv](https://arxiv.org/html/2409.11241v1)

## Aplicaciones Listas Open Source
- **OmniDictate**: Windows, usa faster-whisper, comandos de voz ("coma", "punto").
- **Handy**: Basada en whisper.cpp, atajo global, pega texto en apps activas.
- **Simon Listens**: Linux (KDE), modelos personalizables.

## Implementación Sugerida
- **Motor**: `faster-whisper`.
- **Librerías**: `pyaudio`, `pynput`, `pyautogui`.
- **Flujo**: Captura audio → STT (Whisper large-v3-turbo) → Transcripción → Inserción vía teclado simulado.
- **Entorno**: `uv` para gestión de dependencias.
