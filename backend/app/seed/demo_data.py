import json
from sqlalchemy.orm import Session
from ..models import Patient, CarePlan, Reading, CareTask, FollowupFlag, RuleDefinition

def seed_database(db: Session):
    """
    Idempotent database seeding for SwasthyaLoop demo patients.
    Running multiple times will not duplicate patients.
    """
    # 1. Check if Patient A exists
    patient_a = db.query(Patient).filter(Patient.id == "patient-001").first()
    if not patient_a:
        patient_a = Patient(
            id="patient-001",
            display_name="Demo Patient A",
            age=56,
            conditions=["hypertension"],
            preferred_language="en",
            care_plan_id="plan-001",
            is_demo_data=True
        )
        db.add(patient_a)

        care_plan_a = CarePlan(
            id="plan-001",
            patient_id="patient-001",
            conditions=["hypertension"],
            monitoring=[{
                "type": "blood_pressure",
                "unit": "mmHg",
                "schedule": "daily_morning"
            }],
            medication_tasks_enabled=True,
            next_appointment="2026-10-24T10:00:00+05:30",
            plan_status="active",
            plan_source="simulated_demo_plan"
        )
        db.add(care_plan_a)

        # 5 days of historical BP readings
        bp_history = [
            ("2026-10-14T08:30:00+05:30", 142.0, 90.0),
            ("2026-10-15T08:15:00+05:30", 138.0, 88.0),
            ("2026-10-16T08:45:00+05:30", 136.0, 85.0),
            ("2026-10-17T08:20:00+05:30", 135.0, 84.0),
            ("2026-10-18T08:30:00+05:30", 132.0, 82.0),
        ]
        for idx, (ts, sys, dia) in enumerate(bp_history):
            reading = Reading(
                id=f"reading-bp-{idx+1:03d}",
                patient_id="patient-001",
                type="blood_pressure",
                recorded_at=ts,
                systolic_mmhg=sys,
                diastolic_mmhg=dia,
                unit="mmHg",
                source="manual_entry",
                is_demo_data=True
            )
            db.add(reading)

        # Care tasks for Patient A
        task_a1 = CareTask(
            id="task-101",
            patient_id="patient-001",
            task_type="reading",
            title="Record morning blood pressure",
            due_at="2026-10-18T09:00:00+05:30",
            status="completed",
            completed_at="2026-10-18T08:30:00+05:30",
            created_by="simulated_care_plan"
        )
        task_a2 = CareTask(
            id="task-102",
            patient_id="patient-001",
            task_type="checkin",
            title="Log evening sodium check & 20-min brisk walk",
            due_at="2026-10-18T19:00:00+05:30",
            status="pending",
            created_by="simulated_care_plan"
        )
        db.add(task_a1)
        db.add(task_a2)

    # 2. Check if Patient B exists
    patient_b = db.query(Patient).filter(Patient.id == "patient-002").first()
    if not patient_b:
        patient_b = Patient(
            id="patient-002",
            display_name="Demo Patient B",
            age=62,
            conditions=["type_2_diabetes"],
            preferred_language="en",
            care_plan_id="plan-002",
            is_demo_data=True
        )
        db.add(patient_b)

        care_plan_b = CarePlan(
            id="plan-002",
            patient_id="patient-002",
            conditions=["type_2_diabetes"],
            monitoring=[{
                "type": "blood_glucose",
                "unit": "mg/dL",
                "schedule": "fasting_and_post_meal"
            }],
            medication_tasks_enabled=True,
            next_appointment="2026-10-26T14:30:00+05:30",
            plan_status="active",
            plan_source="simulated_demo_plan"
        )
        db.add(care_plan_b)

        # Glucose history
        glucose_history = [
            ("2026-10-16T08:00:00+05:30", 112.0, "fasting"),
            ("2026-10-16T14:15:00+05:30", 154.0, "after_meal"),
            ("2026-10-17T08:10:00+05:30", 118.0, "fasting"),
            ("2026-10-17T14:30:00+05:30", 168.0, "after_meal"),
            ("2026-10-18T08:05:00+05:30", 115.0, "fasting"),
        ]
        for idx, (ts, val, ctx) in enumerate(glucose_history):
            reading = Reading(
                id=f"reading-glu-{idx+1:03d}",
                patient_id="patient-002",
                type="blood_glucose",
                recorded_at=ts,
                value=val,
                unit="mg/dL",
                context=ctx,
                source="manual_entry",
                is_demo_data=True
            )
            db.add(reading)

        # Tasks for Patient B (includes an overdue task to demonstrate missing-task follow-up)
        task_b1 = CareTask(
            id="task-201",
            patient_id="patient-002",
            task_type="reading",
            title="Log fasting morning glucose",
            due_at="2026-10-18T08:00:00+05:30",
            status="completed",
            completed_at="2026-10-18T08:05:00+05:30",
            created_by="simulated_care_plan"
        )
        task_b2 = CareTask(
            id="task-202",
            patient_id="patient-002",
            task_type="reading",
            title="Log post-lunch glucose reading",
            due_at="2026-10-18T13:30:00+05:30",
            status="pending",  # Overdue relative to current afternoon time
            created_by="simulated_care_plan"
        )
        db.add(task_b1)
        db.add(task_b2)

        # Pre-seed the overdue task flag
        flag_b = FollowupFlag(
            id="flag-001",
            patient_id="patient-002",
            category="missing_task",
            priority="routine",
            reason_code="READING_TASK_OVERDUE",
            reason="Planned post-lunch glucose reading was not recorded by scheduled window.",
            recommended_action="Check whether patient needs help logging or experienced meter sync issues.",
            source_rule_id="rule-missing-reading-v1",
            status="open",
            created_at="2026-10-18T13:45:00+05:30",
            is_demo_data=True
        )
        db.add(flag_b)

    # 3. Seed Rule Definitions
    rule_1 = db.query(RuleDefinition).filter(RuleDefinition.rule_id == "rule-missing-reading-v1").first()
    if not rule_1:
        rule_1 = RuleDefinition(
            rule_id="rule-missing-reading-v1",
            category="missing_task",
            measurement_type="all",
            condition="task_overdue_and_pending",
            priority="routine",
            message_key="task_overdue",
            action_key="check_patient_recording_assistance",
            source="Clinical Practice Guideline Routine Task Monitoring v1.0",
            version=1,
            enabled=True
        )
        db.add(rule_1)

    rule_2 = db.query(RuleDefinition).filter(RuleDefinition.rule_id == "rule-bp-elevated-v1").first()
    if not rule_2:
        rule_2 = RuleDefinition(
            rule_id="rule-bp-elevated-v1",
            category="measurement_safety",
            measurement_type="blood_pressure",
            condition="systolic_gt_160",
            priority="needs_review",
            message_key="systolic_elevation_review",
            action_key="repeat_reading_and_guideline_check",
            source="Synthetic Test Trigger Scenario (Requires Clinical Board Review)",
            version=1,
            enabled=False  # Kept disabled per safety principle
        )
        db.add(rule_2)

    db.commit()
