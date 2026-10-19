from typing import List, Optional, Literal
from pydantic import BaseModel, Field, model_validator

class PatientCreate(BaseModel):
    display_name: str
    age: int
    conditions: List[str]
    preferred_language: str = "en"
    initial_bp_systolic: Optional[float] = None
    initial_bp_diastolic: Optional[float] = None
    initial_glucose: Optional[float] = None

class PatientResponse(BaseModel):
    id: str
    display_name: str
    age: int
    conditions: List[str]
    preferred_language: str
    care_plan_id: Optional[str] = None
    is_demo_data: bool = True

    model_config = {"from_attributes": True}

class CarePlanResponse(BaseModel):
    id: str
    patient_id: str
    conditions: List[str]
    monitoring: List[dict]
    medication_tasks_enabled: bool
    next_appointment: Optional[str] = None
    plan_status: str
    plan_source: str

    model_config = {"from_attributes": True}

class ReadingCreate(BaseModel):
    patient_id: str
    type: Literal["blood_pressure", "blood_glucose"]
    recorded_at: str  # ISO timestamp
    systolic_mmhg: Optional[float] = None
    diastolic_mmhg: Optional[float] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    context: Optional[Literal["fasting", "before_meal", "after_meal", "bedtime", "unspecified"]] = None
    source: str = "manual_entry"

    @model_validator(mode="after")
    def validate_reading_fields(self):
        if self.type == "blood_pressure":
            if self.systolic_mmhg is None or self.diastolic_mmhg is None:
                raise ValueError("Both systolic and diastolic measurements are required for blood pressure.")
            if self.systolic_mmhg < 40 or self.systolic_mmhg > 300:
                raise ValueError(f"Systolic blood pressure {self.systolic_mmhg} is outside plausible physiological range (40-300 mmHg).")
            if self.diastolic_mmhg < 20 or self.diastolic_mmhg > 200:
                raise ValueError(f"Diastolic blood pressure {self.diastolic_mmhg} is outside plausible physiological range (20-200 mmHg).")
            if self.systolic_mmhg <= self.diastolic_mmhg:
                raise ValueError("Systolic pressure must be strictly greater than diastolic pressure.")
            if self.unit and self.unit != "mmHg":
                raise ValueError("Blood pressure unit must be 'mmHg'.")
            self.unit = "mmHg"
        elif self.type == "blood_glucose":
            if self.value is None:
                raise ValueError("A glucose value is required.")
            if self.value < 10 or self.value > 1000:
                raise ValueError(f"Glucose value {self.value} is outside plausible physiological range (10-1000 mg/dL).")
            if self.unit and self.unit != "mg/dL":
                raise ValueError("Glucose unit must be 'mg/dL'.")
            self.unit = "mg/dL"
            if not self.context:
                self.context = "unspecified"
        return self

class ReadingResponse(BaseModel):
    id: str
    patient_id: str
    type: str
    recorded_at: str
    systolic_mmhg: Optional[float] = None
    diastolic_mmhg: Optional[float] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    context: Optional[str] = None
    source: str
    is_demo_data: bool = True

    model_config = {"from_attributes": True}

class CareTaskUpdate(BaseModel):
    status: Literal["pending", "completed", "skipped", "needs_help", "not_applicable"]

class CareTaskResponse(BaseModel):
    id: str
    patient_id: str
    task_type: str
    title: str
    due_at: str
    status: str
    completed_at: Optional[str] = None
    created_by: str

    model_config = {"from_attributes": True}

class FollowupFlagResponse(BaseModel):
    id: str
    patient_id: str
    category: str
    priority: str
    reason_code: str
    reason: str
    recommended_action: str
    source_rule_id: str
    status: str
    created_at: str
    is_demo_data: bool = True

    model_config = {"from_attributes": True}

class CoordinatorOverviewItem(BaseModel):
    patient_id: str
    patient_name: str
    conditions: List[str]
    open_flags_count: int
    pending_tasks_count: int
    latest_reading: Optional[ReadingResponse] = None
    next_appointment: Optional[str] = None
    highest_priority_flag: Optional[FollowupFlagResponse] = None

class CoordinatorOverviewResponse(BaseModel):
    total_patients: int
    total_open_flags: int
    total_pending_tasks: int
    patients: List[CoordinatorOverviewItem]

class SummaryRequest(BaseModel):
    patient_id: str

class SummaryResponse(BaseModel):
    patient_id: str
    summary: str
    used_facts: List[str]
    is_ai_generated: bool
    fallback_used: bool
    safety_disclaimer: str


# =====================================================================
# AI Copilot, Medication Safety & Multimodal Scanner Schemas
# =====================================================================
class CopilotMessageRequest(BaseModel):
    patient_id: str
    user_role: str = "doctor" # "doctor" or "patient"
    message: str
    language: str = "en" # "en" or "hi"

class CopilotMessageResponse(BaseModel):
    reply: str
    audio_text: Optional[str] = None
    is_emergency: bool = False
    citations: List[str] = []
    suggested_actions: List[str] = []
    source: str = "gemini-3.8-flash"

class MedicationCheckRequest(BaseModel):
    patient_id: str
    medication_name: str
    dosage: Optional[str] = ""

class MedicationCheckResponse(BaseModel):
    medication_name: str
    dosage: Optional[str] = ""
    status: str # "safe", "warning", "contraindicated"
    safety_score: int
    summary: str
    contraindications: List[str] = []
    warnings: List[str] = []
    guideline_recommendation: str
    evidence_source: str

class ScanImageRequest(BaseModel):
    image_base64: str
    device_hint: Optional[str] = "auto"
    patient_id: Optional[str] = None

class ScanImageResponse(BaseModel):
    detected_device: str
    reading_type: str
    systolic_mmhg: Optional[float] = None
    diastolic_mmhg: Optional[float] = None
    pulse_bpm: Optional[float] = None
    glucose_value: Optional[float] = None
    glucose_context: Optional[str] = "fasting"
    medications_extracted: List[str] = []
    confidence: float
    clinical_interpretation: str
    raw_text: str
