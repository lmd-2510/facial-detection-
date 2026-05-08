import { FormEvent, useState } from "react";
import type { Employee } from "../types/employee";

interface EmployeeTableProps {
  employees: Employee[];
  isLoading: boolean;
  onEdit: (employee: Employee) => void;
  onDelete: (employeeId: number) => Promise<void>;
  onQueueEmbedding: (employeeId: number, imagePath: string) => Promise<void>;
}

export default function EmployeeTable({
  employees,
  isLoading,
  onEdit,
  onDelete,
  onQueueEmbedding,
}: EmployeeTableProps) {
  const [imagePaths, setImagePaths] = useState<Record<number, string>>({});

  async function handleEmbeddingSubmit(
    event: FormEvent<HTMLFormElement>,
    employeeId: number,
  ) {
    event.preventDefault();
    const imagePath = imagePaths[employeeId]?.trim();
    if (!imagePath) {
      return;
    }
    await onQueueEmbedding(employeeId, imagePath);
    setImagePaths({ ...imagePaths, [employeeId]: "" });
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
            <th>Embedding image path</th>
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
                <form
                  className="inline-form"
                  onSubmit={(event) => handleEmbeddingSubmit(event, employee.id)}
                >
                  <input
                    placeholder="/app/storage/uploads/employee_1.jpg"
                    value={imagePaths[employee.id] ?? ""}
                    onChange={(event) =>
                      setImagePaths({
                        ...imagePaths,
                        [employee.id]: event.target.value,
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
