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
