# Workflow - Voice Stall

## General Principles
- **Local-First**: No se deben introducir dependencias que requieran conexión a internet durante el uso normal (salvo la descarga inicial del modelo).
- **Windows-Centric**: El desarrollo se centra en la compatibilidad y estética de Windows 10/11.
- **Minimalism**: Mantener la interfaz limpia y el código ligero.

## Development Process
- Usar siempre `uv` para gestionar dependencias y ejecución (`uv run`, `uv sync`).
- Los cambios en la UI deben ser coherentes con el estilo "Minimal Pro" definido en `main.py`.
- Cada nueva funcionalidad importante debe ir acompañada de su track correspondiente en Conductor.

## Code Standards
- Seguir PEP 8 para el código Python.
- Mantener la separación de responsabilidades:
    - `main.py`: Orquestación y UI.
    - `recorder.py`: Gestión de bajo nivel del hardware de audio.
    - `engine.py`: Lógica de transcripción y refinamiento.
- Documentar funciones complejas, especialmente en la integración con la API de Windows.

## Testing Strategy (Planned)
- Unit tests para el motor de transcripción (`engine.py`) usando mocks para evitar cargar el modelo pesado.
- Unit tests para el grabador (`recorder.py`) usando streams de audio falsos.
- Pruebas de integración para el flujo completo de dictado.
