# 2-Minute Hackathon Demo Script — SwasthyaLoop

**Focus**: 30-day post-discharge monitoring for cardiac patients after a new or adjusted BP medication.

---

## Quick Reference Summary Table

| Time | Screen | Key Actions | Talking Points |
| :--- | :--- | :--- | :--- |
| **0:00 – 0:25** | **Landing / Boundary** | Open `/doctor`. Point to **Pathway Boundary** card at top. | *"Judges, SwasthyaLoop is not an unconstrained chronic-care app, nor do we claim prior care failed. We focus strictly on the vulnerable 30-day post-discharge window for cardiac patients with newly changed BP medications."* |
| **0:25 – 0:55** | **Coordinator Hero** | Select **Rajesh Sharma (Day 12 of 30)**. View BP trajectory chart. | *"Here is Rajesh Sharma on Day 12. Notice the hero 3-reading trajectory: 138/86 on Day 6, 148/90 on Day 9, and 162/96 on Day 11. Rule BP_TREND_UP_3 triggers with full evidence traceability. Operational task alerts are demoted so clinicians focus only on true physiological risks."* |
| **0:55 – 1:25** | **Safe AI Handoff** | Examine **AI Clinical Handoff** & **Validation Supervisor**. | *"Our AI does not diagnose, prescribe, or titrate medications. Its sole role is generating a concise clinician handoff from verified records. The Validation Supervisor panel proves every figure is source-backed and all forbidden clinical categories are blocked."* |
| **1:25 – 1:45** | **Action Buttons** | Highlight the 3 action buttons. | *"The care coordinator has three clear protocol actions: Request repeat verified reading, Document outreach, or Escalate for clinician review. The loop is closed safely."* |
| **1:45 – 2:00** | **Safe OCR Verification** | Switch to `/patient`. Test OCR extraction failure. | *"Finally, our telemetry intake is fail-safe: if an OCR scan is unreadable or offline, we never fabricate readings. It clearly states 'Extraction unavailable' and requires manual confirmation before entering the clinical record."* |

---

## Detailed Step-by-Step Script

### 1. The Pathway Boundary (0:00 – 0:25)
- **URL**: `http://127.0.0.1:8001/doctor`
- **What to show**: The Pathway Boundary card at the top of the coordinator dashboard.
- **Narrative**:
  > *"Rather than broad, noisy chronic-care monitoring, SwasthyaLoop addresses one specific, dangerous gap: the 30-day post-discharge window after a cardiac patient starts a new or adjusted blood pressure medicine. Our boundary is transparent: we enroll patients with a medication change for 30 days, track verified trajectories, and exit them upon clinical stability. We explicitly exclude acute emergencies and unadjusted stable patients."*

### 2. Hero Rising BP Trajectory (0:25 – 0:55)
- **URL**: `http://127.0.0.1:8001/doctor`
- **What to show**: Selected patient Rajesh Sharma, Day 12 of 30 label, and the BP chart.
- **Narrative**:
  > *"Look at Rajesh Sharma, Day 12 post-discharge. Instead of reacting to an isolated reading, our deterministic engine tracks consecutive verified readings: 138/86 rising to 148/90 and then 162/96 across six days. Rule BP_TREND_UP_3 flags this immediately with full evidence provenance. Meanwhile, overdue daily reminders are demoted to operational alerts, preventing alert fatigue."*

### 3. Safe AI Clinical Handoff & Validation Supervisor (0:55 – 1:25)
- **URL**: `http://127.0.0.1:8001/doctor` (Right column)
- **What to show**: AI Clinical Handoff box and the compact Validation Supervisor panel.
- **Narrative**:
  > *"The role of AI in SwasthyaLoop is strictly constrained: generating a concise clinician handoff from verified database records. It never diagnoses, never suggests a dose titration, and never writes a prescription. Notice the Validation Supervisor panel directly beneath: it verifies that all numbers match database records, confirms rule BP_TREND_UP_3, checks that forbidden categories are blocked, and certifies status as VERIFIED."*

### 4. Coordinator Protocol Actions (1:25 – 1:45)
- **URL**: `http://127.0.0.1:8001/doctor`
- **What to show**: The three primary action buttons:
  - `Request repeat verified reading`
  - `Document outreach`
  - `Escalate for clinician review`
- **Narrative**:
  > *"The coordinator doesn't need to guess next steps. With three clear buttons, they can request a verified re-check, log phone outreach, or escalate the patient for a scheduled teleconsultation review with the cardiology team."*

### 5. Safe Telemetry & Fail-Safe OCR (1:45 – 2:00)
- **URL**: `http://127.0.0.1:8001/patient`
- **What to show**: Vital source dropdown and the device photo scan with unreadable/failed input.
- **Narrative**:
  > *"On the patient side, readings specify their source—whether a Bluetooth cuff, Caregiver/ASHA assistance, or a device photo. Crucially, if an image is blurred or OCR fails, the system never fabricates demo numbers. It reports 'Extraction unavailable' and prevents unverified entries from ever entering clinical triage."*
