import { apiRequest } from "./client";
import type {
  EmbeddingJobResponse,
  Employee,
  EmployeePayload,
} from "../types/employee";

export function listEmployees(token: string): Promise<Employee[]> {
  return apiRequest<Employee[]>("/employees", { token });
}

export function createEmployee(
  token: string,
  payload: EmployeePayload,
): Promise<Employee> {
  return apiRequest<Employee>("/employees", {
    method: "POST",
    token,
    body: JSON.stringify(payload),
  });
}

export function updateEmployee(
  token: string,
  employeeId: number,
  payload: EmployeePayload,
): Promise<Employee> {
  return apiRequest<Employee>(`/employees/${employeeId}`, {
    method: "PUT",
    token,
    body: JSON.stringify(payload),
  });
}

export function deleteEmployee(token: string, employeeId: number): Promise<void> {
  return apiRequest<void>(`/employees/${employeeId}`, {
    method: "DELETE",
    token,
  });
}

export function queueEmbeddingJob(
  token: string,
  employeeId: number,
  imagePath: string,
): Promise<EmbeddingJobResponse> {
  return apiRequest<EmbeddingJobResponse>(`/employees/${employeeId}/embedding-jobs`, {
    method: "POST",
    token,
    body: JSON.stringify({ image_path: imagePath }),
  });
}
