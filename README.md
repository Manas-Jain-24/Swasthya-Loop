# SwasthyaLoop (स्वास्थ्य लूप)

> **AI-Assisted Closed-Loop Post-Discharge Monitoring Platform**  
> *Deterministic Escalation Rules • Source-Verified Telemetry • Two-Tier Validation Supervisor • FHIR-Ready Prototype*

[![Test Suite](https://img.shields.io/badge/Pytest-19%20Passed%20(100%25)-emerald?style=for-the-badge&logo=pytest)](backend/tests/test_api.py)
[![Architecture](https://img.shields.io/badge/Architecture-FastAPI%20%2B%20SQLite%20%2B%20TailwindCSS-blue?style=for-the-badge)](backend/app/main.py)
[![Clinical AI](https://img.shields.io/badge/Clinical%20AI-Gemini%203.8%20Flash%20(Constrained)-blueviolet?style=for-the-badge)](backend/app/services/ai_copilot.py)
[![Safety Layer](https://img.shields.io/badge/Validation%20Supervisor-Deterministic%20Audit%20Matrix-success?style=for-the-badge)](backend/app/services/ai_copilot.py)
[![Standards](https://img.shields.io/badge/Standards-FHIR--Ready%20%2F%20ABDM--Aligned%20Prototype-teal?style=for-the-badge)](docs/architecture.md)

---

## 🎯 Clinical Scope & Pathway Boundary

SwasthyaLoop is purposefully engineered for a **narrow, high-risk 30-day post-discharge transitional care window**:

> **"30-day post-discharge monitoring for cardiac patients after a new or adjusted blood pressure medication."**

It does **not** attempt unconstrained universal chronic care, does **not** claim prior inpatient care failed, does **not** replace licensed clinician judgment, and does **not** claim every discharged patient needs digital surveillance.

### Direct Response to Mid-Evaluation Jury Feedback:
- **Jury 1 (Relevance after discharge)**: Starting or titrating cardiovascular medications (ACE-inhibitors, ARBs, CCBs) requires 7–14 days to stabilize hemodynamically. The 30-day post-discharge period is the clinical window where medication failure, rebound hypertension, and acute readmissions occur. SwasthyaLoop bridges this gap between hospital discharge and the scheduled 30-day OPD follow-up.
- **Jury 2 (Vague problem statement)**: Narrowed strictly from broad chronic care to a high-leverage clinical cohort: post-discharge cardiac patients with adjusted BP medications.
- **Jury 3 (AI hallucination & prescribing risks)**: Eliminated all prescribing, dosage adjustments, and diagnostic commands. Introduced a deterministic **Two-Tier Validation Supervisor** that audits AI outputs against database ground truth.

### Pathway Boundary Matrix
| Boundary Phase | Criteria & Protocols |
| :--- | :--- |
| **Enroll** | Cardiac-discharge patients with newly initiated or adjusted BP medications, monitored for **exactly 30 days**. |
| **Monitor** | Source-verified blood pressure trajectories, adherence tracking, and structured symptom checkpoints. |
| **Exit** | Stable verified hemodynamic trajectory across 30 days, or transition to a scheduled in-person clinician review. |
| **Do Not Enroll** | Patients with acute emergency symptoms (referred immediately to 108/112), hemodynamically stable patients without treatment changes, or patients unable to obtain supported measurements. |

---

## ⚡ Hero Clinical Feature: Deterministic BP Escalation Trend (`BP_TREND_UP_3`)

Rather than sounding alarms on noisy, isolated single measurements, SwasthyaLoop tracks **longitudinal hemodynamic trajectories across verified measurements**:

- **Escalation Trajectory**: `138/86 mmHg` (Day 6) → `148/90 mmHg` (Day 9) → `162/96 mmHg` (Day 11).
- **Deterministic Rule**: Rule ID `BP_TREND_UP_3` triggers only when systolic pressure increases across **three consecutive verified readings** with the latest reading $\ge$ 160 mmHg.
- **Strict Source Verification Gate**:
  Only allowed verified sources can influence trend calculations:
  - `Device photo, patient-confirmed`
  - `Bluetooth cuff`
  - `Caregiver/ASHA-assisted entry`
  - `Pharmacy/sub-centre entry`
  *(Unverified or manual patient entries are flagged for verification and can never trigger a false-positive escalation alert).*
- **Protocol Action**: *"Coordinator outreach and clinician review"*.
- **Operational Demotion**: Overdue routine reminders and missed check-ins are categorized as **Operational Reminders** (routine priority), preserving clinical triage capacity for verified physiological risks.

---

## 🛡️ Safe Clinical AI: Clinician Handoff & Truthful Validation Supervisor

SwasthyaLoop uses Generative AI (Google Gemini) under deterministic clinical guardrails. Its sole role is **generating concise clinician handoffs grounded strictly in verified database vitals**.

### Example AI Clinician Handoff:
> *"Day 12 after discharge. Three verified BP readings increased from 138/86 to 162/96 across six days. No emergency symptoms recorded. This meets BP_TREND_UP_3 review criteria. Coordinator outreach and clinician review are recommended."*

### Zero-Tolerance Guardrails:
- ❌ **No autonomous diagnoses**
- ❌ **No medication or dose titration recommendations**
- ❌ **No prescription generation or prescription modification**
- ❌ **No fabricated or simulated clinical metrics**

### Live Two-Tier Validation Supervisor UI:
Under every AI synthesis, a live **Validation Supervisor** audits the text in real time:
- **Dynamic Status Indication**:
  - 🟢 **`VERIFIED`**: All figures match database records; rule criteria confirmed; prohibited categories clean.
  - 🔴 **`BLOCKED`**: Prohibited medical advice intercepted (diagnosis, prescription, dosage change).
  - 🟡 **`MANUAL REVIEW NEEDED`**: Fewer than 3 verified readings available; manual review required.
- **Truthful Audit Log**: Displays exact `source_readings_used` with timestamps and verified device sources.
- **Deterministic Claim Match**: Regex verification ensures every single number in the summary corresponds to an underlying clinical record.
- **Blocked Categories**: Actively filters out all prescribing and dosing terminology (`titrate`, `dose`, `prescribe`, `increase/decrease`).

---

## 👨‍⚕️ Clinician & Coordinator Workflow: Safe Actions Only

All dormant prescription interfaces, Rx adjustment modals, and dosage titration calculators have been completely removed from the platform. Coordinator and physician actions are restricted strictly to:

1. **Request repeat verified reading** — Dispatches an urgent prompt to patient companion/ASHA to submit a photo or Bluetooth-verified reading.
2. **Document outreach** — Logs telephone contact, adherence verification, or symptom clarification.
3. **Escalate for clinician review** — Queues high-priority clinical review for the attending physician.
4. **Resolve operational reminder** — Clears administrative reminders once patient logs routine telemetry.

---

## 📸 Safe Telemetry Ingestion & Zero-Fabrication OCR Policy

To guarantee low-quality data never contaminates clinical triage:
1. **Zero Fabrication**: If an image scan is blurry, poorly lit, or fails OCR parsing, the system **never guesses or fabricates measurements**. It cleanly returns:
   > *"Extraction unavailable — enter or confirm reading manually"*
2. **Explicit Verification Gate**: Unconfirmed OCR scans remain in an unverified state until confirmed by patient photo review or clinical staff.
3. **Audited Data Sources**:
   - `Device photo, patient-confirmed`
   - `Bluetooth cuff`
   - `Caregiver/ASHA-assisted entry`
   - `Pharmacy/sub-centre entry`
   - `Manual patient entry` (flagged for verification)

---

## 🏥 Neutral Prototype Follow-Up Plan

The patient companion portal provides a structured post-discharge follow-up review note using neutral prototype branding:
- **Header**: `SwasthyaLoop — 30-Day Follow-Up Plan`
- **Sub-label**: `Post-Discharge Cardiac Care Coordination • ABDM-aligned data model`
- **Identity**: `Prototype · simulated/de-identified demo data`
- **Sign-off**: `Attending Care Team · Tele-Coordination Unit`
- *No real hospital or individual physician identity is implied.*

---

## 📁 Repository Structure

```
swasthya-loop/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI application entrypoint & routing
│   │   ├── database.py              # SQLite database configuration & session engine
│   │   ├── models.py                # SQLAlchemy models (Patient, Reading, Flag, CareTask, CarePlan)
│   │   ├── schemas.py               # Pydantic schemas with validation rules
│   │   ├── routers/
│   │   │   └── api.py               # REST API endpoints (triage, readings, AI copilot, OCR)
│   │   ├── services/
│   │   │   ├── ai_copilot.py        # Clinician handoff engine & Tier-2 Validation Supervisor
│   │   │   ├── rules.py             # Deterministic clinical rule engine (BP_TREND_UP_3)
│   │   │   ├── clinical_cohorts.py  # 30-day post-discharge cohort boundaries & milestones
│   │   │   ├── summaries.py         # Grounded plain-language summary generation
│   │   │   └── llm_provider.py      # Constrained Gemini 3.8 Flash client
│   │   ├── seed/
│   │   │   └── demo_data.py         # Deterministic seed data (Rajesh Sharma hero cohort)
│   │   └── static/
│   │       ├── index.html           # Unified landing portal & pathway explainer
│   │       ├── doctor.html          # Doctor / Care Coordinator Command Center
│   │       └── patient.html         # Patient Companion Portal (Vitals log, 30-day plan)
│   └── tests/
│       └── test_api.py              # 19 automated tests (Rules, AI safety, OCR, cohorts)
├── docs/
│   └── architecture.md              # Technical specifications & FHIR/ABDM data models
├── pytest.ini                       # Test configuration & pythonpath settings
├── requirements.txt                 # Backend dependencies
└── README.md                        # Project documentation & evaluation guide
```

---

## 🚀 Quickstart: Running Locally

### 1. Prerequisites
- Python 3.11+
- Git

### 2. Setup Virtual Environment
```powershell
# Clone the repository
git clone https://github.com/Manas-Jain-24/Swasthya-Loop.git
cd Swasthya-Loop

# Create and activate virtual environment (if not already done)
python -m venv .venv
.\.venv\Scripts\activate  # Windows (or: source .venv/bin/activate on Unix)

# Install dependencies
pip install -r requirements.txt
```

### 3. Launch FastAPI Backend
```powershell
# From repository root
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8001
```

Access the application portals:
- **Landing Gateway**: [http://127.0.0.1:8001](http://127.0.0.1:8001)
- **Doctor / Coordinator Command Center**: [http://127.0.0.1:8001/doctor](http://127.0.0.1:8001/doctor)
- **Patient Companion Portal**: [http://127.0.0.1:8001/patient](http://127.0.0.1:8001/patient)
- **Interactive OpenAPI Docs**: [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)

### 4. Execute Automated Test Suite (19/19 Passed)
```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests -v
```
All 19 test cases validate deterministic rules, AI guardrails, unverified reading isolation, zero-fabrication OCR, and clinical cohort metadata.

---

## ⏱️ 2-Minute Judge Evaluation Demo Flow

1. **Step 1: Pathway Boundary Card (0:00 - 0:25)**
   - Open [http://127.0.0.1:8001/doctor](http://127.0.0.1:8001/doctor).
   - Point out the **Pathway Boundary** card: strictly 30 days post-discharge cardiac follow-up with changed BP medication; explicit exclusion of emergency and stable unadjusted patients.
2. **Step 2: Hero Patient & Rising BP Trajectory (0:25 - 0:55)**
   - View demo patient **Rajesh Sharma (Day 12 of 30)** at the top of the triage queue.
   - Highlight the **3-reading escalation trajectory**: `138/86` → `148/90` → `162/96 mmHg` across 6 days.
   - Point out the priority alert banner: Rule ID `BP_TREND_UP_3`, verified dates, telemetry evidence source, and protocol action *"Coordinator outreach and clinician review"*.
3. **Step 3: Safe AI Handoff & Validation Supervisor (0:55 - 1:25)**
   - Inspect the **AI Clinical Handoff**: concise, factual synthesis referencing exact dates and readings without any prescriptions or dosage instructions.
   - Review the **Validation Supervisor Panel**: shows verified source readings, `BP_TREND_UP_3` rule ID, claim check passed, blocked categories (diagnosis/prescription/titration), and dynamic status `VERIFIED`.
   - Click the badge to open the **Live Audit Matrix**: verify ground-truth readings match database records with zero hallucination risk.
4. **Step 4: Safe Coordinator Action Controls (1:25 - 1:45)**
   - Demonstrate the actionable clinical controls:
     - `Request repeat verified reading`
     - `Document outreach`
     - `Escalate for clinician review`
   - Notice the complete absence of prescription writing, dosage change buttons, or titration calculators.
5. **Step 5: Safe OCR Verification & Patient Companion (1:45 - 2:00)**
   - Navigate to [http://127.0.0.1:8001/patient](http://127.0.0.1:8001/patient).
   - Test the OCR scanner on an unreadable image: observe that the system returns *"Extraction unavailable — enter or confirm reading manually"* without fabricating any measurements.
   - Open the **30-Day Follow-Up Plan**: review the sanitized, de-identified prototype care coordination note.

---

## 📋 Hackathon Prototype Disclaimers

1. **Clinical Decision Support Only**: SwasthyaLoop is an investigational software prototype developed for the TELEMEDICINE / Digital Health Hackathon. It is not an FDA-cleared or CDSCO-approved medical device and does not provide autonomous clinical diagnoses or treatment modifications.
2. **De-Identified Data**: All patient names, UHIDs, and medical readings in demo profiles are synthetic and de-identified.
3. **ABDM Sandbox Architecture**: Integration endpoints follow the National Health Authority (NHA) Ayushman Bharat Digital Mission (ABDM) and FHIR R4 schema specifications as reference architecture prototypes.
