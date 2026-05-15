import { useEffect, useState } from "react";
import {
  createEmployee,
  deleteEmployee,
  listEmployees,
  queueEmbeddingJob,
  updateEmployee,
  uploadEmployeeFaceImage,
} from "../api/employees";
import EmployeeForm from "../components/EmployeeForm";
import EmployeeTable from "../components/EmployeeTable";
import type { Employee, EmployeePayload } from "../types/employee";

interface EmployeePageProps {
  token: string;
  onEmployeesChange: (employees: Employee[]) => void;
}

export default function EmployeePage({
  token,
  onEmployeesChange,
}: EmployeePageProps) {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [editingEmployee, setEditingEmployee] = useState<Employee | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadEmployees() {
    setIsLoading(true);
    setError(null);
    try {
      const data = await listEmployees(token);
      setEmployees(data);
      onEmployeesChange(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Cannot load employees");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadEmployees();
  }, [token]);

  async function handleSubmit(payload: EmployeePayload) {
    setIsSaving(true);
    setError(null);
    setMessage(null);
    try {
      if (editingEmployee) {
        await updateEmployee(token, editingEmployee.id, payload);
        setMessage("Employee updated.");
      } else {
        await createEmployee(token, payload);
        setMessage("Employee created.");
      }
      setEditingEmployee(null);
      await loadEmployees();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Cannot save employee");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleDelete(employeeId: number) {
    setError(null);
    setMessage(null);
    try {
      await deleteEmployee(token, employeeId);
      setMessage("Employee disabled.");
      await loadEmployees();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Cannot disable employee");
    }
  }

  async function handleQueueEmbedding(employeeId: number, file: File) {
    setError(null);
    setMessage(null);
    try {
      const upload = await uploadEmployeeFaceImage(token, employeeId, file);
      if (upload.job_id) {
        setMessage(`Image uploaded and embedding job queued: ${upload.job_id}`);
      } else {
        const job = await queueEmbeddingJob(token, employeeId, upload.object_key);
        setMessage(`Embedding job queued: ${job.job_id}`);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Cannot queue embedding job");
    }
  }

  return (
    <section className="page-stack">
      <div className="page-header">
        <div>
          <p className="eyebrow">People</p>
          <h2>Employee management</h2>
        </div>
        <button className="secondary-button" onClick={() => void loadEmployees()}>
          Refresh
        </button>
      </div>

      {error ? <div className="alert error">{error}</div> : null}
      {message ? <div className="alert success">{message}</div> : null}

      <div className="split-layout">
        <EmployeeForm
          employee={editingEmployee}
          isSaving={isSaving}
          onCancelEdit={() => setEditingEmployee(null)}
          onSubmit={handleSubmit}
        />
        <EmployeeTable
          employees={employees}
          isLoading={isLoading}
          onDelete={handleDelete}
          onEdit={setEditingEmployee}
          onQueueEmbedding={handleQueueEmbedding}
        />
      </div>
    </section>
  );
}
