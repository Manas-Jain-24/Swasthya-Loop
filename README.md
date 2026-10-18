# SwasthyaLoop — Post-Discharge Care Coordination & Clinical Triage Platform
> **Intelligent, Protocol-Grounded Chronic-Care Follow-Up Engine**  
> *Deterministic Safety Rules • Traceable Follow-Up Flags • Gemini 3.8 Flash Clinical Synthesis*

[![Live 2-Minute Demo](https://img.shields.io/badge/YouTube-2--Minute%20Live%20Demo-red?style=for-the-badge&logo=youtube)](https://youtu.be/YpQU1QlJLt8)
[![Test Suite](https://img.shields.io/badge/Pytest-8%20Passed%20(100%25)-emerald?style=for-the-badge&logo=pytest)](backend/tests/test_api.py)
[![Model](https://img.shields.io/badge/AI%20Engine-Gemini%203.8%20Flash-blueviolet?style=for-the-badge&logo=google)](backend/app/services/llm_provider.py)
[![ABDM](https://img.shields.io/badge/Standards-ABDM%20Sandbox%20Ready-blue?style=for-the-badge)](https://abdm.gov.in/)

---

## 📺 2-Minute Live Video Demonstration
Watch the complete end-to-end working demonstration (01:52) showcasing the Clinical Command Center, multi-condition directory, longitudinal vitals curve, Gemini 3.8 Flash synthesis, and deterministic triage resolution:

👉 **[Watch Live Demo on YouTube](https://youtu.be/YpQU1QlJLt8)**

[![SwasthyaLoop Live Video Demo](https://img.youtube.com/vi/YpQU1QlJLt8/maxresdefault.jpg)](https://youtu.be/YpQU1QlJLt8)

---

## 🎯 The Problem: The "Discharge Void" in Indian Healthcare
Every year in India, over **60% of chronic care patients** (Hypertension, Type-2 Diabetes, and Multimorbidities) drop out of structured outpatient follow-ups within 90 days of discharge. 

With India's doctor-to-patient ratio at **1:1,456** (WHO standard is 1:1,000) and tertiary OPD doctors seeing 80–120 patients/day (<2.5 min/consultation), manual follow-up calls are unviable. Asymptomatic blood pressure and glucose spikes go unnoticed until patients reappear in catastrophic crisis (stroke, diabetic ketoacidosis, acute heart failure) — **up to 30% of which are clinically preventable**.

---

## 💡 The Solution: SwasthyaLoop
**SwasthyaLoop** is a protocol-grounded, closed-loop clinical coordination and triage platform that bridges home vitals directly into hospital clinical workflows:

1. **Deterministic Clinical Safety Core (Zero Hallucination):** Triage alerts and crisis escalations (e.g. `RULE-HTN-001`: Stage 2 Crisis for BP >160/100 mmHg) are calculated with 100% deterministic rule logic grounded in ICMR 2023 and AHA/ACC guidelines.
2. **Generative Trajectory Synthesis (Gemini 3.8 Flash):** Ingests longitudinal home vitals, active alerts, and medication regimens to generate sub-5-second physician-grade summaries and patient-friendly guidance.
3. **Clinician-in-the-Loop Workflow:** Every alert features clear clinical rationale, recommended protocol actions, and a one-click audit resolution workflow with automated CSV reporting.
4. **ABDM Compatible Architecture:** Structured around FHIR R4 resources for seamless integration with the Ayushman Bharat Digital Mission.

---

## 🚀 Quickstart: Running Locally

### 1. Launch with One Command
From PowerShell in the project directory:
```powershell
# Start FastAPI backend (port 8001)
& ".\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```
Open your browser at:  
👉 **[http://localhost:8001](http://localhost:8001)**

### 2. Run Automated Test Suite
To verify the complete 8-test validation suite:
```powershell
$env:PYTHONPATH="backend"; & ".\.venv\Scripts\python.exe" -m pytest backend/tests -v
```
**Result:** `8 passed in 7.76s (100% test pass rate)`

---

## 🌐 Core API Endpoints
- `GET  /api/health` — Service health & uptime check
- `GET  /api/patients` — List cohort patients with current risk status
- `GET  /api/patients/{id}` — Patient profile, longitudinal vitals & care plan
- `POST /api/patients/{id}/readings` — Ingest & range-validate new health reading
- `POST /api/patients/{id}/gemini-summary` — Real-time Gemini 3.8 Flash clinical synthesis
- `GET  /api/coordinator/overview` — Care coordinator triage statistics & metrics
- `GET  /api/followups` — List active triage flags (High / Medium / Low)
- `PATCH /api/followups/{id}/resolve` — Resolve triage flag with clinical audit note
- `POST /api/tasks/{id}/complete` — Complete care plan task (resolves overdue alert)

---

## 📂 Project Directory Structure
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
│   │   │   ├── rules.py      # Deterministic clinical safety rules (ICMR/AHA)
│   │   │   ├── summaries.py  # Fact aggregator & fallback engine
│   │   │   └── llm_provider.py # Gemini 3.8 Flash clinical adapter
│   │   ├── seed/demo_data.py # 5-patient diverse cohort (HTN Crisis, T2D, Dual)
│   │   └── static/index.html # Clinical dashboard SPA (Tailwind/Chart.js/Lucide)
│   ├── tests/test_api.py     # Automated pytest test suite (8/8 passed)
│   ├── swasthya.db           # SQLite database
│   └── requirements.txt
├── docs/
│   ├── architecture.md
│   ├── safety.md
│   └── demo-script.md
└── README.md
```

---

## 🏆 Presentation Assets
- **Live 2-Minute Demo:** [https://youtu.be/YpQU1QlJLt8](https://youtu.be/YpQU1QlJLt8)
- **GitHub Repository:** [https://github.com/Manas-Jain-24/Swasthya-Loop](https://github.com/Manas-Jain-24/Swasthya-Loop)
- **Team Name:** M&M
- **Team Lead:** Manas Jain
