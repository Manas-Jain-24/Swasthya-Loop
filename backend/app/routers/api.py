from pydantic import BaseModel
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Patient, CarePlan, Reading, CareTask, FollowupFlag
from ..schemas import (
    PatientResponse, PatientCreate,
    CarePlanResponse,
    ReadingCreate,
    ReadingResponse,
    CareTaskUpdate,
    CareTaskResponse,
    FollowupFlagResponse,
    CoordinatorOverviewResponse,
    CoordinatorOverviewItem,
    SummaryRequest,
    SummaryResponse,
    CopilotMessageRequest,
    CopilotMessageResponse,
    MedicationCheckRequest,
    MedicationCheckResponse,
    ScanImageRequest,
    ScanImageResponse,
)
from ..services.ai_copilot import ask_clinical_copilot, check_medication_safety, scan_multimodal_telemetry_image
from ..services.rules import evaluate_patient_tasks_and_rules
from ..services.summaries import generate_patient_summary

router = APIRouter(prefix="/api", tags=["SwasthyaLoop Core API"])

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SwasthyaLoop Clinical Follow-up Engine",
        "version": "1.0.0-hackathon-prototype",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.post("/patients", response_model=PatientResponse)
def create_patient(payload: PatientCreate, db: Session = Depends(get_db)):
    # Generate sequential patient ID
    existing_count = db.query(Patient).count()
    new_id = f"patient-{existing_count + 1:03d}"
    now_iso = datetime.now(timezone.utc).isoformat()

    new_patient = Patient(
        id=new_id,
        display_name=payload.display_name.strip(),
        age=payload.age,
        preferred_language=payload.preferred_language,
        care_plan_id=f"plan-{new_id}",
        is_demo_data=False
    )
    new_patient.conditions = payload.conditions
    db.add(new_patient)

    # Create associated CarePlan
    monitoring_list = []
    if "hypertension" in payload.conditions:
        monitoring_list.append({"type": "blood_pressure", "frequency": "daily", "target": "< 130/80"})
    if "type_2_diabetes" in payload.conditions:
        monitoring_list.append({"type": "blood_glucose", "frequency": "twice_daily", "target": "80-130 fasting"})

    care_plan = CarePlan(
        id=f"plan-{new_id}",
        patient_id=new_id,
        medication_tasks_enabled=True,
        next_appointment="2026-10-30",
        plan_status="active",
        plan_source="clinician_portal_onboarding"
    )
    care_plan.conditions = payload.conditions
    care_plan.monitoring = monitoring_list
    db.add(care_plan)

    # Initial baseline readings if provided
    if payload.initial_bp_systolic and payload.initial_bp_diastolic:
        bp_reading = Reading(
            id=f"reading-{uuid.uuid4().hex[:8]}",
            patient_id=new_id,
            type="blood_pressure",
            recorded_at=now_iso,
            systolic_mmhg=payload.initial_bp_systolic,
            diastolic_mmhg=payload.initial_bp_diastolic,
            unit="mmHg",
            context="unspecified",
            source="intake_vitals"
        )
        db.add(bp_reading)

    if payload.initial_glucose:
        glu_reading = Reading(
            id=f"reading-{uuid.uuid4().hex[:8]}",
            patient_id=new_id,
            type="blood_glucose",
            recorded_at=now_iso,
            value=payload.initial_glucose,
            unit="mg/dL",
            context="fasting",
            source="intake_vitals"
        )
        db.add(glu_reading)

    # Generate initial care task
    task_title = "Log morning blood pressure reading" if "hypertension" in payload.conditions else "Log fasting blood glucose"
    task = CareTask(
        id=f"task-{uuid.uuid4().hex[:6]}",
        patient_id=new_id,
        task_type="reading",
        title=task_title,
        due_at=now_iso,
        status="pending",
        created_by="care_plan_template"
    )
    db.add(task)

    db.commit()
    db.refresh(new_patient)
    return new_patient

@router.get("/patients", response_model=List[PatientResponse])
def list_patients(db: Session = Depends(get_db)):
    patients = db.query(Patient).all()
    # Trigger task & rule evaluation on patient list access
    for p in patients:
        evaluate_patient_tasks_and_rules(db, p.id)
    return patients

@router.get("/patients/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: str, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found.")
    evaluate_patient_tasks_and_rules(db, patient_id)
    return patient

