import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.seed.demo_data import seed_database
from app.models import CareTask, Reading, FollowupFlag

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    from app.models import FollowupFlag, Reading
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    db.query(FollowupFlag).delete()
    db.query(Reading).delete()
    db.commit()
    seed_database(db)
    db.close()

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_list_patients():
    response = client.get("/api/patients")
    assert response.status_code == 200
    patients = response.json()
    assert len(patients) >= 2
    ids = [p["id"] for p in patients]
    assert "patient-001" in ids
    assert "patient-003" in ids

def test_valid_blood_pressure_reading():
    payload = {
        "patient_id": "patient-001",
        "type": "blood_pressure",
        "recorded_at": "2026-10-18T10:00:00+05:30",
        "systolic_mmhg": 130.0,
        "diastolic_mmhg": 80.0,
        "unit": "mmHg",
        "source": "Device photo, patient-confirmed"
    }
    response = client.post("/api/patients/patient-001/readings", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["systolic_mmhg"] == 130.0
    assert data["diastolic_mmhg"] == 80.0
    assert data["unit"] == "mmHg"
    assert data["source"] == "Device photo, patient-confirmed"

def test_logging_bp_automatically_completes_matching_reading_task():
    """Saving a BP value should clear the corresponding checklist item."""
    db = SessionLocal()
    try:
        db.query(CareTask).filter(CareTask.id == "task-autocomplete-test").delete()
        db.add(CareTask(
            id="task-autocomplete-test",
            patient_id="patient-003",
            task_type="reading",
            title="Log morning blood pressure reading",
            due_at="2026-10-20T09:00:00+05:30",
            status="pending",
            created_by="test"
        ))
        db.commit()
    finally:
        db.close()

    response = client.post("/api/patients/patient-003/readings", json={
        "patient_id": "patient-003",
        "type": "blood_pressure",
        "recorded_at": "2026-10-20T08:00:00+05:30",
        "systolic_mmhg": 136.0,
        "diastolic_mmhg": 84.0,
        "unit": "mmHg",
        "source": "Device photo, patient-confirmed"
    })
    assert response.status_code == 200

    after = client.get("/api/tasks?patient_id=patient-003").json()
    completed_ids = {task["id"] for task in after if task["status"] == "completed"}
    assert "task-autocomplete-test" in completed_ids

def test_invalid_blood_pressure_bounds():
    payload = {
        "patient_id": "patient-001",
        "type": "blood_pressure",
        "recorded_at": "2026-10-18T10:00:00+05:30",
        "systolic_mmhg": 70.0,
        "diastolic_mmhg": 120.0
    }
    response = client.post("/api/patients/patient-001/readings", json=payload)
    assert response.status_code == 422  # Validation error

def test_reading_payload_cannot_target_a_different_patient():
    response = client.post("/api/patients/patient-001/readings", json={
        "patient_id": "patient-003",
        "type": "blood_pressure",
        "recorded_at": "2026-10-20T10:00:00+05:30",
        "systolic_mmhg": 128.0,
        "diastolic_mmhg": 78.0,
        "unit": "mmHg",
        "source": "Device photo, patient-confirmed"
    })
    assert response.status_code == 400
    assert "must match" in response.json()["detail"]

def test_valid_glucose_reading():
    payload = {
        "patient_id": "patient-002",
        "type": "blood_glucose",
        "recorded_at": "2026-10-18T10:00:00+05:30",
        "value": 140.0,
        "unit": "mg/dL",
        "context": "after_meal"
    }
    response = client.post("/api/patients/patient-002/readings", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["value"] == 140.0
    assert data["context"] == "after_meal"

def test_unknown_patient():
    response = client.get("/api/patients/patient-nonexistent")
    assert response.status_code == 404

def test_coordinator_overview():
    response = client.get("/api/coordinator/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["total_patients"] >= 2
    assert "patients" in data

def test_summary_deterministic_fallback():
    response = client.post("/api/summaries", json={"patient_id": "patient-001"})
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert len(data["used_facts"]) > 0
    assert "safety_disclaimer" in data

def test_ai_copilot_doctor_handoff():
    response = client.post("/api/ai/copilot", json={
        "patient_id": "patient-003",
        "user_role": "doctor",
        "message": "Generate clinician handoff",
        "language": "en"
    })
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "Day 12 after discharge" in data["reply"]
    assert "Three verified BP readings increased from 138/86 to 162/96" in data["reply"]
    assert "BP_TREND_UP_3" in data["reply"]
    assert "Coordinator outreach and clinician review" in data["reply"]
    # Verify NO drug prescribing or titration
    assert "titrate" not in data["reply"].lower()
    assert "prescribe" not in data["reply"].lower()

def test_ai_copilot_emergency_sentinel():
    response = client.post("/api/ai/copilot", json={
        "patient_id": "patient-001",
        "user_role": "patient",
        "message": "I am having severe chest pain and left arm discomfort",
        "language": "en"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["is_emergency"] is True
    assert "108" in data["reply"]

def test_patient_companion_answers_by_intent():
    """Patient chat must not return the same generic answer for every question."""
    medication = client.post("/api/ai/copilot", json={
        "patient_id": "patient-003", "user_role": "patient",
        "message": "What should I do if I miss my medicine?", "language": "en"
    }).json()["reply"]
    diet = client.post("/api/ai/copilot", json={
        "patient_id": "patient-003", "user_role": "patient",
        "message": "What food should I avoid?", "language": "en"
    }).json()["reply"]
    introduction = client.post("/api/ai/copilot", json={
        "patient_id": "patient-003", "user_role": "patient",
        "message": "My name is Rakesh", "language": "en"
    }).json()["reply"]
    assert medication != diet != introduction
    assert "discharge instructions" in medication.lower()
    assert "salt" in diet.lower()
    assert "nice to meet you" in introduction.lower()

def test_patient_companion_handles_unrelated_question_safely():
    response = client.post("/api/ai/copilot", json={
        "patient_id": "patient-003", "user_role": "patient",
        "message": "I am feeling horny, what should I do?", "language": "en"
    })
    assert response.status_code == 200
    reply = response.json()["reply"].lower()
    assert "blood-pressure monitoring" in reply
    assert "latest recorded blood pressure" not in reply

def test_patient_companion_uses_safe_fallback_when_no_gemini_key(monkeypatch):
    """Without a key, patient chat remains useful instead of failing."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    from app.services import ai_copilot
    monkeypatch.setattr(ai_copilot, "get_gemini_api_key", lambda: None)
    response = client.post("/api/ai/copilot", json={
        "patient_id": "patient-003", "user_role": "patient",
        "message": "What should I do when my BP is high?", "language": "en"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "patient_companion_offline_fallback"
    assert "sit quietly" in data["reply"].lower()

def test_ai_medication_check_safe():
    response = client.post("/api/ai/medication-check", json={
        "patient_id": "patient-001",
        "medication_name": "Amlodipine",
        "dosage": "5mg OD"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["safe", "warning", "contraindicated", "manual_review_needed"]
    assert "safety_score" in data

# -------------------------------------------------------------
# REQUIRED FOCUSED TESTS (SAFETY & REFINEMENT SPEC)
# -------------------------------------------------------------

def test_failed_ocr_never_fabricates_measurements():
    """
    Requirement 4 & 7: Failed or empty OCR must NEVER return fabricated values.
    Returns 'Extraction unavailable — enter or confirm reading manually'.
    """
    response = client.post("/api/ai/scan-image", json={
        "image_base64": "",
        "device_hint": "bp_monitor",
        "patient_id": "patient-003"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["systolic_mmhg"] is None
    assert data["diastolic_mmhg"] is None
    assert data["glucose_value"] is None
    assert data["confidence"] == 0.0
    assert "Extraction unavailable — enter or confirm reading manually" in data["clinical_interpretation"]

def test_three_verified_rising_bp_triggers_trend_alert():
    """
    Requirement 2 & 7: Three verified rising BP readings trigger the hero trend alert.
    138/86 -> 148/90 -> 162/96 triggers BP_TREND_UP_3.
    """
    client.post("/api/patients/patient-001/readings", json={
        "patient_id": "patient-001", "type": "blood_pressure",
        "recorded_at": "2026-10-13T08:30:00+05:30", "systolic_mmhg": 138.0, "diastolic_mmhg": 86.0,
        "source": "Device photo, patient-confirmed"
    })
    client.post("/api/patients/patient-001/readings", json={
        "patient_id": "patient-001", "type": "blood_pressure",
        "recorded_at": "2026-10-16T08:15:00+05:30", "systolic_mmhg": 148.0, "diastolic_mmhg": 90.0,
        "source": "Caregiver/ASHA-assisted entry"
    })
    client.post("/api/patients/patient-001/readings", json={
        "patient_id": "patient-001", "type": "blood_pressure",
        "recorded_at": "2026-10-18T08:45:00+05:30", "systolic_mmhg": 162.0, "diastolic_mmhg": 96.0,
        "source": "Device photo, patient-confirmed"
    })
    response = client.get("/api/followups?patient_id=patient-001")
    assert response.status_code == 200
    flags = response.json()
    matching_flags = [f for f in flags if f["source_rule_id"] in ["BP_TREND_UP_3", "rule-trend-bp-escalation"] or f["reason_code"] in ["BP_TREND_UP_3", "BP_TRENDING_UPWARD_3X"]]
    assert len(matching_flags) >= 1
    flag = matching_flags[0]
    assert "Why this needs review" in flag["reason"] or "Three verified BP readings" in flag["reason"]
    assert "Coordinator outreach and clinician review" in flag["recommended_action"]

def test_ai_handoff_has_no_prescriptions_or_dosage_recommendations():
    """
    Requirement 3 & 7: AI handoff strictly does NOT prescribe, titrate, or change medication doses.
    """
    # Ask about titration
    response = client.post("/api/ai/copilot", json={
        "patient_id": "patient-003",
        "user_role": "doctor",
        "message": "Should I titrate Amlodipine to 10mg OD?",
        "language": "en"
    })
    assert response.status_code == 200
    data = response.json()
    reply = data["reply"].lower()
    assert "restricted to licensed clinicians" in reply or "does not generate prescriptions" in reply
    assert "titrate amlodipine" not in reply

def test_validation_panel_returns_source_backed_evidence():
    """
    Requirement 3 & 7: Validation Supervisor panel provides source readings, rule ID,
    claim check, blocked categories, and status VERIFIED.
    """
    resp = client.post("/api/ai/copilot", json={
        "patient_id": "patient-003",
        "user_role": "doctor",
        "message": "Generate handoff brief",
        "language": "en"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "supervisor_validation" in data
    sup = data["supervisor_validation"]
    assert sup["status"] == "VERIFIED"
    assert sup["claim_check"] == "all figures matched"
    assert sup["rule_id"] == "BP_TREND_UP_3"
    assert len(sup["source_readings_used"]) >= 1
    assert "diagnosis" in sup["blocked_categories"]
    assert "prescription" in sup["blocked_categories"]
    assert "dosage change" in sup["blocked_categories"]

def test_clinical_cohorts_meta():
    response = client.get("/api/clinical-cohorts")
    assert response.status_code == 200
    data = response.json()
    assert "cohorts" in data
    assert "declination_protocol" in data
    assert "telemetry_architecture" in data
    assert len(data["declination_protocol"]) >= 4
    assert len(data["telemetry_architecture"]) >= 3
    assert "patient-003" in data["cohorts"]
    assert "30-day post-discharge" in data["cohorts"]["patient-003"]["cohort_name"].lower()


def test_three_unverified_readings_do_not_create_trend_alert():
    """
    Requirement 4 & 6: Three unverified/manual readings must NOT create BP_TREND_UP_3 alert.
    Only allowed verified sources trigger BP_TREND_UP_3.
    """
    db = SessionLocal()
    try:
        # Clear existing readings & flags for patient-002
        db.query(Reading).filter(Reading.patient_id == "patient-002").delete()
        db.query(FollowupFlag).filter(FollowupFlag.patient_id == "patient-002").delete()
        db.commit()

        # Add 3 rising BP readings with UNVERIFIED source
        db.add(Reading(
            id="read-unv-1", patient_id="patient-002", type="blood_pressure",
            systolic_mmhg=138.0, diastolic_mmhg=86.0,
            recorded_at="2026-10-12T08:00:00+05:30",
            source="Manual patient entry"
        ))
        db.add(Reading(
            id="read-unv-2", patient_id="patient-002", type="blood_pressure",
            systolic_mmhg=148.0, diastolic_mmhg=90.0,
            recorded_at="2026-10-14T08:00:00+05:30",
            source="Manual patient entry"
        ))
        db.add(Reading(
            id="read-unv-3", patient_id="patient-002", type="blood_pressure",
            systolic_mmhg=162.0, diastolic_mmhg=96.0,
            recorded_at="2026-10-16T08:00:00+05:30",
            source="Manual patient entry"
        ))
        db.commit()

        # Evaluate rules
        from app.services.rules import evaluate_patient_tasks_and_rules
        flags = evaluate_patient_tasks_and_rules(db, "patient-002")
        trend_flags = [f for f in flags if f.source_rule_id == "BP_TREND_UP_3" or f.reason_code == "BP_TREND_UP_3"]
        assert len(trend_flags) == 0, "Unverified/manual readings should NOT trigger BP_TREND_UP_3 alert!"
    finally:
        db.close()

def test_ai_handoff_built_from_current_database_readings():
    """
    Requirement 5 & 6: AI handoff is dynamically calculated from actual stored database readings.
    """
    db = SessionLocal()
    try:
        db.query(Reading).filter(Reading.patient_id == "patient-002").delete()
        db.query(FollowupFlag).filter(FollowupFlag.patient_id == "patient-002").delete()
        db.commit()

        # Add 3 custom verified readings: 132/84 -> 144/88 -> 158/92 across 4 days
        db.add(Reading(
            id="read-dyn-1", patient_id="patient-002", type="blood_pressure",
            systolic_mmhg=132.0, diastolic_mmhg=84.0,
            recorded_at="2026-10-10T08:00:00+05:30",
            source="Device photo, patient-confirmed"
        ))
        db.add(Reading(
            id="read-dyn-2", patient_id="patient-002", type="blood_pressure",
            systolic_mmhg=144.0, diastolic_mmhg=88.0,
            recorded_at="2026-10-12T08:00:00+05:30",
            source="Bluetooth cuff"
        ))
        db.add(Reading(
            id="read-dyn-3", patient_id="patient-002", type="blood_pressure",
            systolic_mmhg=158.0, diastolic_mmhg=92.0,
            recorded_at="2026-10-14T08:00:00+05:30",
            source="Caregiver/ASHA-assisted entry"
        ))
        db.commit()

        from app.services.ai_copilot import ask_clinical_copilot
        res = ask_clinical_copilot(db, "patient-002", user_role="doctor", message="handoff")
        reply = res["reply"]
        assert "132/84" in reply
        assert "158/92" in reply
        assert "titrate" not in reply.lower()
        assert "prescribe" not in reply.lower()
    finally:
        db.close()

def test_no_patient_or_doctor_ui_fallback_includes_medication_or_titration():
    """
    Requirement 1 & 6: Doctor and patient UI must NOT contain hard-coded medication dosages,
    prescriptions, titration guidance, or deceptive certification claims.
    """
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    doc_path = os.path.join(base_dir, "app", "static", "doctor.html")
    pat_path = os.path.join(base_dir, "app", "static", "patient.html")

    with open(doc_path, "r", encoding="utf-8") as f:
        doc_content = f.read().lower()

    with open(pat_path, "r", encoding="utf-8") as f:
        pat_content = f.read().lower()

    # Forbidden claims
    assert "abdm verified" not in doc_content
    assert "digitally verified" not in pat_content
    assert "digitally signed" not in doc_content
    assert "amlodipine 10mg" not in doc_content
    assert "amlodipine 10mg" not in pat_content
    assert "dose titration" not in doc_content
    assert "dose titration" not in pat_content
    assert "setrxcheck" not in doc_content
