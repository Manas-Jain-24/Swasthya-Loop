import json
from sqlalchemy.orm import Session
from ..models import Patient, CarePlan, Reading, CareTask, FollowupFlag, RuleDefinition

def seed_database(db: Session):
    """
    Idempotent database seeding for SwasthyaLoop demo patients.
    Running multiple times will not duplicate patients.
    """
    # 1. Patient A: Demo Patient A (Hypertension - Mild Elevation)
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

        bp_history_a = [
            ("2026-10-14T08:30:00+05:30", 142.0, 90.0),
            ("2026-10-15T08:15:00+05:30", 138.0, 88.0),
            ("2026-10-16T08:45:00+05:30", 136.0, 85.0),
            ("2026-10-17T08:20:00+05:30", 135.0, 84.0),
            ("2026-10-18T08:30:00+05:30", 132.0, 82.0),
        ]
        for idx, (ts, sys, dia) in enumerate(bp_history_a):
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

    # 2. Patient B: Demo Patient B (Type 2 Diabetes - Overdue Reading Flag)
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

        glucose_history_b = [
            ("2026-10-16T08:00:00+05:30", 112.0, "fasting"),
            ("2026-10-16T14:15:00+05:30", 154.0, "after_meal"),
            ("2026-10-17T08:10:00+05:30", 118.0, "fasting"),
            ("2026-10-17T14:30:00+05:30", 168.0, "after_meal"),
            ("2026-10-18T08:05:00+05:30", 115.0, "fasting"),
        ]
        for idx, (ts, val, ctx) in enumerate(glucose_history_b):
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
            status="pending",
            created_by="simulated_care_plan"
        )
        db.add(task_b1)
        db.add(task_b2)

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

    # 3. Patient C: Rajesh Sharma (Hypertension - Stage 2 Severe Elevation / Urgent Flag)
    patient_c = db.query(Patient).filter(Patient.id == "patient-003").first()
    if not patient_c:
        patient_c = Patient(
            id="patient-003",
            display_name="Rajesh Sharma",
            age=64,
            conditions=["hypertension"],
            preferred_language="en",
            care_plan_id="plan-003",
            is_demo_data=True
        )
        db.add(patient_c)

        care_plan_c = CarePlan(
            id="plan-003",
            patient_id="patient-003",
            conditions=["hypertension"],
            monitoring=[{
                "type": "blood_pressure",
                "unit": "mmHg",
                "schedule": "daily_twice"
            }],
            medication_tasks_enabled=True,
            next_appointment="2026-10-22T11:00:00+05:30",
            plan_status="active",
            plan_source="simulated_demo_plan"
        )
        db.add(care_plan_c)

        bp_history_c = [
            ("2026-10-15T09:00:00+05:30", 146.0, 92.0),
            ("2026-10-16T09:00:00+05:30", 152.0, 95.0),
            ("2026-10-17T09:15:00+05:30", 158.0, 98.0),
            ("2026-10-18T08:30:00+05:30", 168.0, 102.0),
        ]
        for idx, (ts, sys, dia) in enumerate(bp_history_c):
            reading = Reading(
                id=f"reading-bp-c-{idx+1:03d}",
                patient_id="patient-003",
                type="blood_pressure",
                recorded_at=ts,
                systolic_mmhg=sys,
                diastolic_mmhg=dia,
                unit="mmHg",
                source="manual_entry",
                is_demo_data=True
            )
            db.add(reading)

        task_c1 = CareTask(
            id="task-301",
            patient_id="patient-003",
            task_type="reading",
            title="Log morning resting blood pressure",
            due_at="2026-10-18T09:00:00+05:30",
            status="completed",
            completed_at="2026-10-18T08:30:00+05:30",
            created_by="simulated_care_plan"
        )
        task_c2 = CareTask(
            id="task-302",
            patient_id="patient-003",
            task_type="medication",
            title="Take Amlodipine 5mg with breakfast",
            due_at="2026-10-18T09:30:00+05:30",
            status="pending",
            created_by="simulated_care_plan"
        )
        db.add(task_c1)
        db.add(task_c2)

        flag_c = FollowupFlag(
            id="flag-002",
            patient_id="patient-003",
            category="measurement_safety",
            priority="urgent",
            reason_code="BP_STAGE_2_ELEVATION",
            reason="Blood pressure spike: 168/102 mmHg exceeds safety threshold (>160 mmHg systolic).",
            recommended_action="Coordinate immediate clinical review with treating physician and verify repeat resting reading.",
            source_rule_id="rule-bp-elevated-v1",
            status="open",
            created_at="2026-10-18T08:35:00+05:30",
            is_demo_data=True
        )
        db.add(flag_c)

    # 4. Patient D: Sunita Patel (Type 2 Diabetes - Well-Controlled Clean Cohort)
    patient_d = db.query(Patient).filter(Patient.id == "patient-004").first()
    if not patient_d:
        patient_d = Patient(
            id="patient-004",
            display_name="Sunita Patel",
            age=51,
            conditions=["type_2_diabetes"],
            preferred_language="en",
            care_plan_id="plan-004",
            is_demo_data=True
        )
        db.add(patient_d)

        care_plan_d = CarePlan(
            id="plan-004",
            patient_id="patient-004",
            conditions=["type_2_diabetes"],
            monitoring=[{
                "type": "blood_glucose",
                "unit": "mg/dL",
                "schedule": "fasting_daily"
            }],
            medication_tasks_enabled=True,
            next_appointment="2026-11-05T15:00:00+05:30",
            plan_status="active",
            plan_source="simulated_demo_plan"
        )
        db.add(care_plan_d)

        glucose_history_d = [
            ("2026-10-15T07:45:00+05:30", 102.0, "fasting"),
            ("2026-10-16T08:00:00+05:30", 105.0, "fasting"),
            ("2026-10-17T07:50:00+05:30", 108.0, "fasting"),
            ("2026-10-18T08:10:00+05:30", 104.0, "fasting"),
        ]
        for idx, (ts, val, ctx) in enumerate(glucose_history_d):
            reading = Reading(
                id=f"reading-glu-d-{idx+1:03d}",
                patient_id="patient-004",
                type="blood_glucose",
                recorded_at=ts,
                value=val,
                unit="mg/dL",
                context=ctx,
                source="manual_entry",
                is_demo_data=True
            )
            db.add(reading)

        task_d1 = CareTask(
            id="task-401",
            patient_id="patient-004",
            task_type="reading",
            title="Log fasting morning blood glucose",
            due_at="2026-10-18T08:30:00+05:30",
            status="completed",
            completed_at="2026-10-18T08:10:00+05:30",
            created_by="simulated_care_plan"
        )
        task_d2 = CareTask(
            id="task-402",
            patient_id="patient-004",
            task_type="checkin",
            title="Complete weekly dietary fiber check-in",
            due_at="2026-10-18T18:00:00+05:30",
            status="completed",
            completed_at="2026-10-18T17:00:00+05:30",
            created_by="simulated_care_plan"
        )
        db.add(task_d1)
        db.add(task_d2)

    # 5. Patient E: Amitav Verma (Multimorbid: Hypertension + Type 2 Diabetes)
    patient_e = db.query(Patient).filter(Patient.id == "patient-005").first()
    if not patient_e:
        patient_e = Patient(
            id="patient-005",
            display_name="Amitav Verma",
            age=59,
            conditions=["hypertension", "type_2_diabetes"],
            preferred_language="en",
            care_plan_id="plan-005",
            is_demo_data=True
        )
        db.add(patient_e)

        care_plan_e = CarePlan(
            id="plan-005",
            patient_id="patient-005",
            conditions=["hypertension", "type_2_diabetes"],
            monitoring=[
                {"type": "blood_pressure", "unit": "mmHg", "schedule": "daily_morning"},
                {"type": "blood_glucose", "unit": "mg/dL", "schedule": "fasting_morning"}
            ],
            medication_tasks_enabled=True,
            next_appointment="2026-10-30T10:30:00+05:30",
            plan_status="active",
            plan_source="simulated_demo_plan"
        )
        db.add(care_plan_e)

        readings_e = [
            ("2026-10-16T08:00:00+05:30", "blood_pressure", 138.0, 88.0, None, None),
            ("2026-10-16T08:05:00+05:30", "blood_glucose", None, None, 132.0, "fasting"),
            ("2026-10-17T08:15:00+05:30", "blood_pressure", 140.0, 90.0, None, None),
            ("2026-10-17T08:20:00+05:30", "blood_glucose", None, None, 138.0, "fasting"),
        ]
        for idx, (ts, r_type, sys, dia, val, ctx) in enumerate(readings_e):
            r = Reading(
                id=f"reading-dual-{idx+1:03d}",
                patient_id="patient-005",
                type=r_type,
                recorded_at=ts,
                systolic_mmhg=sys,
                diastolic_mmhg=dia,
                value=val,
                unit="mmHg" if r_type == "blood_pressure" else "mg/dL",
                context=ctx,
                source="manual_entry",
                is_demo_data=True
            )
            db.add(r)

        task_e1 = CareTask(
            id="task-501",
            patient_id="patient-005",
            task_type="reading",
            title="Log morning dual panel (BP & Fasting Glucose)",
            due_at="2026-10-18T08:30:00+05:30",
            status="pending",
            created_by="simulated_care_plan"
        )
        db.add(task_e1)

        flag_e = FollowupFlag(
            id="flag-003",
            patient_id="patient-005",
            category="missing_task",
            priority="needs_review",
            reason_code="DUAL_PANEL_MISSED",
            reason="Multimorbid morning vitals panel missed for 2 consecutive days.",
            recommended_action="Outreach to patient via WhatsApp/SMS to check on device sync or medication supplies.",
            source_rule_id="rule-missing-reading-v1",
            status="open",
            created_at="2026-10-18T09:00:00+05:30",
            is_demo_data=True
        )
        db.add(flag_e)

    # Seed Rule Definitions
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
            priority="urgent",
            message_key="systolic_elevation_review",
            action_key="repeat_reading_and_guideline_check",
            source="ICMR / AHA 2023 Stage 2 Hypertension Triage Protocol",
            version=1,
            enabled=True
        )
        db.add(rule_2)

    db.commit()
