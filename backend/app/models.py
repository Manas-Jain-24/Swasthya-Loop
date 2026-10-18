import json
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, Float, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(String, primary_key=True, index=True)
    display_name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    _conditions = Column("conditions", Text, nullable=False, default="[]")
    preferred_language = Column(String, default="en")
    care_plan_id = Column(String, nullable=True)
    is_demo_data = Column(Boolean, default=True)

    @property
    def conditions(self):
        try:
            return json.loads(self._conditions)
        except Exception:
            return []

    @conditions.setter
    def conditions(self, val):
        self._conditions = json.dumps(val)

    care_plan = relationship("CarePlan", back_populates="patient", uselist=False, cascade="all, delete-orphan")
    readings = relationship("Reading", back_populates="patient", cascade="all, delete-orphan")
    tasks = relationship("CareTask", back_populates="patient", cascade="all, delete-orphan")
    flags = relationship("FollowupFlag", back_populates="patient", cascade="all, delete-orphan")


class CarePlan(Base):
    __tablename__ = "care_plans"

    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False)
    _conditions = Column("conditions", Text, nullable=False, default="[]")
    _monitoring = Column("monitoring", Text, nullable=False, default="[]")
    medication_tasks_enabled = Column(Boolean, default=True)
    next_appointment = Column(String, nullable=True)
    plan_status = Column(String, default="active")
    plan_source = Column(String, default="simulated_demo_plan")

    @property
    def conditions(self):
        try:
            return json.loads(self._conditions)
        except Exception:
            return []

    @conditions.setter
    def conditions(self, val):
        self._conditions = json.dumps(val)

    @property
    def monitoring(self):
        try:
            return json.loads(self._monitoring)
        except Exception:
            return []

    @monitoring.setter
    def monitoring(self, val):
        self._monitoring = json.dumps(val)

    patient = relationship("Patient", back_populates="care_plan")


class Reading(Base):
    __tablename__ = "readings"

    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False, index=True)
    type = Column(String, nullable=False)  # "blood_pressure" | "blood_glucose"
    recorded_at = Column(String, nullable=False)  # ISO 8601 string
    systolic_mmhg = Column(Float, nullable=True)
    diastolic_mmhg = Column(Float, nullable=True)
    value = Column(Float, nullable=True)
    unit = Column(String, nullable=True)  # "mmHg" or "mg/dL"
    context = Column(String, nullable=True)  # "fasting", "before_meal", "after_meal", "bedtime", "unspecified"
    source = Column(String, default="manual_entry")
    is_demo_data = Column(Boolean, default=True)

    patient = relationship("Patient", back_populates="readings")


class CareTask(Base):
    __tablename__ = "care_tasks"

    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False, index=True)
    task_type = Column(String, nullable=False)  # "reading" | "medication" | "checkin"
    title = Column(String, nullable=False)
    due_at = Column(String, nullable=False)  # ISO 8601 string
    status = Column(String, default="pending")  # "pending", "completed", "skipped", "needs_help", "not_applicable"
    completed_at = Column(String, nullable=True)
    created_by = Column(String, default="simulated_care_plan")

    patient = relationship("Patient", back_populates="tasks")


class FollowupFlag(Base):
    __tablename__ = "followup_flags"

    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False, index=True)
    category = Column(String, nullable=False)  # "missing_task" | "data_quality" | "measurement_safety"
    priority = Column(String, default="routine")  # "routine" | "needs_review" | "urgent"
    reason_code = Column(String, nullable=False)
    reason = Column(Text, nullable=False)
    recommended_action = Column(Text, nullable=False)
    source_rule_id = Column(String, nullable=False)
    status = Column(String, default="open")  # "open" | "resolved" | "dismissed"
    created_at = Column(String, default=lambda: datetime.now(timezone.utc).isoformat())
    is_demo_data = Column(Boolean, default=True)

    patient = relationship("Patient", back_populates="flags")


class RuleDefinition(Base):
    __tablename__ = "rule_definitions"

    rule_id = Column(String, primary_key=True, index=True)
    category = Column(String, nullable=False)
    measurement_type = Column(String, nullable=False)
    condition = Column(String, nullable=False)
    priority = Column(String, default="needs_review")
    message_key = Column(String, nullable=False)
    action_key = Column(String, nullable=False)
    source = Column(String, nullable=False)
    version = Column(Integer, default=1)
    enabled = Column(Boolean, default=False)
