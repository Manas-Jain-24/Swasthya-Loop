"""
SwasthyaLoop — 30-Day Post-Discharge Cardiac & BP Medication Change Pathway
Narrow clinical pathway focusing strictly on:
"30-day post-discharge monitoring for cardiac patients after a new or adjusted BP medication."
"""

from typing import Dict, Any, List

PATHWAY_BOUNDARY = {
    "title": "30-Day Post-Discharge Cardiac Telemetry Boundary",
    "enroll": "Cardiac-discharge patients with a new or adjusted BP medication, monitored for 30 days.",
    "monitor": "Verified BP trajectory and symptom check-ins.",
    "exit": "Stable trajectory or scheduled clinician review at Day 30.",
    "do_not_enroll": "Emergency symptoms (dial 108), stable patients without medication changes, or patients unable to obtain supported measurements."
}

COHORT_REGISTRY: Dict[str, Dict[str, Any]] = {
    "patient-003": {
        "cohort_name": "30-day post-discharge monitoring for cardiac patients after a new or adjusted BP medication",
        "cohort_badge": "Day 12 of 30",
        "badge_color": "rose",
        "indication": "Post-Discharge Cardiac Care · Adjusted BP Medication (Amlodipine 5mg OD)",
        "enrollment_day": 12,
        "duration_days": 30,
        "exit_milestone": "Stable trajectory or scheduled clinician review",
        "telemetry_source": "Device photo, patient-confirmed & Caregiver/ASHA-assisted entry",
        "active_rx": ["Tab. Amlodipine 5mg OD", "Tab. Atorvastatin 40mg OD", "Tab. Aspirin 75mg OD"],
        "open_clinical_question": "Hemodynamic trajectory verification after discharge BP medication change without precipitating uncontrolled surge."
    },
    "patient-001": {
        "cohort_name": "30-day post-discharge monitoring for cardiac patients after a new or adjusted BP medication",
        "cohort_badge": "Day 8 of 30",
        "badge_color": "emerald",
        "indication": "Post-ACS Discharge · New Antihypertensive Initiation (Telmisartan 40mg OD)",
        "enrollment_day": 8,
        "duration_days": 30,
        "exit_milestone": "Stable trajectory or scheduled clinician review",
        "telemetry_source": "Device photo, patient-confirmed",
        "active_rx": ["Tab. Telmisartan 40mg OD", "Tab. Aspirin 75mg OD"],
        "open_clinical_question": "Hemodynamic response and postural stability following new antihypertensive start."
    },
    "patient-002": {
        "cohort_name": "30-day post-discharge monitoring for cardiac patients after a new or adjusted BP medication",
        "cohort_badge": "Day 15 of 30",
        "badge_color": "amber",
        "indication": "Post-Discharge Cardiac & Renal Follow-Up (Baseline eGFR 42 mL/min)",
        "enrollment_day": 15,
        "duration_days": 30,
        "exit_milestone": "Stable trajectory or scheduled clinician review",
        "telemetry_source": "Caregiver/ASHA-assisted entry",
        "active_rx": ["Tab. Metformin 500mg BID", "Tab. Telmisartan 40mg OD"],
        "open_clinical_question": "Renal safety and glycemic monitoring alongside BP medication adjustment."
    },
    "patient-004": {
        "cohort_name": "30-day post-discharge monitoring for cardiac patients after a new or adjusted BP medication",
        "cohort_badge": "Day 6 of 30",
        "badge_color": "blue",
        "indication": "Post-Crisis Cardiac & Glycemic Discharge",
        "enrollment_day": 6,
        "duration_days": 30,
        "exit_milestone": "Stable trajectory or scheduled clinician review",
        "telemetry_source": "Manual patient entry",
        "active_rx": ["Insulin Glargine 14 Units Bedtime", "Tab. Metformin 1000mg ER"],
        "open_clinical_question": "Dual metabolic and hemodynamic stability post-discharge."
    }
}

DECLINATION_PROTOCOL: List[Dict[str, Any]] = [
    {
        "category": "Stable Patients Without Treatment Change",
        "decision": "DO NOT ENROLL",
        "rationale": "Patients on unchanged medications with stable vitals require routine primary care checkups, not intensive 30-day remote telemetry.",
        "alternative_care": "Schedule routine semi-annual follow-up at primary health centre."
    },
    {
        "category": "Acute Emergency Symptoms at Intake",
        "decision": "DO NOT ENROLL / DIVERT",
        "rationale": "Patients exhibiting chest pain, severe dyspnea, or syncope require immediate emergency facility evaluation, not outpatient remote monitoring.",
        "alternative_care": "Immediate diversion to emergency medical services (EMS 108 / nearest cardiac casualty)."
    },
    {
        "category": "Unable to Obtain Supported Measurements",
        "decision": "DO NOT ENROLL",
        "rationale": "Patients lacking access to verified digital monitors, ASHA sub-centres, or designated caregivers cannot produce auditable telemetry.",
        "alternative_care": "Referral to in-person public sub-centre clinic for direct nursing vitals check."
    },
    {
        "category": "Non-Cardiac Routine Outpatients",
        "decision": "DO NOT ENROLL",
        "rationale": "General outpatients without recent hospital discharge or cardiovascular therapy adjustments fall outside this acute 30-day monitoring pathway.",
        "alternative_care": "Standard outpatient care and lifestyle guidance."
    }
]

TELEMETRY_MODES_ARCH: List[Dict[str, Any]] = [
    {
        "tier": "Mode 1 (Device Photo)",
        "name": "Device photo, patient-confirmed",
        "hardware_needed": "Any standard non-connected digital monitor (Omron, Dr. Morepen, etc.).",
        "protocol": "Patient takes photo of monitor display; reading confirmed manually or via OCR before submission."
    },
    {
        "tier": "Mode 2 (Community / Assisted)",
        "name": "Caregiver/ASHA-assisted entry & Pharmacy/sub-centre entry",
        "hardware_needed": "Sub-centre or pharmacy digital monitor.",
        "protocol": "ASHA worker, pharmacist, or caregiver verifies and logs the measurement."
    },
    {
        "tier": "Mode 3 (Direct / Connected)",
        "name": "Bluetooth cuff or Manual patient entry",
        "hardware_needed": "Bluetooth cuff or verified home monitor.",
        "protocol": "Direct wireless telemetry sync or manual patient log with technique confirmation."
    }
]

def get_patient_cohort_info(patient_id: str) -> Dict[str, Any]:
    if patient_id in COHORT_REGISTRY:
        return COHORT_REGISTRY[patient_id]
    return {
        "cohort_name": "30-day post-discharge monitoring for cardiac patients after a new or adjusted BP medication",
        "cohort_badge": "Day 12 of 30",
        "badge_color": "blue",
        "indication": "30-Day Post-Discharge Cardiac Telemetry Protocol",
        "enrollment_day": 12,
        "duration_days": 30,
        "exit_milestone": "Stable trajectory or scheduled clinician review",
        "telemetry_source": "Device photo, patient-confirmed",
        "active_rx": ["Guideline-Directed Medical Therapy"],
        "open_clinical_question": "Hemodynamic trajectory verification after discharge medication change."
    }
