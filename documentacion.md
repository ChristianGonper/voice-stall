# Documentacion de Voice Stall (Dictado Local)

Este proyecto ha sido diseñado para ofrecer una experiencia de dictado profesional, rápida y privada, funcionando íntegramente de forma local en tu equipo.

## 1. Funcionamiento 100% Local
La aplicación **no envía audio ni texto a la nube**. Todo el procesamiento ocurre dentro de tu ordenador gracias a los modelos de inteligencia artificial alojados en tu disco duro. Esto garantiza:
*   **Privacidad Total**: Tus conversaciones y dictados nunca salen de tu máquina.
*   **Sin Suscripciones**: No dependes de APIs externas ni cuotas mensuales.
*   **Funcionamiento Offline**: Puedes dictar aunque no tengas conexión a internet.

## 2. Tecnologías Utilizadas
*   **faster-whisper (Engine)**: Una implementación optimizada del modelo Whisper de OpenAI que permite una transcripción extremadamente rápida.
*   **NVIDIA CUDA**: Al detectar tu tarjeta NVIDIA A5070, la app utiliza los núcleos Tensor para acelerar el dictado, reduciendo la latencia al mínimo.
*   **Puntuación Inteligente**: El modelo `large-v3-turbo` está configurado para entender el contexto y añadir puntos, comas y mayúsculas automáticamente basándose en tus pausas y entonación.
*   **Interfaz Windows**: Una pequeña ventana flotante y minimalista que indica el estado del dictado (Grabando, Procesando, Listo).

## 3. Guía de Uso
*   **Atajo de Teclado**: Presiona `Ctrl + Alt + S` para empezar a grabar. Presiona la misma combinación para detenerte.
*   **Inserción de Texto**: Una vez procesado, el texto aparecerá automáticamente donde esté tu cursor.
*   **Indicadores Visuales**:
    *   **Gris**: En espera (Voice Stall descansando).
    *   **Rojo**: Grabando audio.
    *   **Azul/Animado**: Procesando con IA.

## 4. Optimización de Recursos
La app está configurada para aprovechar tus **32GB de RAM** y los **8GB de VRAM** de tu NVIDIA A5070:
*   **Modo float16**: Utiliza precisión de punto flotante de 16 bits en la GPU, lo que acelera el procesamiento sin perder precisión.
*   **Gestión de VRAM**: El modelo `large-v3-turbo` ocupa aproximadamente 3-4GB de VRAM, dejando el resto libre para que tu sistema no se ralentice.

## 5. Tip para Portátiles (NVIDIA Optimus)
Si notas que la app tarda unos segundos en "despertar" en el primer dictado, puedes forzar el alto rendimiento:
1.  Ve a **Configuración de Windows** > **Sistema** > **Pantalla** > **Gráficos**.
2.  Busca el ejecutable de Python de este proyecto: `c:\Users\chris\Downloads\Voz\.venv\Scripts\python.exe`.
3.  Haz clic en **Opciones** y selecciona **Alto rendimiento** (GPU NVIDIA).

