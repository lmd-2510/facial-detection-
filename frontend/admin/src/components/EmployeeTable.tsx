import { FormEvent, useState } from "react";
import type { Employee } from "../types/employee";

interface EmployeeTableProps {
  employees: Employee[];
  isLoading: boolean;
  onEdit: (employee: Employee) => void;
  onDelete: (employeeId: number) => Promise<void>;
  onQueueEmbedding: (employeeId: number, file: File) => Promise<void>;
}

export default function EmployeeTable({
  employees,
  isLoading,
  onEdit,
  onDelete,
  onQueueEmbedding,
}: EmployeeTableProps) {
  const [imageFiles, setImageFiles] = useState<Record<number, File | null>>({});

  async function handleEmbeddingSubmit(
    event: FormEvent<HTMLFormElement>,
    employeeId: number,
  ) {
    event.preventDefault();
    const imageFile = imageFiles[employeeId];
    if (!imageFile) {
      return;
    }
    await onQueueEmbedding(employeeId, imageFile);
    setImageFiles({ ...imageFiles, [employeeId]: null });
  }

  if (isLoading) {
    return <div className="panel state-panel">Loading employees...</div>;
  }

  if (employees.length === 0) {
    return <div className="panel state-panel">No employees yet.</div>;
  }

  return (
    <div className="panel table-panel">
      <table>
        <thead>
          <tr>
            <th>Code</th>
            <th>Name</th>
            <th>Department</th>
            <th>Status</th>
            <th>Embedding</th>
            <th>Embedding image</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {employees.map((employee) => (
            <tr key={employee.id}>
              <td>{employee.code}</td>
              <td>{employee.name}</td>
              <td>{employee.department ?? "-"}</td>
              <td>
                <span className={`status-pill ${employee.status}`}>
                  {employee.status}
                </span>
              </td>
              <td>
                <span className={`status-pill ${employee.embedding_status}`}>
                  {employee.embedding_status}
                </span>
                {employee.embedding_error ? (
                  <p className="cell-note">{employee.embedding_error}</p>
                ) : null}
              </td>
              <td>
                <form
                  className="inline-form"
                  onSubmit={(event) => handleEmbeddingSubmit(event, employee.id)}
                >
                  <input
                    accept="image/*"
                    type="file"
                    onChange={(event) =>
                      setImageFiles({
                        ...imageFiles,
                        [employee.id]: event.target.files?.[0] ?? null,
                      })
                    }
                  />
                  <button className="small-button" type="submit">
                    Queue
                  </button>
                </form>
              </td>
              <td className="row-actions">
                <button className="small-button" onClick={() => onEdit(employee)}>
                  Edit
                </button>
                <button
                  className="danger-button"
                  onClick={() => void onDelete(employee.id)}
                >
                  Disable
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
