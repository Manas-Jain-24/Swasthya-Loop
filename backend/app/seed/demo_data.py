import json
from sqlalchemy.orm import Session
from ..models import Patient, CarePlan, Reading, CareTask, FollowupFlag, RuleDefinition

def seed_database(db: Session):
    """
    Idempotent database seeding for SwasthyaLoop demo patients.
    Includes 10 clinically diverse patients:
    - Critical acute alerts (HTN Crisis, Severe Glycemic Spikes)
    - Well-controlled / Almost healed (Target BP 118/76, Controlled Glucose 104)
    - Young adult / Stress-induced pre-HTN (Age 24)
    - Single condition (Hypertension, T2D) & Multimorbid (Dual HTN + T2D)
    """

    # 1. Patient 001: Ananya Deshmukh (Hypertension - Mild Elevation, Steady Improvement)
    patient_1 = db.query(Patient).filter(Patient.id == "patient-001").first()
    if patient_1 and ("Demo" in patient_1.display_name):
        patient_1.display_name = "Ananya Deshmukh"
    if not patient_1:
        patient_1 = Patient(
            id="patient-001",
            display_name="Ananya Deshmukh",
            age=56,
            conditions=["hypertension"],
            preferred_language="en",
            care_plan_id="plan-001",
            is_demo_data=True
        )
        db.add(patient_1)

        care_plan_1 = CarePlan(
            id="plan-001",
            patient_id="patient-001",
            conditions=["hypertension"],
            monitoring=[{"type": "blood_pressure", "unit": "mmHg", "schedule": "daily_morning"}],
            medication_tasks_enabled=True,
            next_appointment="2026-10-24T10:00:00+05:30",
            plan_status="active",
            plan_source="simulated_demo_plan"
        )
        db.add(care_plan_1)

        bp_history_1 = [
            ("2026-10-14T08:30:00+05:30", 142.0, 90.0),
            ("2026-10-15T08:15:00+05:30", 138.0, 88.0),
            ("2026-10-16T08:45:00+05:30", 136.0, 85.0),
            ("2026-10-17T08:20:00+05:30", 135.0, 84.0),
            ("2026-10-18T08:30:00+05:30", 132.0, 82.0),
        ]
        for idx, (ts, sys, dia) in enumerate(bp_history_1):
            db.add(Reading(
                id=f"reading-bp-1-{idx+1:03d}",
                patient_id="patient-001",
                type="blood_pressure",
                recorded_at=ts,
                systolic_mmhg=sys,
                diastolic_mmhg=dia,
                unit="mmHg",
                source="manual_entry",
                is_demo_data=True
            ))

        db.add(CareTask(
            id="task-101",
            patient_id="patient-001",
            task_type="reading",
            title="Record morning resting blood pressure",
            due_at="2026-10-18T09:00:00+05:30",
            status="completed",
            completed_at="2026-10-18T08:30:00+05:30",
            created_by="simulated_care_plan"
        ))
        db.add(CareTask(
            id="task-102",
            patient_id="patient-001",
            task_type="checkin",
            title="Log evening sodium check & 20-min brisk walk",
            due_at="2026-10-18T19:00:00+05:30",
            status="pending",
            created_by="simulated_care_plan"
        ))

    # 2. Patient 002: Vikramaditya Rao (Type 2 Diabetes - Overdue Reading Flag)
    patient_2 = db.query(Patient).filter(Patient.id == "patient-002").first()
    if patient_2 and ("Demo" in patient_2.display_name):
        patient_2.display_name = "Vikramaditya Rao"
    if not patient_2:
        patient_2 = Patient(
            id="patient-002",
            display_name="Vikramaditya Rao",
            age=62,
            conditions=["type_2_diabetes"],
            preferred_language="en",
            care_plan_id="plan-002",
            is_demo_data=True
        )
        db.add(patient_2)

        care_plan_2 = CarePlan(
            id="plan-002",
            patient_id="patient-002",
            conditions=["type_2_diabetes"],
            monitoring=[{"type": "blood_glucose", "unit": "mg/dL", "schedule": "fasting_and_post_meal"}],
            medication_tasks_enabled=True,
            next_appointment="2026-10-26T14:30:00+05:30",
            plan_status="active",
            plan_source="simulated_demo_plan"
        )
        db.add(care_plan_2)

        glucose_history_2 = [
            ("2026-10-16T08:00:00+05:30", 112.0, "fasting"),
            ("2026-10-16T14:15:00+05:30", 154.0, "after_meal"),
            ("2026-10-17T08:10:00+05:30", 118.0, "fasting"),
            ("2026-10-17T14:30:00+05:30", 168.0, "after_meal"),
            ("2026-10-18T08:05:00+05:30", 115.0, "fasting"),
        ]
        for idx, (ts, val, ctx) in enumerate(glucose_history_2):
            db.add(Reading(
                id=f"reading-glu-2-{idx+1:03d}",
                patient_id="patient-002",
                type="blood_glucose",
                recorded_at=ts,
                value=val,
                unit="mg/dL",
                context=ctx,
                source="manual_entry",
                is_demo_data=True
            ))

        db.add(CareTask(
            id="task-201",
            patient_id="patient-002",
            task_type="reading",
            title="Log fasting morning glucose",
            due_at="2026-10-18T08:30:00+05:30",
            status="completed",
            completed_at="2026-10-18T08:05:00+05:30",
            created_by="simulated_care_plan"
        ))
        db.add(CareTask(
            id="task-202",
            patient_id="patient-002",
            task_type="reading",
            title="Log post-lunch glucose reading",
            due_at="2026-10-18T14:30:00+05:30",
            status="pending",
            created_by="simulated_care_plan"
        ))

        db.add(FollowupFlag(
            id="flag-001",
            patient_id="patient-002",
            category="missing_task",
            priority="routine",
            reason_code="POST_MEAL_READING_OVERDUE",
            reason="Scheduled task 'Log post-lunch glucose reading' was due by 2026-10-18T14:30:00+05:30 and has not yet been completed.",
            recommended_action="Follow up via routine check-in to confirm if the patient needs assistance recording this reading.",
            source_rule_id="rule-missing-reading-v1",
            status="open",
            created_at="2026-10-18T15:00:00+05:30",
            is_demo_data=True
        ))

    # 3. Patient 003: Rajesh Sharma (Hypertension - Stage 2 Hypertensive Crisis Spike)
    patient_3 = db.query(Patient).filter(Patient.id == "patient-003").first()
    if not patient_3:
        patient_3 = Patient(
            id="patient-003",
            display_name="Rajesh Sharma",
            age=58,
            conditions=["hypertension"],
            preferred_language="en",
            care_plan_id="plan-003",
            is_demo_data=True
        )
        db.add(patient_3)

        care_plan_3 = CarePlan(
            id="plan-003",
            patient_id="patient-003",
            conditions=["hypertension"],
            monitoring=[{"type": "blood_pressure", "unit": "mmHg", "schedule": "daily_twice"}],
            medication_tasks_enabled=True,
            next_appointment="2026-10-22T11:00:00+05:30",
            plan_status="active",
            plan_source="simulated_demo_plan"
        )
        db.add(care_plan_3)

        bp_history_3 = [
            ("2026-10-15T08:30:00+05:30", 152.0, 94.0),
            ("2026-10-16T08:15:00+05:30", 156.0, 96.0),
            ("2026-10-17T08:45:00+05:30", 158.0, 98.0),
            ("2026-10-18T08:20:00+05:30", 168.0, 102.0),
        ]
        for idx, (ts, sys, dia) in enumerate(bp_history_3):
            db.add(Reading(
                id=f"reading-bp-3-{idx+1:03d}",
                patient_id="patient-003",
                type="blood_pressure",
                recorded_at=ts,
                systolic_mmhg=sys,
                diastolic_mmhg=dia,
                unit="mmHg",
                source="manual_entry",
                is_demo_data=True
            ))

        db.add(CareTask(
            id="task-301",
            patient_id="patient-003",
            task_type="reading",
            title="Log morning resting blood pressure",
            due_at="2026-10-18T09:00:00+05:30",
            status="completed",
            completed_at="2026-10-18T08:30:00+05:30",
            created_by="simulated_care_plan"
        ))
        db.add(CareTask(
            id="task-302",
            patient_id="patient-003",
            task_type="medication",
            title="Take Amlodipine 5mg with breakfast",
            due_at="2026-10-18T09:30:00+05:30",
            status="pending",
            created_by="simulated_care_plan"
        ))

        db.add(FollowupFlag(
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
        ))

    # 4. Patient 004: Sunita Patel (Type 2 Diabetes - Well-Controlled Clean Cohort)
    patient_4 = db.query(Patient).filter(Patient.id == "patient-004").first()
    if not patient_4:
        patient_4 = Patient(
            id="patient-004",
            display_name="Sunita Patel",
            age=51,
            conditions=["type_2_diabetes"],
            preferred_language="en",
            care_plan_id="plan-004",
            is_demo_data=True
        )
        db.add(patient_4)

        care_plan_4 = CarePlan(
            id="plan-004",
            patient_id="patient-004",
            conditions=["type_2_diabetes"],
            monitoring=[{"type": "blood_glucose", "unit": "mg/dL", "schedule": "fasting_daily"}],
            medication_tasks_enabled=True,
            next_appointment="2026-11-05T15:00:00+05:30",
            plan_status="active",
            plan_source="simulated_demo_plan"
        )
        db.add(care_plan_4)

        glucose_history_4 = [
            ("2026-10-15T07:45:00+05:30", 102.0, "fasting"),
            ("2026-10-16T08:00:00+05:30", 105.0, "fasting"),
            ("2026-10-17T07:50:00+05:30", 108.0, "fasting"),
            ("2026-10-18T08:10:00+05:30", 104.0, "fasting"),
        ]
        for idx, (ts, val, ctx) in enumerate(glucose_history_4):
            db.add(Reading(
                id=f"reading-glu-4-{idx+1:03d}",
                patient_id="patient-004",
                type="blood_glucose",
                recorded_at=ts,
                value=val,
                unit="mg/dL",
                context=ctx,
                source="manual_entry",
                is_demo_data=True
            ))

        db.add(CareTask(
            id="task-401",
            patient_id="patient-004",
            task_type="reading",
            title="Log fasting morning blood glucose",
            due_at="2026-10-18T08:30:00+05:30",
            status="completed",
            completed_at="2026-10-18T08:10:00+05:30",
            created_by="simulated_care_plan"
        ))

    # 5. Patient 005: Amitav Verma (Multimorbid: Hypertension + Type 2 Diabetes)
    patient_5 = db.query(Patient).filter(Patient.id == "patient-005").first()
    if not patient_5:
        patient_5 = Patient(
            id="patient-005",
            display_name="Amitav Verma",
            age=59,
            conditions=["hypertension", "type_2_diabetes"],
            preferred_language="en",
            care_plan_id="plan-005",
            is_demo_data=True
        )
        db.add(patient_5)

        care_plan_5 = CarePlan(
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
        db.add(care_plan_5)

        readings_5 = [
            ("2026-10-16T08:00:00+05:30", "blood_pressure", 138.0, 88.0, None, None),
            ("2026-10-16T08:05:00+05:30", "blood_glucose", None, None, 132.0, "fasting"),
            ("2026-10-17T08:15:00+05:30", "blood_pressure", 140.0, 90.0, None, None),
            ("2026-10-17T08:20:00+05:30", "blood_glucose", None, None, 138.0, "fasting"),
        ]
        for idx, (ts, r_type, sys, dia, val, ctx) in enumerate(readings_5):
            db.add(Reading(
                id=f"reading-dual-5-{idx+1:03d}",
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
            ))

        db.add(CareTask(
            id="task-501",
            patient_id="patient-005",
            task_type="reading",
            title="Log morning dual panel (BP & Fasting Glucose)",
            due_at="2026-10-18T08:30:00+05:30",
            status="pending",
            created_by="simulated_care_plan"
        ))

        db.add(FollowupFlag(
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
        ))

    # 6. Patient 006: Kavita Nambiar (CRITICAL Type 2 Diabetes - Acute Glycemic Spike 284 mg/dL)
    patient_6 = db.query(Patient).filter(Patient.id == "patient-006").first()
    if not patient_6:
        patient_6 = Patient(
            id="patient-006",
            display_name="Kavita Nambiar",
            age=49,
            conditions=["type_2_diabetes"],
            preferred_language="en",
            care_plan_id="plan-006",
            is_demo_data=True
        )
        db.add(patient_6)

        care_plan_6 = CarePlan(
            id="plan-006",
            patient_id="patient-006",
            conditions=["type_2_diabetes"],
            monitoring=[{"type": "blood_glucose", "unit": "mg/dL", "schedule": "daily_twice"}],
            medication_tasks_enabled=True,
            next_appointment="2026-10-20T10:00:00+05:30",
            plan_status="active",
            plan_source="simulated_demo_plan"
        )
        db.add(care_plan_6)

        glucose_history_6 = [
            ("2026-10-16T08:00:00+05:30", 185.0, "fasting"),
            ("2026-10-17T08:00:00+05:30", 210.0, "fasting"),
            ("2026-10-18T14:30:00+05:30", 284.0, "after_meal"),
        ]
        for idx, (ts, val, ctx) in enumerate(glucose_history_6):
            db.add(Reading(
                id=f"reading-glu-6-{idx+1:03d}",
                patient_id="patient-006",
                type="blood_glucose",
                recorded_at=ts,
                value=val,
                unit="mg/dL",
                context=ctx,
                source="manual_entry",
                is_demo_data=True
            ))

        db.add(CareTask(
            id="task-601",
            patient_id="patient-006",
            task_type="reading",
            title="Log fasting morning blood glucose",
            due_at="2026-10-18T08:30:00+05:30",
            status="completed",
            completed_at="2026-10-18T08:15:00+05:30",
            created_by="simulated_care_plan"
        ))
        db.add(CareTask(
            id="task-602",
            patient_id="patient-006",
            task_type="medication",
            title="Inject Insulin Glargine 12 units before dinner",
            due_at="2026-10-18T20:00:00+05:30",
            status="pending",
            created_by="simulated_care_plan"
        ))

        db.add(FollowupFlag(
            id="flag-004",
            patient_id="patient-006",
            category="measurement_safety",
            priority="urgent",
            reason_code="GLUCOSE_SEVERE_SPIKE",
            reason="Critical post-prandial blood glucose spike (284 mg/dL exceeds 250 mg/dL safety limit).",
            recommended_action="Emergency endocrinology review. Assess ketone levels and evaluate insulin dose titration.",
            source_rule_id="rule-glucose-crisis-v1",
            status="open",
            created_at="2026-10-18T15:15:00+05:30",
            is_demo_data=True
        ))

    # 7. Patient 007: Meera Krishnan (ALMOST HEALED / Controlled Hypertension - Remission Phase)
    patient_7 = db.query(Patient).filter(Patient.id == "patient-007").first()
    if not patient_7:
        patient_7 = Patient(
            id="patient-007",
            display_name="Meera Krishnan",
            age=53,
            conditions=["hypertension"],
            preferred_language="en",
            care_plan_id="plan-007",
            is_demo_data=True
        )
        db.add(patient_7)

        care_plan_7 = CarePlan(
            id="plan-007",
            patient_id="patient-007",
            conditions=["hypertension"],
            monitoring=[{"type": "blood_pressure", "unit": "mmHg", "schedule": "alternate_days"}],
            medication_tasks_enabled=True,
            next_appointment="2026-11-20T10:00:00+05:30",
            plan_status="active",
            plan_source="simulated_demo_plan"
        )
        db.add(care_plan_7)

        bp_history_7 = [
            ("2026-10-12T08:00:00+05:30", 122.0, 78.0),
            ("2026-10-14T08:00:00+05:30", 120.0, 76.0),
            ("2026-10-16T08:00:00+05:30", 118.0, 76.0),
            ("2026-10-18T08:00:00+05:30", 116.0, 74.0),
        ]
        for idx, (ts, sys, dia) in enumerate(bp_history_7):
            db.add(Reading(
                id=f"reading-bp-7-{idx+1:03d}",
                patient_id="patient-007",
                type="blood_pressure",
                recorded_at=ts,
                systolic_mmhg=sys,
                diastolic_mmhg=dia,
                unit="mmHg",
                source="manual_entry",
                is_demo_data=True
            ))

        db.add(CareTask(
            id="task-701",
            patient_id="patient-007",
            task_type="reading",
            title="Log resting morning blood pressure",
            due_at="2026-10-18T09:00:00+05:30",
            status="completed",
            completed_at="2026-10-18T08:00:00+05:30",
            created_by="simulated_care_plan"
        ))
        db.add(CareTask(
            id="task-702",
            patient_id="patient-007",
            task_type="checkin",
            title="Weekly 150-min cardio maintenance log",
            due_at="2026-10-18T18:00:00+05:30",
            status="completed",
            completed_at="2026-10-18T17:30:00+05:30",
            created_by="simulated_care_plan"
        ))

    # 8. Patient 008: Aarav Mehta ("Some Me" - Age 24, Tech Worker with Stress-Induced Pre-HTN)
    patient_8 = db.query(Patient).filter(Patient.id == "patient-008").first()
    if not patient_8:
        patient_8 = Patient(
            id="patient-008",
            display_name="Aarav Mehta",
            age=24,
            conditions=["hypertension"],
            preferred_language="en",
            care_plan_id="plan-008",
            is_demo_data=True
        )
        db.add(patient_8)

        care_plan_8 = CarePlan(
            id="plan-008",
            patient_id="patient-008",
            conditions=["hypertension"],
            monitoring=[{"type": "blood_pressure", "unit": "mmHg", "schedule": "daily_evening"}],
            medication_tasks_enabled=False,
            next_appointment="2026-11-15T16:00:00+05:30",
            plan_status="active",
            plan_source="simulated_demo_plan"
        )
        db.add(care_plan_8)

        bp_history_8 = [
            ("2026-10-15T20:30:00+05:30", 144.0, 90.0),
            ("2026-10-16T21:15:00+05:30", 140.0, 88.0),
            ("2026-10-17T20:45:00+05:30", 142.0, 88.0),
            ("2026-10-18T20:30:00+05:30", 138.0, 86.0),
        ]
        for idx, (ts, sys, dia) in enumerate(bp_history_8):
            db.add(Reading(
                id=f"reading-bp-8-{idx+1:03d}",
                patient_id="patient-008",
                type="blood_pressure",
                recorded_at=ts,
                systolic_mmhg=sys,
                diastolic_mmhg=dia,
                unit="mmHg",
                source="manual_entry",
                is_demo_data=True
            ))

        db.add(CareTask(
            id="task-801",
            patient_id="patient-008",
            task_type="reading",
            title="Log evening post-shift resting BP",
            due_at="2026-10-18T21:00:00+05:30",
            status="pending",
            created_by="simulated_care_plan"
        ))
        db.add(CareTask(
            id="task-802",
            patient_id="patient-008",
            task_type="checkin",
            title="Mindfulness & sleep hygiene check-in (7+ hrs sleep)",
            due_at="2026-10-18T22:00:00+05:30",
            status="completed",
            completed_at="2026-10-18T21:00:00+05:30",
            created_by="simulated_care_plan"
        ))

    # 9. Patient 009: Harish Chandra (Severe Multimorbid: Dual HTN Crisis 164/98 + T2D Fasting 210)
    patient_9 = db.query(Patient).filter(Patient.id == "patient-009").first()
    if not patient_9:
        patient_9 = Patient(
            id="patient-009",
            display_name="Harish Chandra",
            age=67,
            conditions=["hypertension", "type_2_diabetes"],
            preferred_language="en",
            care_plan_id="plan-009",
            is_demo_data=True
        )
        db.add(patient_9)

        care_plan_9 = CarePlan(
            id="plan-009",
            patient_id="patient-009",
            conditions=["hypertension", "type_2_diabetes"],
            monitoring=[
                {"type": "blood_pressure", "unit": "mmHg", "schedule": "daily_morning"},
                {"type": "blood_glucose", "unit": "mg/dL", "schedule": "daily_morning"}
            ],
            medication_tasks_enabled=True,
            next_appointment="2026-10-21T09:30:00+05:30",
            plan_status="active",
            plan_source="simulated_demo_plan"
        )
        db.add(care_plan_9)

        readings_9 = [
            ("2026-10-16T08:00:00+05:30", "blood_pressure", 160.0, 96.0, None, None),
            ("2026-10-16T08:05:00+05:30", "blood_glucose", None, None, 198.0, "fasting"),
            ("2026-10-17T08:00:00+05:30", "blood_pressure", 162.0, 96.0, None, None),
            ("2026-10-17T08:05:00+05:30", "blood_glucose", None, None, 205.0, "fasting"),
            ("2026-10-18T08:00:00+05:30", "blood_pressure", 164.0, 98.0, None, None),
            ("2026-10-18T08:05:00+05:30", "blood_glucose", None, None, 210.0, "fasting"),
        ]
        for idx, (ts, r_type, sys, dia, val, ctx) in enumerate(readings_9):
            db.add(Reading(
                id=f"reading-dual-9-{idx+1:03d}",
                patient_id="patient-009",
                type=r_type,
                recorded_at=ts,
                systolic_mmhg=sys,
                diastolic_mmhg=dia,
                value=val,
                unit="mmHg" if r_type == "blood_pressure" else "mg/dL",
                context=ctx,
                source="manual_entry",
                is_demo_data=True
            ))

        db.add(CareTask(
            id="task-901",
            patient_id="patient-009",
            task_type="reading",
            title="Morning dual telemetry log (BP + Fasting Glucose)",
            due_at="2026-10-18T08:30:00+05:30",
            status="completed",
            completed_at="2026-10-18T08:05:00+05:30",
            created_by="simulated_care_plan"
        ))

        db.add(FollowupFlag(
            id="flag-005",
            patient_id="patient-009",
            category="measurement_safety",
            priority="urgent",
            reason_code="MULTIMORBID_DUAL_CRISIS",
            reason="Concurrent Stage 2 Hypertension (164/98 mmHg) and uncontrolled fasting hyperglycemia (210 mg/dL).",
            recommended_action="Urgent cardio-metabolic review. Schedule comprehensive renal panel and titrate dual therapies.",
            source_rule_id="rule-bp-elevated-v1",
            status="open",
            created_at="2026-10-18T08:30:00+05:30",
            is_demo_data=True
        ))

    # 10. Patient 010: Priya Sengupta (Pre-Diabetes / Borderline Glycemic Elevation 118 mg/dL)
    patient_10 = db.query(Patient).filter(Patient.id == "patient-010").first()
    if not patient_10:
        patient_10 = Patient(
            id="patient-010",
            display_name="Priya Sengupta",
            age=44,
            conditions=["type_2_diabetes"],
            preferred_language="en",
            care_plan_id="plan-010",
            is_demo_data=True
        )
        db.add(patient_10)

        care_plan_10 = CarePlan(
            id="plan-010",
            patient_id="patient-010",
            conditions=["type_2_diabetes"],
            monitoring=[{"type": "blood_glucose", "unit": "mg/dL", "schedule": "weekly_fasting"}],
            medication_tasks_enabled=False,
            next_appointment="2026-11-12T14:00:00+05:30",
            plan_status="active",
            plan_source="simulated_demo_plan"
        )
        db.add(care_plan_10)

        glucose_history_10 = [
            ("2026-10-04T08:00:00+05:30", 114.0, "fasting"),
            ("2026-10-11T08:00:00+05:30", 116.0, "fasting"),
            ("2026-10-18T08:00:00+05:30", 118.0, "fasting"),
        ]
        for idx, (ts, val, ctx) in enumerate(glucose_history_10):
            db.add(Reading(
                id=f"reading-glu-10-{idx+1:03d}",
                patient_id="patient-010",
                type="blood_glucose",
                recorded_at=ts,
                value=val,
                unit="mg/dL",
                context=ctx,
                source="manual_entry",
                is_demo_data=True
            ))

        db.add(CareTask(
            id="task-1001",
            patient_id="patient-010",
            task_type="reading",
            title="Log weekly fasting glucose reading",
            due_at="2026-10-18T09:00:00+05:30",
            status="completed",
            completed_at="2026-10-18T08:00:00+05:30",
            created_by="simulated_care_plan"
        ))

    # Standard Rule Definitions
    rule_defs = [
        ("rule-missing-reading-v1", "missing_task", "all", "task_overdue_and_pending", "routine", "task_overdue", "check_patient_recording_assistance", "Clinical Practice Guideline Routine Task Monitoring v1.0"),
        ("rule-bp-elevated-v1", "measurement_safety", "blood_pressure", "systolic_gt_160", "urgent", "systolic_elevation_review", "repeat_reading_and_guideline_check", "ICMR / AHA 2023 Stage 2 Hypertension Triage Protocol"),
        ("rule-glucose-crisis-v1", "measurement_safety", "blood_glucose", "value_gt_250", "urgent", "glucose_crisis_review", "emergency_endocrinology_eval", "ADA 2024 Glycemic Emergency Triage Protocol")
    ]
    for r_id, cat, m_type, cond, prio, m_key, a_key, src in rule_defs:
        if not db.query(RuleDefinition).filter(RuleDefinition.rule_id == r_id).first():
            db.add(RuleDefinition(
                rule_id=r_id,
                category=cat,
                measurement_type=m_type,
                condition=cond,
                priority=prio,
                message_key=m_key,
                action_key=a_key,
                source=src,
                version=1,
                enabled=True
            ))

    db.commit()
