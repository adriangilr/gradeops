#  GradeOps-AI Architecture

This document describes the current architecture of GradeOps-AI, including its execution flow, main components, and future evolution path.

---

##  Overview

GradeOps-AI is a CLI-based pipeline designed to automate the extraction, evaluation, and structuring of student submissions from Google Classroom.

The system focuses on:
- Operational simplicity (CLI-driven)
- Transparent evaluation (rule-based scoring)
- Human-in-the-loop grading (manual review support)
- Portfolio-ready outputs (structured CSV + artifacts)

---

##  High-Level Flow

```mermaid
flowchart TD
	A[User CLI Input] --> B[Course Selection]
	B --> C[Download Submissions]
	C --> D[File Processing]
	D --> E[Rules Engine Evaluation]
	E --> F[Auto Score + Feedback]
	F --> G[CSV Export]
	G --> H[Optional AI Enrichment]

---

## Core Components

### CLI Controller (main.py)
Handles user interaction and orchestrates execution.

### Data Ingestion
Connects to Google Classroom API and downloads submissions.

Handles:

- Google Classroom API integration
- Coursework and submission retrieval
- File downloads

Outputs:

- Local folder structure organized by:
- Course
- Activity
- Student


### File Processing
Extracts readable content and detects file types.

Processes submission artifacts:

- Detects file types (PDF, DOCX, TXT, images, etc.)
- Extracts readable content when possible
- Flags non-readable submissions

Key outputs:

- is_readable
- word_count
- primary_file_type

### Rules Engine
Evaluates submissions using configurable scoring logic.

ToDo: Rules Engine (Current: Embedded → Future: Externalized)


Current State

- Hardcoded logic inside main.py

Target State

- External configuration file:

	/config/rulesActivity.json

	Example structure:

	{
		"base_score": 40,
		"rules": [
			{ "type": "has_submission", "score": 40 },
			{ "type": "has_content", "score": 20 },
			{ "type": "readable", "score": 20 },
			{ "type": "minimum_length", "threshold": 50, "score": 20 }
		],
		"penalties": [
			{ "type": "late", "days": 5, "penalty": 5 },
			{ "type": "late", "days": 999, "penalty": 10 }
		]
	}


### Evaluation Output Layer

Each submission generates:

- auto_score
- auto_feedback
- auto_grading_reason
- requires_manual_review
- confidence_score


### Export Layer
Generates structured CSV outputs.

Primary output:

- CSV file per activity

	Standard schema:

	- course_name
	- activity_name
	- student_name
	- student_mail
	- submission_status
	- has_attachment
	- submission_type
	- primary_file_type
	- days_late
	- is_readable
	- word_count
	- keyword_hits
	- requires_manual_review
	- confidence_score
	- auto_score
	- auto_feedback
	- auto_grading_reason
	- ai_feedback
	- final_grade
	- final_feedback

Logging System (Planned ToDo)

	Each activity will generate:

	/output/{activity}/logActivity.yaml

	Contains:

	- Evaluation decisions
	- Rule triggers
	- Errors or edge cases


### AI Layer (ToDo)

Planned as a post-processing and optional step, not core dependency.

Responsibilities:

- Improve feedback quality
- Suggest grading adjustments
- Summarize submissions

Design principle:

- AI augments decisions, does not replace rule transparency.

---

## Folder Structure

gradeops-ai/
├── src/
├── config/
├── data/
├── docs/
└── README.md

---

## Evolution Roadmap

Phase 1 (Current)
 - base script
 - Rule-based scoring
 - CSV export

Phase 2
 - Modularization (core modules)
 - External rules engine
 - Structured logging

Phase 3
 - AI feedback integration
 - Model-based scoring (rubric excel file to train IA)
 - Web UI / API layer


## Design Principles

-Transparency over complexity
-Deterministic first, AI later
-Human review always available
-Portable execution (low setup)

## Why This Architecture

This design prioritizes:

-Maintainability (simple pipeline)
-Extensibility (rules → ML transition)
-Real-world usability (educational workflows)
-Portfolio clarity (easy to explain in interviews)


---

##  About

Built by Adrian Gil  
Data Analyst | Operational Analytics  

Focused on building practical data tools for real-world workflows.
