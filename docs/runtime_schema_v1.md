# Runtime Schema v1 — GradeOps-AI

## Overview

This document defines the runtime schema currently used by GradeOps-AI for rubric processing, heuristic evaluation, and submission analysis.

The goal of the runtime layer is to provide:

- stable rubric execution
- predictable evaluation behavior
- backward compatibility
- low coupling between rubric structure and grading engines
- future extensibility for heuristic and ML-assisted evaluation

The runtime format is intentionally JSON-based to simplify:
- debugging
- portability
- inspection
- testing
- future integrations

---

# Runtime Architecture

Current execution flow:

```text
Rubric.xlsx
    ↓
runtime_builder
    ↓
rubric_runtime.json
    ↓
criterion evaluation
    ↓
aggregation layer
    ↓
submission result
```

The runtime JSON acts as the internal source of truth during evaluation.

---

# Runtime Version

Current stable schema:

```json
{
  "schema_version": "1.0.0"
}
```

Future rules:

| Change Type | Version Impact |
|---|---|
| Backward compatible fields | minor |
| New optional fields | minor |
| Breaking structure changes | major |
| Internal fixes only | patch |

Example:

- 1.0.0
- 1.1.0
- 1.2.0
- 2.0.0

---

# Runtime Root Structure

Example:

```json
{
  "schema_version": "1.0.0",
  "generated_at": "2026-05-11T18:10:00",
  "source_file": "config/Rubric.xlsx",
  "active_activity_name": "SE_P02",
  "rubrics": []
}
```

---

# Rubric Runtime Object

Each activity tab generates one rubric runtime object.

Example:

```json
{
  "sheet_name": "SE_P02",
  "rubric_id": "SE_P02",
  "criteria": []
}
```

---

# Criterion Runtime Structure

Each criterion is evaluated independently.

Example:

```json
{
  "criterion_id": "REQ_001",
  "rubric_id": "SE_P02",
  "criterion_name": "Matriz de requerimientos",
  "criterion_type": "keyword_match",
  "evaluation_strategy": "keyword_engine",
  "evaluation_config": {},
  "max_score": 10
}
```

---

# Required Fields

| Field | Type | Description |
|---|---|---|
| criterion_id | string | Unique criterion identifier |
| criterion_name | string | Human readable criterion |
| max_score | integer | Maximum obtainable score |
| rubric_id | string | Parent rubric identifier |

---

# Optional Fields

| Field | Type | Default |
|---|---|---|
| criterion_type | string | keyword_match |
| evaluation_strategy | string | keyword_engine |
| evaluation_config | dict | {} |
| manual_review | bool | false |
| matched_keywords | list | [] |
| language | string | es |

---

# Criterion Types

Supported v1 criterion types:

| criterion_type | Purpose |
|---|---|
| keyword_match | keyword detection |
| minimum_words | minimum sufficiency |
| document_presence | evidence validation |
| manual_review | human verification |
| structure_validation | structural checks |
| hybrid | mixed evaluation |

Unknown types should fallback safely.

---

# Evaluation Strategies

Evaluation strategies resolve execution engines.

Example:

```python
ENGINE_REGISTRY = {
    "keyword_engine": evaluate_keywords,
    "minimum_words_engine": evaluate_minimum_words,
}
```

Strategies are intentionally decoupled from the rubric source format.

---

# Evaluation Config

`evaluation_config` allows criterion-specific behavior without changing engine code.

Example:

```json
{
  "min_words": 50,
  "case_sensitive": false
}
```

---

# Keyword Runtime Format

Current keyword syntax:

```text
uml-2,clase-1/modulo-3
```

Interpretation:

- comma = AND group
- slash = OR group
- suffix number = minimum occurrences

Parsed internally into normalized structures.

---

# Criterion Result Structure

Each evaluated criterion generates a normalized result object.

Example:

```json
{
  "criterion_id": "REQ_001",
  "status": "PASS",
  "score": 8,
  "confidence": 0.87,
  "matched_keywords": [
    "uml",
    "clase"
  ]
}
```

---

# Supported Status Values

| Status | Meaning |
|---|---|
| PASS | criterion satisfied |
| PARTIAL | partially satisfied |
| FAIL | criterion failed |
| MANUAL_REVIEW | requires human validation |
| ERROR | execution failure |

---

# Aggregation Layer

The aggregation layer is responsible for:

- rubric totals
- weighted scores
- category totals
- normalization
- final submission score

Criterion engines should never compute final rubric grades directly.

---

# Runtime Stability Guidelines

The following should remain stable during v1 lifecycle:

- runtime root structure
- criterion field names
- CSV export schema
- folder naming strategy
- rubric execution flow

New engines should extend behavior without breaking existing runtime contracts.

---

# Logging Recommendations

Recommended runtime logs:

```text
data/runtime/logs/
```

Suggested structure:

```json
{
  "criterion_id": "REQ_001",
  "engine": "keyword_engine",
  "status": "FAIL",
  "reason": "keyword not found"
}
```

This improves:
- debugging
- reproducibility
- grading traceability

---

# Compatibility Notes

The runtime layer is intentionally:
- JSON-based
- deterministic
- portable
- human-readable
- backward-compatible when possible

The current design prioritizes:
- maintainability
- gradual evolution
- low operational complexity
- easier future ML integration

---

# Current Scope

v1 intentionally excludes:

- embeddings
- vector databases
- LLM grading
- OCR pipelines
- distributed execution
- microservices
- plugin marketplaces

These features belong to later architectural phases.

---

# Design Philosophy

GradeOps-AI runtime design follows:

- criterion-centric evaluation
- schema-driven behavior
- explicit runtime contracts
- isolated evaluation engines
- low coupling
- maintainable execution flow

The objective is to evolve gradually from heuristic evaluation toward hybrid human + AI assisted grading without requiring a full rewrite of the platform.
