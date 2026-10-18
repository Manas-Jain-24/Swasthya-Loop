# SwasthyaLoop — 24-Hour Healthcare Hackathon MVP
> **AI-Assisted Chronic-Care Follow-up Platform**  
> *Deterministic Clinical Rules • Traceable Follow-up Flags • Plain-Language Hybrid AI Summaries*

---

## 🌟 Overview
**SwasthyaLoop** bridges the critical gap between quarterly doctor appointments for patients managing chronic conditions (Hypertension and Type 2 Diabetes). It provides a unified, explainable loop connecting patients to hospital care coordinators while guaranteeing **clinical safety**:
- **Zero Hallucinated Diagnoses:** Prohibited from prescribing or modifying medication doses.
- **Auditable Traceability:** Every follow-up flag links to a concrete rule ID (e.g. `rule-missing-reading-v1`).
- **Hybrid AI Architecture:** Combines deterministic validation rules with optional constrained LLM summaries (with automatic offline fallback).

---

## 🚀 Quickstart: Running the Application

### 1. Launch with One Command
From PowerShell in the project directory:
```powershell
python run_server.py
```
This automatically starts the FastAPI backend server and launches your default browser at:
👉 **[http://localhost:8000](http://localhost:8000)**

### 2. Run Automated Test Suite
To verify the complete 8-test validation suite:
```powershell
& ".\.venv\Scripts\python.exe" -m pytest -o pythonpath=backend backend -v
```

---

## 📋 API Endpoints
- `GET  /api/health` — Service health check
- `GET  /api/patients` — List synthetic demo patients
- `GET  /api/patients/{id}` — Patient profile & care plan
- `GET  /api/patients/{id}/readings` — Longitudinal readings history
- `POST /api/patients/{id}/readings` — Ingest & validate new reading
- `GET  /api/patients/{id}/tasks` — Care tasks schedule
- `PATCH /api/tasks/{id}` — Update task status (completing resolves overdue flags)
- `GET  /api/coordinator/overview` — Care coordinator triage statistics
- `GET  /api/followups` — List active follow-up flags
- `PATCH /api/followups/{id}/resolve` — Mark follow-up resolved
- `POST /api/summaries` — Generate plain-language summary with fallback

---

## 🏛️ Project Directory Structure
```text
swasthya-loop/
├── backend/
│   ├── app/
│   │   ├── database.py       # SQLite engine & session factory
│   │   ├── models.py         # Patient, CarePlan, Reading, CareTask, FollowupFlag
│   │   ├── schemas.py        # Pydantic v2 schemas with range validators
│   │   ├── main.py           # FastAPI server & static UI mount
│   │   ├── routers/api.py    # REST API endpoints
│   │   ├── services/
│   │   │   ├── rules.py      # Deterministic task & safety rules
│   │   │   ├── summaries.py  # Fact aggregator & fallback engine
│   │   │   └── llm_provider.py # Constrained LLM adapter
│   │   ├── seed/demo_data.py # Idempotent seed data
│   │   └── static/index.html # Clinical dashboard SPA (React/Tailwind/Chart.js)
│   ├── tests/test_api.py     # Automated pytest suite (8 passed)
│   ├── swasthya.db           # SQLite database
│   └── requirements.txt
├── frontend/                 # Standard React + TypeScript scaffold
│   ├── src/api/client.ts
│   ├── src/types/index.ts
│   └── package.json
├── docs/
│   ├── architecture.md
│   ├── safety.md
│   └── demo-script.md
├── run_server.py             # 1-click launcher
└── README.md
```

---

## 🏆 Hackathon Demo Flow
Follow the 3-minute script in [docs/demo-script.md](docs/demo-script.md) for live presentation before judges.
