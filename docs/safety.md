# Clinical AI Safety & Boundary Policy — SwasthyaLoop

## 1. Focused Pathway Boundary
SwasthyaLoop is strictly constrained to **30-day post-discharge monitoring for cardiac patients after a new or adjusted BP medication**.
- **Enroll**: Cardiac-discharge patients with an altered blood pressure regimen.
- **Monitor**: Verified BP trajectories and reported symptom checkpoints.
- **Exit**: Documented hemodynamic stability or scheduled clinician review.
- **Do Not Enroll**: Acute emergency symptoms (referred to local emergency departments), stable patients without medication changes, or patients unable to obtain verified measurements.

## 2. Zero Clinical Hallucination & Non-Prescribing Policy
SwasthyaLoop enforces absolute restrictions on generative AI:
- **No Autonomous Diagnosis**: The platform identifies trajectory patterns against deterministic rules; it does not issue medical diagnoses.
- **No Prescriptions or Titration**: The platform strictly prohibits AI from generating prescriptions, suggesting dose changes, or directing medication titration. All therapeutic modifications remain exclusively with the licensed treating clinician.
- **No Simulated Measurements**: The system never manufactures fake vitals or lab values. If an OCR scan fails or is unreadable, it returns *"Extraction unavailable — enter or confirm reading manually"*.

## 3. The Validation Supervisor
Every AI synthesis is audited before display:
- **Source Grounding**: Numerical claims are checked against verified database records.
- **Rule Verification**: Text is checked for correspondence with deterministic rule IDs (e.g., `BP_TREND_UP_3`).
- **Forbidden Categories Filter**: Explicitly blocks claims in the categories of diagnosis, prescription, and dosage change.
- **Status Audit**: Outputs a clear audit status: `VERIFIED`, `BLOCKED`, or `MANUAL REVIEW NEEDED`.

## 4. Telemetry Source Verification
Clinical triage flags are triggered only by verified data sources:
- `Device photo, patient-confirmed`
- `Bluetooth cuff`
- `Caregiver/ASHA-assisted entry`
- `Pharmacy/sub-centre entry`
- `Manual patient entry`
