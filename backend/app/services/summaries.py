from typing import List, Dict, Any
from sqlalchemy.orm import Session
from ..models import Patient, Reading, CareTask, FollowupFlag, CarePlan
from .llm_provider import generate_plain_language_summary

SAFETY_DISCLAIMER = (
    "SwasthyaLoop Prototype Disclaimer: This summary is for care-coordination and follow-up reference only. "
    "It does not provide medical diagnosis, treatment changes, or replace clinical consultations."
)

def build_patient_facts(db: Session, patient_id: str) -> List[str]:
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        return []

    facts = []
    conditions_str = ", ".join(patient.conditions) if patient.conditions else "monitored condition"
    facts.append(f"Care plan covers: {conditions_str}.")

    # Care Plan appointment
    care_plan = db.query(CarePlan).filter(CarePlan.patient_id == patient_id).first()
    if care_plan and care_plan.next_appointment:
        facts.append(f"Next scheduled healthcare appointment is {care_plan.next_appointment}.")

    # Readings summary
    readings = db.query(Reading).filter(Reading.patient_id == patient_id).order_by(Reading.recorded_at.desc()).all()
    if readings:
        latest = readings[0]
        facts.append(f"Total readings on file: {len(readings)}.")
        if latest.type == "blood_pressure":
            facts.append(f"Most recent reading: BP {int(latest.systolic_mmhg)}/{int(latest.diastolic_mmhg)} mmHg on {latest.recorded_at[:10]}.")
        elif latest.type == "blood_glucose":
            facts.append(f"Most recent reading: Glucose {int(latest.value)} {latest.unit} ({latest.context}) on {latest.recorded_at[:10]}.")
    else:
        facts.append("No vitals recorded yet.")

    # Care tasks
    tasks = db.query(CareTask).filter(CareTask.patient_id == patient_id).all()
    pending = [t for t in tasks if t.status == "pending"]
    completed = [t for t in tasks if t.status == "completed"]
    facts.append(f"Care tasks status: {len(completed)} completed, {len(pending)} pending.")

    # Open flags
    flags = db.query(FollowupFlag).filter(FollowupFlag.patient_id == patient_id, FollowupFlag.status == "open").all()
    if flags:
        facts.append(f"Follow-up items for care team: {len(flags)} open item(s).")
    else:
        facts.append("All follow-up items are up to date.")

    return facts

def generate_patient_summary(db: Session, patient_id: str) -> Dict[str, Any]:
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        return {
            "patient_id": patient_id,
            "summary": "Patient not found.",
            "used_facts": [],
            "is_ai_generated": False,
            "fallback_used": True,
            "safety_disclaimer": SAFETY_DISCLAIMER
        }

    facts = build_patient_facts(db, patient_id)
    condition_name = ", ".join(patient.conditions)

    # 1. Deterministic Fallback Summary
    deterministic_summary = (
        f"Summary for {patient.display_name}: " + " ".join(facts)
    )

    # 2. Try Optional Constrained LLM
    ai_summary = generate_plain_language_summary(facts, condition_name)

    if ai_summary:
        return {
            "patient_id": patient_id,
            "summary": ai_summary,
            "used_facts": facts,
            "is_ai_generated": True,
            "fallback_used": False,
            "safety_disclaimer": SAFETY_DISCLAIMER
        }
    else:
        return {
            "patient_id": patient_id,
            "summary": deterministic_summary,
            "used_facts": facts,
            "is_ai_generated": False,
            "fallback_used": True,
            "safety_disclaimer": SAFETY_DISCLAIMER
        }
