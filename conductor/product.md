# Product Definition - Voice Stall

## Overview
Voice Stall es una aplicación de dictado (voz a texto) de alto rendimiento para Windows, diseñada para ser local, privada y minimalista. Permite a los usuarios transcribir voz en tiempo real y pegar el texto automáticamente en cualquier aplicación activa mediante un atajo de teclado global.

## Target Audience
- Usuarios que necesitan dictado rápido en Windows sin depender de servicios en la nube.
- Escritores, programadores y profesionales que buscan eficiencia en la entrada de texto.
- Usuarios preocupados por la privacidad de sus datos de voz.

## Core Features
- **Privacidad Total**: Procesamiento STT (Speech-to-Text) 100% local usando Whisper.
- **Integración Global**: Atajo de teclado (`Ctrl + Alt + S`) para iniciar/detener dictado en cualquier ventana.
- **Automatización de Pegado**: Copia y pega automáticamente el resultado en la aplicación enfocada.
- **Interfaz Minimalista**: Overlay de estado siempre visible (Topmost) con diseño moderno y oscuro.
- **Respaldo Automático**: Guarda el último dictado en un archivo de texto para evitar pérdidas.
- **Optimización de Hardware**: Soporte para GPU NVIDIA (CUDA) con fallback inteligente a CPU.

## Goals
- Mantener latencias bajas (transcripción casi instantánea).
- Garantizar una experiencia de usuario sin fricciones.
- Asegurar la robustez del motor de audio en diferentes entornos de Windows.
