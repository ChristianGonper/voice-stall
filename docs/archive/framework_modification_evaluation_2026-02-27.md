# Evaluación de Modificación de Framework (Archivado)

Documento histórico de transición PySide6 -> Tauri.

## Estado histórico

- Fecha original: `2026-02-27`
- Contexto original: validar si Tauri debía convivir temporalmente con PySide6
- Estado actual del repositorio: la aplicación activa ya usa Tauri + sidecar Python y `main_qt.py` ya no forma parte del árbol

## Resumen del contenido original

- Se consideraba Tauri como prototipo funcional con sidecar Python.
- La recomendación provisional era mantener convivencia temporal hasta cumplir umbrales de benchmark y confiabilidad.
- Esa recomendación quedó superada cuando Tauri pasó a ser la UI activa del proyecto.
