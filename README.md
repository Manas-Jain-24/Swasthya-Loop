# SwasthyaLoop — 30-Day Post-Discharge Cardiac & BP Medication Monitoring Platform

> **Safe, Protocol-Grounded Follow-Up for Post-Discharge Cardiac Patients**  
> *Deterministic Escalation Rules • Traceable Telemetry • Safe AI Clinician Handoff • FHIR-Ready Prototype*

[![Test Suite](https://img.shields.io/badge/Pytest-16%20Passed%20(100%25)-emerald?style=for-the-badge&logo=pytest)](backend/tests/test_api.py)
[![Architecture](https://img.shields.io/badge/Architecture-FastAPI%20%2B%20SQLite-blue?style=for-the-badge)](backend/app/main.py)
[![AI Engine](https://img.shields.io/badge/Clinical%20AI-Gemini%203.8%20Flash%20(Constrained)-blueviolet?style=for-the-badge)](backend/app/services/ai_copilot.py)
[![Standards](https://img.shields.io/badge/Standards-FHIR--Ready%20%2F%20ABDM--Aligned%20Prototype-teal?style=for-the-badge)](docs/architecture.md)

---

## 🎯 Clinical Scope & Pathway Boundary

SwasthyaLoop is purposefully designed for a **narrow, high-risk 30-day transitional window**:
> **"30-day post-discharge monitoring for cardiac patients after a new or adjusted BP medication."**

It does **not** attempt universal chronic care or unconstrained home surveillance. It does **not** claim prior clinical care failed, does **not** replace physician judgment, and does **not** claim every discharged patient needs digital monitoring.

### Pathway Boundary Matrix
| Boundary Phase | Criteria & Protocols |
| :--- | :--- |
| **Enroll** | Cardiac-discharge patients with a newly initiated or adjusted blood pressure medication, monitored for exactly **30 days**. |
| **Monitor** | Verified blood pressure trajectories, adherence tracking, and reported symptom checkpoints. |
| **Exit** | Stable verified hemodynamic trajectory across 30 days, or transition to a scheduled in-person clinician review. |
| **Do Not Enroll** | Patients with acute emergency symptoms (referred immediately to emergency services), hemodynamically stable patients without treatment changes, or patients unable to obtain supported measurements. |

---

## ⚡ Hero Clinical Feature: Deterministic BP Escalation Trend (`BP_TREND_UP_3`)

Rather than alarming on isolated, noisy single measurements, SwasthyaLoop tracks longitudinal hemodynamic trajectories across multiple verified readings:

- **Escalation Trajectory**: `138/86 mmHg` (Day 6) → `148/90 mmHg` (Day 9) → `162/96 mmHg` (Day 11)
- **Deterministic Rule**: Rule ID `BP_TREND_UP_3` triggers when systolic pressure increases across three consecutive verified readings with the latest $\ge$ 160 mmHg.
- **Traceable Clinical Evidence**: Displays exact reading dates, values, and audit-logged evidence sources.
- **Protocol Action**: *"Coordinator outreach and clinician review"*.
- **Operational Demotion**: Overdue daily tasks and missed readings are classified as **Operational Reminders** (routine priority), reserving clinical triage capacity for verified physiological risks.

---

## 🛡️ Safe Clinical AI: Clinician Handoff & Validation Supervisor

SwasthyaLoop uses Generative AI (Google Gemini) under strict clinical guardrails. Its primary role is **generating concise clinician handoffs from verified database records**.

### Example Output:
> *"Day 12 after discharge. Three verified BP readings increased from 138/86 to 162/96 across six days. No emergency symptoms recorded. This meets BP_TREND_UP_3 review criteria. Coordinator outreach and clinician review are recommended."*

### Zero-Tolerance Guardrails:
- ❌ **No autonomous diagnoses**
- ❌ **No medication or dose titration recommendations**
- ❌ **No prescription generation**
- ❌ **No simulated lab values presented as real data**

### Compact Validation Supervisor Panel:
Under every AI synthesis, a live **Validation Supervisor** audits the text:
- **Source Readings Used**: Verified database records (e.g., `138/86`, `148/90`, `162/96 mmHg`).
- **Rule ID Used**: Verified deterministic rule linkage (`BP_TREND_UP_3`).
- **Claim Check**: Deterministic regex matching verifies that every numerical claim in the summary directly corresponds to an underlying clinical record.
- **Blocked Categories**: Scans for and blocks forbidden medical categories (`diagnosis`, `prescription`, `dosage change`, `titration`).
- **Audit Status**: Clear verification badge (`VERIFIED`, `BLOCKED`, or `MANUAL REVIEW NEEDED`).

---

## 📸 Safe Telemetry Ingestion & OCR Policy

To ensure garbage data does not contaminate clinical triage:
1. **No Simulated Fallbacks**: If an image scan fails, has low resolution, or the API is unavailable, the OCR endpoint **never fabricates fake BP or glucose values**. It returns:
   > *"Extraction unavailable — enter or confirm reading manually"*
2. **Explicit Verification Gate**: Unconfirmed OCR scans cannot create verified clinical records.
3. **Audited Data Sources**:
   - `Device photo, patient-confirmed`
   - `Bluetooth cuff`
   - `Caregiver/ASHA-assisted entry`
   - `Pharmacy/sub-centre entry`
   - `Manual patient entry`

---

## 🚀 Quickstart: Running Locally

### 1. Launch FastAPI Backend
```powershell
# From the repository root
& ".venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Access the application portals:
- **Landing Gateway**: [http://127.0.0.1:8001](http://127.0.0.1:8001)
- **Doctor / Coordinator Command Center**: [http://127.0.0.1:8001/doctor](http://127.0.0.1:8001/doctor)
- **Patient Companion Portal**: [http://127.0.0.1:8001/patient](http://127.0.0.1:8001/patient)

### 2. Execute Automated Test Suite (16/16 Passed)
```powershell
& ".venv\Scripts\python.exe" -m pytest backend/tests -v
```
All 16 test cases validate deterministic rules, AI guardrails, safe OCR, and clinical cohort metadata.

---

## ⏱️ 2-Minute Judge Evaluation Demo Flow

1. **Step 1: Pathway Boundary (0:00 - 0:25)**
   - Open [http://127.0.0.1:8001/doctor](http://127.0.0.1:8001/doctor).
   - Point out the **Pathway Boundary** card: strictly 30 days post-discharge cardiac follow-up with changed BP medication; explicit exclusion of emergency and stable unadjusted patients.
2. **Step 2: Hero Patient & Rising BP Trajectory (0:25 - 0:55)**
   - View demo patient **Rajesh Sharma (Day 12 of 30)** at the top of the coordinator screen.
   - Highlight the **3-reading escalation trajectory**: `138/86` → `148/90` → `162/96 mmHg` across 6 days.
   - Point out the priority alert banner: Rule ID `BP_TREND_UP_3`, verified dates, telemetry evidence source, and protocol action *"Coordinator outreach and clinician review"*.
3. **Step 3: Safe AI Handoff & Validation Supervisor (0:55 - 1:25)**
   - Inspect the **AI Clinical Handoff**: concise, factual synthesis referencing exact dates and readings without any prescriptions or dosage instructions.
   - Review the **Validation Supervisor Panel**: shows verified source readings, `BP_TREND_UP_3` rule ID, claim check passed, blocked categories (diagnosis/prescription/titration), and status: `VERIFIED`.
4. **Step 4: Coordinator Action Buttons (1:25 - 1:45)**
   - Demonstrate the three actionable clinical controls:
     - `Request repeat verified reading`
     - `Document outreach`
     - `Escalate for clinician review`
5. **Step 5: Safe OCR Verification (1:45 - 2:00)**
   - Navigate to [http://127.0.0.1:8001/patient](http://127.0.0.1:8001/patient).
   - Open OCR camera scan on an unreadable or blank image: observe that the system returns *"Extraction unavailable — enter or confirm reading manually"* without fabricating any measurements.

---

## 📋 Current Prototype Limitations

1. **Future Integration**: ABDM milestone integrations (M1/M2/M3) and FHIR R4 server exports are architected as data models and mock endpoints; production deployment requires official ABDM sandbox bridge certification.
2. **Connectivity Fallback**: Bluetooth cuff telemetry currently uses simulated Web Bluetooth API events in browser prototypes rather than native mobile OS drivers.
3. **Offline Ingestion**: ASHA-assisted entry currently caches in local browser storage; background sync requires full Service Worker PWA deployment.