@router.get("/patients/{patient_id}/care-plan", response_model=CarePlanResponse)
def get_care_plan(patient_id: str, db: Session = Depends(get_db)):
    plan = db.query(CarePlan).filter(CarePlan.patient_id == patient_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Care plan not found for patient.")
    return plan

@router.get("/patients/{patient_id}/readings", response_model=List[ReadingResponse])
def get_readings(patient_id: str, db: Session = Depends(get_db)):
    readings = db.query(Reading).filter(Reading.patient_id == patient_id).order_by(Reading.recorded_at.desc()).all()
    return readings

@router.post("/patients/{patient_id}/readings", response_model=ReadingResponse)
def create_reading(patient_id: str, reading_in: ReadingCreate, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found.")

    new_reading = Reading(
        id=f"reading-{uuid.uuid4().hex[:8]}",
        patient_id=patient_id,
        type=reading_in.type,
        recorded_at=reading_in.recorded_at,
        systolic_mmhg=reading_in.systolic_mmhg,
        diastolic_mmhg=reading_in.diastolic_mmhg,
        value=reading_in.value,
        unit=reading_in.unit,
        context=reading_in.context,
        source=reading_in.source,
        is_demo_data=True
    )
    db.add(new_reading)
    db.commit()
    db.refresh(new_reading)

    # Re-evaluate rules after new reading
    evaluate_patient_tasks_and_rules(db, patient_id)

    return new_reading

@router.get("/patients/{patient_id}/tasks", response_model=List[CareTaskResponse])
def list_tasks(patient_id: str, db: Session = Depends(get_db)):
    tasks = db.query(CareTask).filter(CareTask.patient_id == patient_id).order_by(CareTask.due_at.asc()).all()
    return tasks

@router.patch("/tasks/{task_id}", response_model=CareTaskResponse)
def update_task_status(task_id: str, task_update: CareTaskUpdate, db: Session = Depends(get_db)):
    task = db.query(CareTask).filter(CareTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")

    task.status = task_update.status
    if task_update.status == "completed":
        task.completed_at = datetime.now(timezone.utc).isoformat()
    else:
        task.completed_at = None

    db.commit()
    db.refresh(task)

    # Re-evaluate rules (resolves overdue flags if task completed)
    evaluate_patient_tasks_and_rules(db, task.patient_id)

    return task

@router.get("/followups", response_model=List[FollowupFlagResponse])
def list_followups(patient_id: Optional[str] = None, status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(FollowupFlag)
    if patient_id:
        query = query.filter(FollowupFlag.patient_id == patient_id)
    if status:
        query = query.filter(FollowupFlag.status == status)
    else:
        # Default to open items
        query = query.filter(FollowupFlag.status == "open")

    return query.order_by(FollowupFlag.created_at.desc()).all()

@router.patch("/followups/{flag_id}/resolve", response_model=FollowupFlagResponse)
def resolve_followup(flag_id: str, db: Session = Depends(get_db)):
    flag = db.query(FollowupFlag).filter(FollowupFlag.id == flag_id).first()
    if not flag:
        raise HTTPException(status_code=404, detail="Follow-up flag not found.")
    flag.status = "resolved"

    # If this flag was for an overdue task, automatically mark the corresponding care task as completed!
    if flag.category == "missing_task" or flag.source_rule_id == "rule-missing-reading-v1":
        pending_tasks = db.query(CareTask).filter(
            CareTask.patient_id == flag.patient_id,
            CareTask.status == "pending"
        ).all()
        now_iso = datetime.now(timezone.utc).isoformat()
        
        # Match task title in reason
        matched = False
        for t in pending_tasks:
            if t.title in flag.reason:
                t.status = "completed"
                t.completed_at = now_iso
                matched = True
                break
        
        # If not exact match, complete the earliest overdue task
        if not matched:
            for t in pending_tasks:
                if t.due_at <= now_iso:
                    t.status = "completed"
                    t.completed_at = now_iso
                    break

    db.commit()
    db.refresh(flag)
    return flag

@router.get("/coordinator/overview", response_model=CoordinatorOverviewResponse)
def get_coordinator_overview(db: Session = Depends(get_db)):
    patients = db.query(Patient).all()
    overview_items = []
    total_open_flags = 0
    total_pending_tasks = 0

    for p in patients:
        evaluate_patient_tasks_and_rules(db, p.id)
        open_flags = db.query(FollowupFlag).filter(FollowupFlag.patient_id == p.id, FollowupFlag.status == "open").all()
        pending_tasks = db.query(CareTask).filter(CareTask.patient_id == p.id, CareTask.status == "pending").all()
        latest_reading = db.query(Reading).filter(Reading.patient_id == p.id).order_by(Reading.recorded_at.desc()).first()
        care_plan = db.query(CarePlan).filter(CarePlan.patient_id == p.id).first()

        total_open_flags += len(open_flags)
        total_pending_tasks += len(pending_tasks)

        highest_flag = None
        if open_flags:
            # Sort by priority: urgent > needs_review > routine
            prio_order = {"urgent": 3, "needs_review": 2, "routine": 1}
            sorted_flags = sorted(open_flags, key=lambda f: prio_order.get(f.priority, 0), reverse=True)
            highest_flag = sorted_flags[0]

        overview_items.append(
            CoordinatorOverviewItem(
                patient_id=p.id,
                patient_name=p.display_name,
                conditions=p.conditions,
                open_flags_count=len(open_flags),
                pending_tasks_count=len(pending_tasks),
                latest_reading=latest_reading,
                next_appointment=care_plan.next_appointment if care_plan else None,
                highest_priority_flag=highest_flag
            )
        )

    return CoordinatorOverviewResponse(
        total_patients=len(patients),
        total_open_flags=total_open_flags,
        total_pending_tasks=total_pending_tasks,
        patients=overview_items
    )

@router.post("/summaries", response_model=SummaryResponse)
def get_patient_summary_endpoint(req: SummaryRequest, db: Session = Depends(get_db)):
    summary_data = generate_patient_summary(db, req.patient_id)
    return SummaryResponse(**summary_data)

class GeminiKeyRequest(BaseModel):
    api_key: str

@router.get("/settings/status")
def get_settings_status():
    from ..services.llm_provider import get_gemini_api_key
    key = get_gemini_api_key()
    return {
        "gemini_active": bool(key),
        "model": "gemini-3.8-flash" if key else "offline_deterministic_fallback"
    }

@router.post("/settings/gemini-key")
def set_gemini_key(req: GeminiKeyRequest):
    key = req.api_key.strip()
    if not key:
        raise HTTPException(status_code=400, detail="API key cannot be empty.")
    
    from ..services.llm_provider import test_gemini_connection
    is_valid = test_gemini_connection(key)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Failed to authenticate with Gemini API. Please check your key.")
    
    import os
    from pathlib import Path
    os.environ["GEMINI_API_KEY"] = key
    
    env_file = Path(__file__).resolve().parent.parent.parent.parent / ".env"
    try:
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(f"GEMINI_API_KEY={key}\n")
    except Exception:
        pass
        
    return {
        "status": "success",
        "message": "Gemini API key successfully validated and activated!",
        "model": "gemini-3.8-flash"
    }



# =====================================================================
# AI Copilot, Medication Safety & Multimodal Telemetry OCR Endpoints
# =====================================================================
@router.get("/summary/{patient_id}")
def get_patient_summary_get(patient_id: str, db: Session = Depends(get_db)):
    return generate_patient_summary(db, patient_id)

@router.post("/ai/copilot", response_model=CopilotMessageResponse)
def ai_copilot_endpoint(req: CopilotMessageRequest, db: Session = Depends(get_db)):
    return ask_clinical_copilot(
        db=db,
        patient_id=req.patient_id,
        user_role=req.user_role,
        message=req.message,
        language=req.language
    )

@router.post("/ai/medication-check", response_model=MedicationCheckResponse)
def ai_medication_check_endpoint(req: MedicationCheckRequest, db: Session = Depends(get_db)):
    return check_medication_safety(
        db=db,
        patient_id=req.patient_id,
        medication_name=req.medication_name,
        dosage=req.dosage
    )

@router.post("/ai/scan-image", response_model=ScanImageResponse)
def ai_scan_image_endpoint(req: ScanImageRequest):
    return scan_multimodal_telemetry_image(
        image_base64=req.image_base64,
        device_hint=req.device_hint,
        patient_id=req.patient_id
    )
