# SwasthyaLoop — Architecture Documentation

SwasthyaLoop is a protocol-grounded, closed-loop clinical monitoring and triage platform for a narrow 30-day post-discharge cardiac and BP medication pathway.

## System Architecture

```text
+-------------------------------------------------------------------------+
|                           PATIENT & CLINICIAN UI                        |
|  - Patient Companion: Telemetry Ingestion (Photo, Bluetooth, ASHA)      |
|  - Coordinator Command Center: Day 12 Hero View, Trajectory & Triage    |
|  - Pathway Boundary Card & Strict Intake Verification                   |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                            FASTAPI BACKEND                              |
|  - Reading Ingestion with Physiological Range Checks                    |
|  - Deterministic Safety Rules Engine (ICMR / ACC/AHA Grounded)          |
|    * Hero Rule: BP_TREND_UP_3 (138/86 -> 148/90 -> 162/96 mmHg)        |
|    * Operational Reminder Demotion for Missed Tasks                     |
|  - Constrained AI Copilot: Clinician Handoffs (Gemini 3.8 Flash)        |
|  - Validation Supervisor: Claim Verification & Blocked Categories Guard |
|  - Safe OCR Service: Fail-Safe Handling (Zero Measurement Fabrication)  |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                            SQLITE DATA STORE                            |
|  - Patients (Discharge Date, Assigned Pathway, Telemetry Records)       |
|  - Readings (Systolic, Diastolic, Verified Data Source, Audit Trail)    |
|  - FollowupFlags (Rule ID, Audit Reason, Evidence Values, Action)       |
|  - CareTasks (Operational Reminders, Schedule Milestones)               |
+-------------------------------------------------------------------------+
```

## Architectural Tenets

1. **Deterministic Clinical Core**: Clinical risk calculation is 100% deterministic and rule-based. AI never makes triage decisions.
2. **Safe Generative AI Role**: AI is strictly limited to synthesizing verified records into a concise clinician handoff.
3. **Validation Supervisor Guardrail**: AI outputs pass through a deterministic validation supervisor verifying source figures and blocking forbidden clinical categories (diagnosis, prescription, dosage change).
4. **Data Integrity & Traceability**: Telemetry records maintain audited source attribution (`Device photo, patient-confirmed`, `Bluetooth cuff`, `Caregiver/ASHA-assisted entry`, `Pharmacy/sub-centre entry`, `Manual patient entry`).
5. **FHIR-Ready / ABDM-Aligned Prototype**: Standardized resource mappings for seamless clinical adoption without deceptive certification claims.
