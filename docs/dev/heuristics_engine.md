# GradeOps-AI — Heuristics Engine Overview

## Objetivo actual

El motor heurístico actual de GradeOps-AI funciona como una capa de evaluación automática ligera orientada a:

- validar entregas
- detectar evidencia
- recuperar contenido legible
- buscar coincidencias simples
- sugerir una calificación inicial
- marcar casos para revisión manual

El modelo actual NO usa IA generativa ni modelos ML.
La evaluación se basa principalmente en reglas, umbrales y coincidencias configurables.

---

# Flujo general de evaluación

## 1. Validación de entrega

Primero valida si existe entrega:

- submission_state
- archivos adjuntos
- texto enviado
- links/formularios/videos

Si no existe entrega:

- auto_score = 0
- feedback automático indicando ausencia de evidencia

---

## 2. Detección de evidencia

El sistema identifica:

- PDF
- DOCX
- PPTX
- TXT
- ZIP
- imágenes
- links
- formularios
- YouTube

Tipos detectados:

- text_only
- file_only
- image_only
- mixed
- link_only
- none

---

## 3. Extracción de contenido legible

Actualmente intenta recuperar texto desde:

- PDFs
- Word
- PowerPoint
- TXT

Usa librerías simples:

- PyPDF2
- python-docx
- python-pptx

Si no logra recuperar contenido:

- marca baja confianza
- puede activar manual_review

---

# Heurísticas actuales

## Heurística de suficiencia mínima

Evalúa cantidad básica de contenido.

### Umbrales actuales

| Regla | Valor |
|---|---|
| min_words_partial | 10 |
| min_words_full | 50 |
| min_chars_partial | 80 |
| min_chars_full | 300 |

### Resultado

| Condición | Resultado |
|---|---|
| >= 50 palabras | suficiencia completa |
| >= 10 palabras | suficiencia parcial |
| < 10 palabras | insuficiente |

---

## Heurística de keywords

Busca coincidencias simples dentro del contenido extraído.

### Keywords default actuales

- control
- sistema
- resumen

### Reglas soportadas

## Coincidencia simple

control

## Múltiples obligatorias (AND)

control,sistema

## Alternativas (OR)

control/sistema

## Ocurrencias mínimas

control-2

## Combinaciones

control-2,sistema-1/modulo-3

Interpretación:

- "," = AND
- "/" = OR
- "-N" = ocurrencias mínimas

---

# Motores heurísticos actuales

## keyword_engine

Evalúa:

- presencia de palabras clave
- ocurrencias mínimas
- grupos AND/OR

Resultado:

- PASS
- FAIL

---

## sufficiency_engine

Evalúa:

- contenido legible
- cantidad de palabras

Resultado:

- PASS
- PARTIAL
- FAIL

---

## attachment_engine

Evalúa únicamente:

- existencia de evidencia adjunta

Resultado:

- PASS
- FAIL

---

## late_policy_engine

Evalúa:

- días de retraso
- entrega tardía

Resultado:

- PASS
- PARTIAL
- FAIL

Penalizaciones actuales:

| Condición | Penalización |
|---|---|
| tardanza menor | -5 |
| tardanza mayor | -10 |

---

## manual_review_engine

Marca entregas que requieren revisión humana.

Casos típicos:

- imágenes
- archivos no interpretables
- evidencia ambigua
- contenido ilegible

Resultado:

- MANUAL_REVIEW

---

## hybrid_engine

Motor fallback actual.

Combina:

- keywords
- evidencia
- revisión manual

Dependiendo del criterio configurado.

---

# Confidence score

El sistema genera un confidence_score heurístico entre 0 y 1.

Factores positivos:

- evidencia adjunta
- contenido legible
- suficientes palabras
- keywords detectadas

Factores negativos:

- solo imágenes
- mixed submissions
- manual_review
- contenido vacío

---

# Auto feedback actual

El sistema construye comentarios automáticos concatenando reglas simples.

Ejemplos:

- contenido legible detectado
- keywords encontradas
- entrega tardía
- requiere revisión manual
- sugerencia de calificación

Ejemplo típico:

"Contenido legible detectado con 120 palabras aprox. Coincidencias clave: sistema, control. Calificacion automatica sugerida: 85/100."

---

# Auto grading reason

Además del feedback visible, genera una explicación compacta interna.

Ejemplo:

"Entrega valida; contenido legible; suficiencia 20 pts; keywords detectadas."

Se usa principalmente para:

- auditoría
- debugging
- trazabilidad
- revisión docente

---

# Tipos de criterio actuales

El sistema infiere automáticamente el tipo de criterio:

| Tipo | Uso |
|---|---|
| keyword_match | coincidencias |
| minimum_words | suficiencia |
| document_presence | existencia de archivo |
| manual_review | revisión humana |
| late_policy | puntualidad |
| hybrid | fallback general |

---

# Limitaciones actuales

El motor actual:

- no entiende semántica real
- no evalúa calidad técnica profunda
- no valida lógica de programación
- no detecta plagio
- no interpreta diagramas complejos
- no usa embeddings ni NLP avanzado

Actualmente funciona mejor para:

- validación inicial
- preclasificación
- checklist académico
- detección rápida de evidencia
- apoyo human-in-the-loop

---

# Dirección arquitectónica prevista

La arquitectura ya está preparada para evolucionar hacia:

- motores heurísticos modulares
- criterios desacoplados
- schemas configurables
- plugins por tipo de actividad
- NLP/ML futuro
- semantic evaluation
- rubric-aware engines

Separación objetivo:

- grading/
- rubrics/
- runtime/
- domain/
- classroom/

---

# Estado actual

El grader actual funciona principalmente como:

- rule-based grader
- lightweight heuristic evaluator
- academic pre-review engine
- human-in-the-loop assistant

Prioriza:

- mantenibilidad
- compatibilidad
- trazabilidad
- bajo acoplamiento
- facilidad de configuración
