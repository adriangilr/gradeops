# GradeOps AI (Hybrid Pipeline)
A semi-automated grading system that combines heuristic rules, AI-assisted evaluation, and human validation to process classroom submissions at scale.

## Why GradeOps?
This project solves a practical workflow problem: collecting assignment deliverables and attached files from Google Classroom in a structured way, as well as reducing time spent on manual and individual grading and comments on classroom.

---

## Main features
- Rule-based grading (deterministic scoring customizable)
- Flags submission penalty handling
- AI-assisted feedback generation (optional)
- Human-in-the-loop review for edge cases
- Structured CSV output for auditability
- Support for multiple file types (PDF, DOCX, etc.)
- Designed for future ML integration

---

## Project structure
```text
gradeops/
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
├── HEURISTICS_ENGINE.md
├── credentials/
├── data/
├── docs/
│   ├── SETUP.md            # detailed setup
│   ├── SBS.md              # StepByStep
│   ├── ARCHITECTURE.md     # opcional (pro-level)
├── src/
├── tests/
└── output/
    └── course_name-activity_name
        ├── grading_results.csv
        ├── logActivity.yaml
        └── attachments/
```
---

### Output Fields
- submission_status
- is_readable
- word_count
- keyword_hits
- auto_score
- auto_feedback
- requires_manual_review
- final_grade

---
## Pipeline workflow
```
┌──────────────────────────────────────────────┐
│ HYBRID CLASSROOM GRADING PIPELINE            │
│ Heuristic + AI + Human-in-the-loop           │
└──────────────────────────────────────────────┘


[INPUT]                [PROCESS]                         [OUTPUT]

Submissions ───▶  File Processing ───▶  Heuristic Score ───▶ CSV Export
(files, API)       (readability, type)     (+ rules)

                         │
                         ▼
                   AI Feedback (optional)
                         │
                         ▼
                  Manual Review Flag
                         │
                         ▼
                   Final Grade / Feedback

```
---

### System Flow - pasar a arch

                 ┌───────────────────────────────┐
                 │        DATA SOURCE            │
                 │───────────────────────────────│
                 │ Google Classroom API          │
                 │ Submissions + Attachments     │
                 └───────────────┬───────────────┘
                                 │
                                 ▼
                 ┌───────────────────────────────┐
                 │     INGESTION LAYER           │
                 │───────────────────────────────│
                 │ Fetch submissions             │
                 │ Normalize metadata            │
                 │ Store raw files               │
                 └───────────────┬───────────────┘
                                 │
                                 ▼
                 ┌───────────────────────────────┐
                 │   PROCESSING LAYER            │
                 │───────────────────────────────│
                 │ File type detection           │
                 │ Text extraction (PDF/DOCX)    │
                 │ Readability validation        │
                 └───────────────┬───────────────┘
                                 │
                                 ▼
                 ┌───────────────────────────────┐
                 │  HEURISTIC ENGINE (CORE)      │
                 │───────────────────────────────│
                 │ Rule-based scoring            │
                 │ - word_count                  │
                 │ - keyword_hits                │
                 │ - late penalties              │
                 │ Deterministic + explainable   │
                 └───────────────┬───────────────┘
                                 │
                     ┌───────────┴───────────┐
                     │                       │
                     ▼                       ▼
     ┌──────────────────────────┐   ┌──────────────────────────┐
     │   AI AUGMENTATION LAYER  │   │   RULE-ONLY PATH         │
     │──────────────────────────│   │──────────────────────────│
     │ Feedback generation      │   │ Skip AI (faster path)    │
     │ Content evaluation       │   │                          │
     └──────────────┬───────────┘   └──────────────┬───────────┘
                    │                              │
                    └──────────────┬───────────────┘
                                   ▼
                 ┌───────────────────────────────┐
                 │   DECISION / ROUTING LAYER    │
                 │───────────────────────────────│
                 │ If unreadable → manual_review │
                 │ If low confidence → review    │
                 │ Else → auto-grade             │
                 └───────────────┬───────────────┘
                                 │
                                 ▼
                 ┌───────────────────────────────┐
                 │   HUMAN-IN-THE-LOOP LAYER     │
                 │───────────────────────────────│
                 │ Instructor validation         │
                 │ Override grading              │
                 │ Add final feedback            │
                 └───────────────┬───────────────┘
                                 │
                                 ▼
                 ┌───────────────────────────────┐
                 │        OUTPUT LAYER           │
                 │───────────────────────────────│
                 │ Structured CSV                │
                 │ Audit-ready results           │
                 │ final_grade + feedback        │
                 └───────────────────────────────┘


---

## Design Principles

- **Deterministic core** → predictable scoring
- **AI as augmentation** → not a black box
- **Human override always available**
- **Auditability via structured outputs**

---

## Use Case

This project is designed for:

- Instructors managing large class sizes
- Educational workflows requiring automation
- Data-driven evaluation processes
- Operational analytics in academic environments

---

## Disclaimer

This tool provides **automated suggestions** and **does not replace human grading**. Final evaluation should always be reviewed by instructors.

---

## Tech stack
- Python
- Google Classroom API
- Google Drive API
- Pandas
- OAuth 2.0


---

## Scalability Considerations

- Batch processing per coursework
- Parallel file parsing
- Pluggable AI layer (optional)
- CSV as interface between stages

---

##  About

Built by Adrian Gil  
Data Analyst | Operational Analytics  

Focused on building practical data tools for real-world workflows.
