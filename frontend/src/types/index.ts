export type Condition = "hypertension" | "type_2_diabetes";

export interface Patient {
  id: string;
  display_name: string;
  age: number;
  conditions: string[];
  preferred_language: string;
  care_plan_id?: string;
  is_demo_data: boolean;
}

export interface CarePlan {
  id: string;
  patient_id: string;
  conditions: string[];
  monitoring: Array<{
    type: string;
    unit: string;
    schedule: string;
  }>;
  medication_tasks_enabled: boolean;
  next_appointment?: string;
  plan_status: string;
  plan_source: string;
}

export interface Reading {
  id: string;
  patient_id: string;
  type: "blood_pressure" | "blood_glucose";
  recorded_at: string;
  systolic_mmhg?: number;
  diastolic_mmhg?: number;
  value?: number;
  unit?: string;
  context?: "fasting" | "before_meal" | "after_meal" | "bedtime" | "unspecified";
  source: string;
  is_demo_data: boolean;
}

export interface CareTask {
  id: string;
  patient_id: string;
  task_type: "reading" | "medication" | "checkin";
  title: string;
  due_at: string;
  status: "pending" | "completed" | "skipped" | "needs_help" | "not_applicable";
  completed_at?: string;
  created_by: string;
}

export interface FollowupFlag {
  id: string;
  patient_id: string;
  category: "missing_task" | "data_quality" | "measurement_safety";
  priority: "routine" | "needs_review" | "urgent";
  reason_code: string;
  reason: string;
  recommended_action: string;
  source_rule_id: string;
  status: "open" | "resolved" | "dismissed";
  created_at: string;
  is_demo_data: boolean;
}

export interface CoordinatorOverviewItem {
  patient_id: string;
  patient_name: string;
  conditions: string[];
  open_flags_count: number;
  pending_tasks_count: number;
  latest_reading?: Reading;
  next_appointment?: string;
  highest_priority_flag?: FollowupFlag;
}

export interface CoordinatorOverview {
  total_patients: number;
  total_open_flags: number;
  total_pending_tasks: number;
  patients: CoordinatorOverviewItem[];
}

export interface PatientSummary {
  patient_id: string;
  summary: string;
  used_facts: string[];
  is_ai_generated: boolean;
  fallback_used: boolean;
  safety_disclaimer: string;
}
