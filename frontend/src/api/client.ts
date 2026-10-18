import { 
  Patient, 
  CarePlan, 
  Reading, 
  CareTask, 
  FollowupFlag, 
  CoordinatorOverview, 
  PatientSummary 
} from "../types";

const API_BASE = "http://127.0.0.1:8000/api";

export async function fetchPatients(): Promise<Patient[]> {
  const res = await fetch(`${API_BASE}/patients`);
  if (!res.ok) throw new Error("Failed to fetch patients");
  return res.json();
}

export async function fetchPatient(id: string): Promise<Patient> {
  const res = await fetch(`${API_BASE}/patients/${id}`);
  if (!res.ok) throw new Error("Failed to fetch patient details");
  return res.json();
}

export async function fetchCarePlan(patientId: string): Promise<CarePlan> {
  const res = await fetch(`${API_BASE}/patients/${patientId}/care-plan`);
  if (!res.ok) throw new Error("Failed to fetch care plan");
  return res.json();
}

export async function fetchReadings(patientId: string): Promise<Reading[]> {
  const res = await fetch(`${API_BASE}/patients/${patientId}/readings`);
  if (!res.ok) throw new Error("Failed to fetch readings");
  return res.json();
}

export async function createReading(reading: Partial<Reading>): Promise<Reading> {
  const res = await fetch(`${API_BASE}/patients/${reading.patient_id}/readings`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(reading),
  });
  if (!res.ok) {
    const errorData = await res.json();
    throw new Error(errorData.detail || "Failed to submit reading");
  }
  return res.json();
}

export async function fetchTasks(patientId: string): Promise<CareTask[]> {
  const res = await fetch(`${API_BASE}/patients/${patientId}/tasks`);
  if (!res.ok) throw new Error("Failed to fetch care tasks");
  return res.json();
}

export async function updateTaskStatus(taskId: string, status: CareTask["status"]): Promise<CareTask> {
  const res = await fetch(`${API_BASE}/tasks/${taskId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) throw new Error("Failed to update task status");
  return res.json();
}

export async function fetchFollowups(patientId?: string): Promise<FollowupFlag[]> {
  const url = patientId ? `${API_BASE}/followups?patient_id=${patientId}` : `${API_BASE}/followups`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch follow-up flags");
  return res.json();
}

export async function resolveFollowup(flagId: string): Promise<FollowupFlag> {
  const res = await fetch(`${API_BASE}/followups/${flagId}/resolve`, { method: "PATCH" });
  if (!res.ok) throw new Error("Failed to resolve flag");
  return res.json();
}

export async function fetchCoordinatorOverview(): Promise<CoordinatorOverview> {
  const res = await fetch(`${API_BASE}/coordinator/overview`);
  if (!res.ok) throw new Error("Failed to fetch coordinator overview");
  return res.json();
}

export async function fetchSummary(patientId: string): Promise<PatientSummary> {
  const res = await fetch(`${API_BASE}/summaries`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ patient_id: patientId }),
  });
  if (!res.ok) throw new Error("Failed to fetch summary");
  return res.json();
}
