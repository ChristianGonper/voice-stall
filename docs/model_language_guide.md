# Modelos e Idioma en Voice Stall

## Estado actual de la aplicación

La UI expone hoy dos opciones de modelo:

- `large-v3-turbo`: opción principal actual.
- `base`: opción ligera.

El backend no está limitado a esas dos. `engine.py` pasa `model_size` directamente a `WhisperModel`, así que puede trabajar con otros tamaños soportados por `faster-whisper` si se exponen en la UI o se escriben manualmente en `config.json`.

## Modelos que puede manejar `faster-whisper`

Según la documentación de `faster-whisper`, los nombres habituales disponibles incluyen:

- `tiny`
- `tiny.en`
- `base`
- `base.en`
- `small`
- `small.en`
- `medium`
- `medium.en`
- `large-v1`
- `large-v2`
- `large-v3`
- `turbo`
- variantes `distil-*`

En este proyecto ya se está usando `large-v3-turbo` en la configuración local. En la práctica, la familia `turbo` es la recomendación natural cuando priorizas velocidad con muy buena calidad.

## Recomendación práctica por perfil de uso

### `base`

- Cuándo usarlo:
  - equipos modestos
  - pruebas rápidas
  - fallback ligero
- Ventajas:
  - menos consumo
  - arranque e inferencia más ligeros
- Inconvenientes:
  - peor robustez con nombres propios
  - peor tolerancia a acento, ruido y spanglish

### `small`

- Cuándo tendría sentido añadirlo:
  - quieres algo claramente mejor que `base` sin irte al coste de `medium`
- Ventajas:
  - salto razonable de calidad
  - mejor equilibrio general
- Inconvenientes:
  - sigue estando bastante por debajo de `large-v3-turbo` en casos complejos

### `medium`

- Cuándo tendría sentido añadirlo:
  - dictado frecuente con mezcla ES/EN
  - necesitas más robustez que `small`
  - quieres una opción intermedia real
- Ventajas:
  - mejor captura de términos técnicos y pronunciaciones mixtas
  - más tolerancia a frases con spanglish
- Inconvenientes:
  - más memoria y más latencia que `small` o `base`
  - en muchos equipos, si ya puedes usar `large-v3-turbo`, suele compensar seguir en `turbo`

### `large-v3-turbo`

- Cuándo usarlo:
  - uso diario principal
  - GPU disponible
  - prioridad en calidad/velocidad global
- Ventajas:
  - mejor opción actual del proyecto para dictado técnico
  - buena calidad con latencia razonable
- Inconvenientes:
  - más pesado que `base`

## Qué haría en este proyecto

Si quieres una UI más normal para un usuario final, lo razonable es exponer:

- `base`
- `small`
- `medium`
- `large-v3-turbo`

Eso cubre bien:

- ligero
- intermedio
- robusto
- recomendado

## Cómo funciona hoy el idioma

En `engine.py` el comportamiento actual es este:

- `auto` -> no fija idioma y deja que Whisper lo detecte
- `en` -> fuerza inglés
- cualquier otro valor -> fuerza español

Eso significa que, para tu caso, hoy solo hay tres comportamientos reales:

- autodetección
- inglés fijo
- español fijo

## Recomendación para dictado con spanglish

Si la mayoría de tu dictado es español y solo metes palabras técnicas en inglés, la mejor opción actual suele ser:

- `language = "es"`
- mantener un `initial_prompt` explícito de spanglish técnico
- reforzar con `dictionary` las palabras que fallen de forma repetida

## Por qué `auto` no siempre ayuda

`auto` funciona mejor cuando:

- no sabes cuál será el idioma dominante
- cambias de idioma entre audios completos

`auto` suele funcionar peor cuando:

- la frase base es español
- insertas términos en inglés dentro de la misma oración
- quieres consistencia terminológica

En ese escenario, el detector puede interpretar mal la lengua dominante o normalizar palabras inglesas hacia algo parecido en español.

## Prompt vs diccionario: qué corrige cada uno

### `initial_prompt`

Sirve para orientar el contexto:

- estilo
- idioma dominante
- tipo de vocabulario
- instrucciones de conservación de términos

Es útil para decirle al modelo:

- que el dictado es español de España
- que puede haber términos técnicos en inglés
- que no traduzca esos términos

### `dictionary`

Sirve para correcciones deterministas después de la transcripción.

Es la mejor herramienta cuando ya sabes qué fallos se repiten, por ejemplo:

- `paifón` -> `Python`
- `matlap` -> `Matlab`
- `kiwin` -> `Qwen`

### Conclusión práctica

Para tu caso, el orden correcto hoy es:

1. fijar idioma a `es`
2. mantener un prompt de spanglish técnico
3. ampliar el diccionario con errores recurrentes

## Configuración recomendada hoy

Para tu uso habitual, yo probaría esta combinación antes de tocar más cosas:

- modelo: `large-v3-turbo`
- idioma: `es`
- perfil: `balanced`
- prompt inicial:
  - dictado profesional en español de España con terminología técnica en inglés
  - conservar términos ingleses tal como se pronuncian
  - no traducir nombres de herramientas, frameworks o productos

## Cuándo tendría sentido cambiar algo en código

Las siguientes mejoras sí tendrían sentido si quieres seguir afinando:

- exponer `small` y `medium` en la UI
- añadir documentación visible en la propia pantalla de ajustes
- soportar `hotwords` de `faster-whisper` además del diccionario
- permitir un modo más explícito para dictado bilingüe real

## Recomendación final

Para tu caso concreto:

- no empezaría por `auto`
- empezaría por `es`
- mantendría `large-v3-turbo`
- ajustaría el prompt inicial y el diccionario

Solo si eso sigue fallando de forma consistente, tendría sentido probar una opción intermedia como `medium` o añadir soporte de `hotwords`.
