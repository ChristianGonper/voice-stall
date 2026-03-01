# Evaluación de Modificación de Framework: PySide6 -> Tauri

Fecha: 2026-02-27

> Nota histórica: este documento refleja una evaluación previa. El estado actual del repositorio ya consolidó la aplicación activa en `tauri-app/` con `python_backend.py`, y `main_qt.py` ya no forma parte del árbol.

## Objetivo
Determinar si la migración a Tauri mejora el rendimiento y mantenibilidad sin degradar hotkey global, foco y pegado automático.

## Estado actual
- Implementado prototipo funcional en `tauri-app/` con sidecar Python (`python_backend.py`).
- App PySide6 (`main_qt.py`) se mantiene como fallback operativo.
- Validación técnica de build completada:
  - `cargo check` exitoso en `tauri-app/src-tauri`.
  - `npm run tauri -- build --debug` exitoso (sin empaquetado).

## Impacto técnico del cambio
- Positivo:
  - UI desacoplada del motor STT.
  - Bridge explícito por protocolo JSON (más testeable).
  - Mejor camino a empaquetado multiplataforma en fases futuras.
- Riesgos:
  - Mayor complejidad operativa (Node + Rust + Python).
  - Superficie de fallo adicional en IPC y ciclo de vida del sidecar.

## Criterios de aceptación comparativa
1. `stop->paste p95` en Tauri no peor que +15% vs PySide6.
2. Fallo hotkey/pegado <= 1% en 100 ciclos.
3. RAM idle no > 2x baseline PySide6.
4. Sin regresiones funcionales en ajustes, historial y diagnóstico.

## Veredicto provisional
- Recomendación actual: **mantener convivencia temporal** y no retirar PySide6 todavía.
- Cambio de framework se aprobará para reemplazo solo si Tauri cumple los umbrales de benchmark y confiabilidad definidos.

## Estado actual del repositorio
- Esta recomendación quedó superada.
- La aplicación activa se ejecuta sobre Tauri + sidecar Python.
