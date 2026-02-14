# 📖 Tutorial de Conductor: El Gestor de Proyectos de Gemini CLI

**Conductor** es una extensión diseñada para transformar la CLI de Gemini de un asistente de chat en un **ingeniero de software proactivo**. Utiliza un sistema de archivos persistentes para mantener el contexto, planificar tareas y ejecutar implementaciones de forma ordenada.

---

## 🏗️ 1. Estructura de Archivos
Conductor organiza todo en una carpeta raíz llamada `conductor/`. Esta carpeta es el "cerebro" que permite a Gemini recordar las reglas de tu proyecto.

### A. Archivos de Contexto Global (El ADN del proyecto)
Estos archivos definen la identidad del software y no suelen cambiar a menos que el proyecto evolucione:
- **`product.md`**: Define el propósito, el público objetivo y los objetivos del producto.
- **`tech-stack.md`**: Lista las tecnologías, lenguajes y frameworks permitidos.
- **`workflow.md`**: Describe los procesos de trabajo (ej: "siempre escribir tests", "estilo de commits").
- **`product-guidelines.md`**: Reglas específicas de diseño, arquitectura o UI/UX.
- **`tracks.md`**: El índice maestro que lista todas las tareas pendientes, en curso y terminadas.

### B. Las Tracks (Tareas Específicas)
Cada nueva funcionalidad o error se gestiona en una **Track** dentro de `conductor/tracks/<id_de_la_track>/`:
- **`spec.md`**: La especificación de *qué* hay que hacer.
- **`plan.md`**: La lista de pasos técnicos detallados de *cómo* se va a hacer.
- **`metadata.json`**: Información técnica sobre el estado de la tarea.

---

## 🕹️ 2. Modos de Operación
Conductor funciona mediante estados o comandos específicos:

1.  **`setup`**: Analiza el código existente y genera automáticamente el contexto inicial (`product.md`, `tech-stack.md`).
2.  **`newTrack`**: Crea una nueva unidad de trabajo. Gemini te preguntará qué quieres hacer, redactará la `spec.md` y luego el `plan.md`.
3.  **`implement`**: El modo de ejecución. Gemini lee el `plan.md` y realiza los cambios en el código, uno por uno, marcando el progreso.
4.  **`status`**: Muestra un resumen de en qué punto del proyecto te encuentras.
5.  **`review`**: Verifica que la implementación cumple con lo definido en la especificación.
6.  **`revert`**: Deshace los cambios realizados en una track específica si los resultados no son los esperados.

---

## 🚀 3. Flujo de Trabajo Recomendado

### Paso 1: Configuración Inicial
Si es la primera vez que usas Conductor en un proyecto, pide:
> *"Configura Conductor para este proyecto (`setup`)"*

### Paso 2: Definir una Tarea
Cuando necesites una nueva función:
> *"Crea una nueva track para añadir [funcionalidad] (`newTrack`)"*

### Paso 3: Revisar y Aprobar el Plan
Gemini escribirá un `plan.md`. **No empezará a programar todavía.** Debes leer el plan y decir:
> *"El plan me parece bien, adelante"* o *"Cambia el paso 2 para usar X librería"*.

### Paso 4: Ejecución
Una vez aprobado el plan:
> *"Implementa la track actual (`implement`)"*

---

## 💡 4. Consejos de Oro
- **Contexto Persistente:** Si dejas de trabajar y vuelves días después, Gemini leerá el `plan.md` y sabrá exactamente dónde se quedó. No tienes que volver a explicarle nada.
- **Tech Stack:** Si no quieres que Gemini use una librería específica, asegúrate de que **no** esté en `tech-stack.md`.
- **Iteración:** Puedes pedirle a Gemini que actualice el `product.md` o `workflow.md` en cualquier momento si las reglas del proyecto cambian.

---
*Generado por Gemini para el tutorial de Conductor CLI.*
