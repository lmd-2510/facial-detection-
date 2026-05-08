export type EmployeeStatus = "active" | "inactive";

export interface Employee {
  id: number;
  code: string;
  name: string;
  department: string | null;
  status: EmployeeStatus;
  created_at: string;
}

export interface EmployeePayload {
  code: string;
  name: string;
  department?: string | null;
  status: EmployeeStatus;
}

export interface EmbeddingJobResponse {
  job_id: string;
  type: string;
  employee_id: number;
  image_path: string;
  queue_name: string;
  message: string;
}
