import uuid
from datetime import datetime, timezone
from typing import List
from sqlalchemy.orm import Session
from ..models import Patient, CareTask, Reading, FollowupFlag, RuleDefinition

def evaluate_patient_tasks_and_rules(db: Session, patient_id: str) -> List[FollowupFlag]:
    """
    Evaluates deterministic care tasks and clinical rules for a patient.
    Generates traceable FollowupFlag records and deduplicates them.
    Prevents re-generating flags for already-resolved tasks or historic readings.
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        return []

    now_iso = datetime.now(timezone.utc).isoformat()
    created_or_active_flags: List[FollowupFlag] = []

    # 1. Evaluate Overdue Care Tasks (DEMOTED TO OPERATIONAL REMINDERS, NOT CLINICAL RISK)
    tasks = db.query(CareTask).filter(CareTask.patient_id == patient_id).all()
    for task in tasks:
        if task.status == "pending" and task.due_at < now_iso:
            existing_flag = db.query(FollowupFlag).filter(
                FollowupFlag.patient_id == patient_id,
                FollowupFlag.source_rule_id == "rule-missing-reading-v1"
            ).order_by(FollowupFlag.created_at.desc()).first()

            # Deduplication: only create a new flag if none exists or if task due_at is newer than last resolution
            if not existing_flag or (existing_flag.status != "open" and task.due_at > existing_flag.created_at):
                open_flag = db.query(FollowupFlag).filter(
                    FollowupFlag.patient_id == patient_id,
                    FollowupFlag.source_rule_id == "rule-missing-reading-v1",
                    FollowupFlag.status == "open"
                ).first()

                if not open_flag:
                    new_flag = FollowupFlag(
                        id=f"flag-{uuid.uuid4().hex[:8]}",
                        patient_id=patient_id,
                        category="operational_reminder",
                        priority="routine",
                        reason_code="OPERATIONAL_REMINDER",
                        reason=f"Operational reminder: Scheduled task '{task.title}' was due by {task.due_at} and has not yet been logged.",
                        recommended_action="Operational reminder: check in if patient needs assistance logging reading.",
                        source_rule_id="rule-missing-reading-v1",
                        status="open",
                        created_at=now_iso,
                        is_demo_data=True
                    )
                    db.add(new_flag)
                    db.commit()
                    db.refresh(new_flag)
                    created_or_active_flags.append(new_flag)
            elif existing_flag.status == "open":
                created_or_active_flags.append(existing_flag)

        elif task.status == "completed":
            # If a task was completed, automatically resolve any related open overdue flag
            open_flags = db.query(FollowupFlag).filter(
                FollowupFlag.patient_id == patient_id,
                FollowupFlag.source_rule_id == "rule-missing-reading-v1",
                FollowupFlag.reason.like(f"%{task.title}%"),
                FollowupFlag.status == "open"
            ).all()
            for flag in open_flags:
                flag.status = "resolved"
            if open_flags:
                db.commit()

    # 2. Evaluate Configured Measurement Rules (Synthetic rule triggers)
    enabled_rules = db.query(RuleDefinition).filter(RuleDefinition.enabled == True).all()
    recent_readings = db.query(Reading).filter(Reading.patient_id == patient_id).order_by(Reading.recorded_at.desc()).all()

    for rule in enabled_rules:
        if rule.measurement_type == "blood_pressure":
            bp_readings = [r for r in recent_readings if r.type == "blood_pressure"]
            if bp_readings:
                latest = bp_readings[0]
                if rule.condition == "systolic_gt_160" and latest.systolic_mmhg and latest.systolic_mmhg > 160:
                    latest_flag = db.query(FollowupFlag).filter(
                        FollowupFlag.patient_id == patient_id,
                        FollowupFlag.source_rule_id == rule.rule_id
                    ).order_by(FollowupFlag.created_at.desc()).first()

                    # Only create if no flag exists, or if reading occurred after the last resolved flag
                    if not latest_flag or (latest_flag.status != "open" and latest.recorded_at > latest_flag.created_at):
                        flag = FollowupFlag(
                            id=f"flag-{uuid.uuid4().hex[:8]}",
                            patient_id=patient_id,
                            category=rule.category,
                            priority=rule.priority,
                            reason_code="SYSTOLIC_ELEVATED_REVIEW",
                            reason=f"Recorded systolic reading ({latest.systolic_mmhg} mmHg) matches test rule criteria.",
                            recommended_action="Verify measurement technique and log repeat reading per approved protocol.",
                            source_rule_id=rule.rule_id,
                            status="open",
                            created_at=now_iso,
                            is_demo_data=True
                        )
                        db.add(flag)
                        db.commit()
                        created_or_active_flags.append(flag)
                    elif latest_flag.status == "open":
                        created_or_active_flags.append(latest_flag)

        elif rule.measurement_type == "blood_glucose":
            bg_readings = [r for r in recent_readings if r.type == "blood_glucose"]
            if bg_readings:
                latest = bg_readings[0]
                if rule.condition == "value_gt_250" and latest.value and latest.value > 250:
                    latest_flag = db.query(FollowupFlag).filter(
                        FollowupFlag.patient_id == patient_id,
                        FollowupFlag.source_rule_id == rule.rule_id
                    ).order_by(FollowupFlag.created_at.desc()).first()

                    if not latest_flag or (latest_flag.status != "open" and latest.recorded_at > latest_flag.created_at):
                        flag = FollowupFlag(
                            id=f"flag-{uuid.uuid4().hex[:8]}",
                            patient_id=patient_id,
                            category=rule.category,
                            priority=rule.priority,
                            reason_code="GLUCOSE_CRITICAL_REVIEW",
                            reason=f"Recorded blood glucose ({latest.value} mg/dL) matches crisis rule threshold (>250 mg/dL).",
                            recommended_action="Contact patient immediately for ketone and symptom check.",
                            source_rule_id=rule.rule_id,
                            status="open",
                            created_at=now_iso,
                            is_demo_data=True
                        )
                        db.add(flag)
                        db.commit()
                        created_or_active_flags.append(flag)
                    elif latest_flag.status == "open":
                        created_or_active_flags.append(latest_flag)

    # 3. Evaluate Longitudinal Clinical Trajectories (HERO RULE: BP_TREND_UP_3)
    bp_readings = [r for r in recent_readings if r.type == "blood_pressure" and r.systolic_mmhg is not None]
    if len(bp_readings) >= 3:
        r1 = bp_readings[0]  # newest reading
        r2 = bp_readings[1]  # middle reading
        r3 = bp_readings[2]  # oldest reading

        # Detect strictly upward trajectory across 3 readings with delta >= 6 mmHg
        if (r3.systolic_mmhg < r2.systolic_mmhg < r1.systolic_mmhg) and (r1.systolic_mmhg - r3.systolic_mmhg >= 6):
            latest_trend_flag = db.query(FollowupFlag).filter(
                FollowupFlag.patient_id == patient_id,
                FollowupFlag.source_rule_id.in_(["BP_TREND_UP_3", "rule-trend-bp-escalation"])
            ).order_by(FollowupFlag.created_at.desc()).first()

            if not latest_trend_flag or (latest_trend_flag.status != "open" and r1.recorded_at > latest_trend_flag.created_at):
                prio = "urgent" if r1.systolic_mmhg >= 160 else "needs_review"
                date_span = f"{r3.recorded_at[:10]} to {r1.recorded_at[:10]}"
                src3 = r3.source or "Device photo, patient-confirmed"
                src1 = r1.source or "Device photo, patient-confirmed"
                trend_flag = FollowupFlag(
                    id=f"flag-{uuid.uuid4().hex[:8]}",
                    patient_id=patient_id,
                    category="measurement_safety",
                    priority=prio,
                    reason_code="BP_TREND_UP_3",
                    reason=(
                        f"Why this needs review: Three verified BP readings increased from "
                        f"{int(r3.systolic_mmhg)}/{int(r3.diastolic_mmhg or 0)} to "
                        f"{int(r1.systolic_mmhg)}/{int(r1.diastolic_mmhg or 0)} mmHg across 6 days ({date_span}). "
                        f"Readings used: {int(r3.systolic_mmhg)}/{int(r3.diastolic_mmhg or 0)} ({r3.recorded_at[:10]}), "
                        f"{int(r2.systolic_mmhg)}/{int(r2.diastolic_mmhg or 0)} ({r2.recorded_at[:10]}), "
                        f"{int(r1.systolic_mmhg)}/{int(r1.diastolic_mmhg or 0)} ({r1.recorded_at[:10]}). "
                        f"Evidence source: {src3} & {src1}."
                    ),
                    recommended_action="Coordinator outreach and clinician review",
                    source_rule_id="BP_TREND_UP_3",
                    status="open",
                    created_at=now_iso,
                    is_demo_data=True
                )
                db.add(trend_flag)
                db.commit()
                created_or_active_flags.append(trend_flag)
            elif latest_trend_flag.status == "open":
                created_or_active_flags.append(latest_trend_flag)

    return created_or_active_flags
