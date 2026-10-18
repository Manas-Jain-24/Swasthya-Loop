# SwasthyaLoop — Architecture Documentation

SwasthyaLoop is an AI-assisted chronic-care follow-up platform connecting patients and care coordinators through deterministic safety rules and constrained plain-language summaries.

## System Layers

### 1. Presentation Layer
- **Client Technology**: Modern Clinical Portal built with responsive, glassmorphic UI, Lucide icons, and Chart.js.
- **Role Switcher**: 1-click toggling between:
  - **Demo Patient A** (Hypertension monitoring & trend trajectory)
  - **Demo Patient B** (Type 2 Diabetes & overdue post-meal task detection)
  - **Care Coordinator Portal** (Multi-patient triage board with priority tags and audited source rules)

### 2. API & Ingestion Layer
- **Framework**: FastAPI (Python 3.13) + Pydantic v2.
- **Validation**: Strict boundary validation for physiological measurements:
  - Systolic BP: 40 - 300 mmHg
  - Diastolic BP: 20 - 200 mmHg (systolic must exceed diastolic)
  - Blood Glucose: 10 - 1000 mg/dL with explicit context tags (`fasting`, `after_meal`, etc.)
- **CORS Enabled**: Cross-origin support for both local development servers and embedded portals.

### 3. Persistence Layer
- **Database**: SQLite with SQLAlchemy ORM.
- **Tables**: `patients`, `care_plans`, `readings`, `care_tasks`, `followup_flags`, `rule_definitions`.
- **Seeding**: Idempotent startup seed generating reproducible demonstration states for Patient A and Patient B.

### 4. Hybrid AI Engine
The intelligence layer strictly separates deterministic rules from probabilistic generation:
- **Deterministic Rules (`rules.py`)**:
  - Overdue task identification (`READING_TASK_OVERDUE`).
  - Flag deduplication (no redundant alerts for identical events).
  - Traceable source rule mapping (`rule-missing-reading-v1`).
  - Dynamic resolution: marking a care task complete resolves associated overdue flags.
- **Constrained Plain-Language Summaries (`summaries.py` & `llm_provider.py`)**:
  - **Inputs**: Only approved, structured facts (reading counts, latest values, pending tasks, appointment date).
  - **LLM Adapter**: Connects optionally to Gemini 1.5 Flash.
  - **Deterministic Fallback**: If `GEMINI_API_KEY` is omitted, network drops, or output fails safety checks, the deterministic template is returned automatically. The application never crashes.
  - **Strict Guardrail**: Zero diagnosis, zero prescribing, zero modification of medications.
