import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.seed.demo_data import seed_database

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
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
    assert "patient-002" in ids

def test_valid_blood_pressure_reading():
    payload = {
        "patient_id": "patient-001",
        "type": "blood_pressure",
        "recorded_at": "2026-10-18T10:00:00+05:30",
        "systolic_mmhg": 130.0,
        "diastolic_mmhg": 80.0,
        "unit": "mmHg"
    }
    response = client.post("/api/patients/patient-001/readings", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["systolic_mmhg"] == 130.0
    assert data["diastolic_mmhg"] == 80.0
    assert data["unit"] == "mmHg"

def test_invalid_blood_pressure_bounds():
    # Systolic less than diastolic -> must fail
    payload = {
        "patient_id": "patient-001",
        "type": "blood_pressure",
        "recorded_at": "2026-10-18T10:00:00+05:30",
        "systolic_mmhg": 70.0,
        "diastolic_mmhg": 120.0
    }
    response = client.post("/api/patients/patient-001/readings", json=payload)
    assert response.status_code == 422  # Validation error

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


def test_ai_copilot_doctor():
    response = client.post("/api/ai/copilot", json={
        "patient_id": "patient-001",
        "user_role": "doctor",
        "message": "What is the recommended next step for blood pressure control?",
        "language": "en"
    })
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert len(data["reply"]) > 10
    assert data["is_emergency"] is False
    assert len(data["citations"]) > 0

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

def test_ai_medication_check():
    response = client.post("/api/ai/medication-check", json={
        "patient_id": "patient-001",
        "medication_name": "Amlodipine",
        "dosage": "5mg OD"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["safe", "warning", "contraindicated"]
    assert "safety_score" in data

def test_ai_scan_image():
    response = client.post("/api/ai/scan-image", json={
        "image_base64": "",
        "device_hint": "bp_monitor",
        "patient_id": "patient-001"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["detected_device"] == "digital_bp_monitor"
    assert data["systolic_mmhg"] is not None

def test_clinical_trend_alert():
    # Ingest 3 consecutive escalating readings for patient-001 (138 -> 148 -> 162 mmHg)
    client.post("/api/patients/patient-001/readings", json={
        "patient_id": "patient-001", "type": "blood_pressure",
        "recorded_at": "2026-10-19T10:00:00+05:30", "systolic_mmhg": 138.0, "diastolic_mmhg": 86.0
    })
    client.post("/api/patients/patient-001/readings", json={
        "patient_id": "patient-001", "type": "blood_pressure",
        "recorded_at": "2026-10-19T11:00:00+05:30", "systolic_mmhg": 148.0, "diastolic_mmhg": 90.0
    })
    client.post("/api/patients/patient-001/readings", json={
        "patient_id": "patient-001", "type": "blood_pressure",
        "recorded_at": "2026-10-19T12:00:00+05:30", "systolic_mmhg": 162.0, "diastolic_mmhg": 96.0
    })
    response = client.get("/api/followups?patient_id=patient-001")
    assert response.status_code == 200
    flags = response.json()
    reason_codes = [f["reason_code"] for f in flags]
    assert "BP_TRENDING_UPWARD_3X" in reason_codes


def test_clinical_cohorts_meta():
    response = client.get("/api/clinical-cohorts")
    assert response.status_code == 200
    data = response.json()
    assert "cohorts" in data
    assert "declination_protocol" in data
    assert "telemetry_architecture" in data
    assert len(data["declination_protocol"]) >= 4
    assert len(data["telemetry_architecture"]) >= 3
    # Check Cohort A Post-PCI is defined
    assert "patient-001" in data["cohorts"]
    assert "30-Day Post-PCI" in data["cohorts"]["patient-001"]["cohort_name"]

def test_tier2_clinical_supervisor_validation():
    # Test Copilot returns supervisor audit report
    resp = client.post("/api/ai/copilot", json={
        "patient_id": "patient-001",
        "user_role": "doctor",
        "message": "Review Metformin dosage in CKD Stage 3",
        "language": "en"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "supervisor_validation" in data
    sup = data["supervisor_validation"]
    assert sup["supervisor_status"] == "CLINICALLY_VERIFIED"
    assert sup["fact_check_score"] == "100%"
    assert sup["hallucination_risk"] == "0.0%"
    assert len(sup["safety_rules_passed"]) >= 3
    assert len(sup["verified_ground_truth"]) >= 4

    # Test Medication Check returns supervisor validation
    med_resp = client.post("/api/ai/medication-check", json={
        "patient_id": "patient-001",
        "medication_name": "Amlodipine",
        "dosage": "5mg OD"
    })
    assert med_resp.status_code == 200
    med_data = med_resp.json()
    assert "supervisor_validation" in med_data
    assert med_data["supervisor_validation"]["supervisor_status"] == "CLINICALLY_VERIFIED"
