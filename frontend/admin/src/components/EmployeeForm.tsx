import { FormEvent, useEffect, useState } from "react";
import type { Employee, EmployeePayload, EmployeeStatus } from "../types/employee";

interface EmployeeFormProps {
  employee?: Employee | null;
  isSaving: boolean;
  onCancelEdit: () => void;
  onSubmit: (payload: EmployeePayload) => Promise<void>;
}

const initialForm: EmployeePayload = {
  code: "",
  name: "",
  department: "",
  status: "active",
};

export default function EmployeeForm({
  employee,
  isSaving,
  onCancelEdit,
  onSubmit,
}: EmployeeFormProps) {
  const [form, setForm] = useState<EmployeePayload>(initialForm);

  useEffect(() => {
    if (employee) {
      setForm({
        code: employee.code,
        name: employee.name,
        department: employee.department ?? "",
        status: employee.status,
      });
      return;
    }

    setForm(initialForm);
  }, [employee]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await onSubmit({
      ...form,
      code: form.code.trim(),
      name: form.name.trim(),
      department: form.department?.trim() || null,
    });
    if (!employee) {
      setForm(initialForm);
    }
  }

  return (
    <form className="panel form-panel" onSubmit={handleSubmit}>
      <div className="panel-heading">
        <div>
          <p className="eyebrow">{employee ? "Edit record" : "New record"}</p>
          <h2>{employee ? employee.name : "Register employee"}</h2>
        </div>
        {employee ? (
          <button className="ghost-button" onClick={onCancelEdit} type="button">
            Cancel
          </button>
        ) : null}
      </div>

      <label>
        Employee code
        <input
          required
          maxLength={50}
          value={form.code}
          onChange={(event) => setForm({ ...form, code: event.target.value })}
        />
      </label>

      <label>
        Full name
        <input
          required
          maxLength={150}
          value={form.name}
          onChange={(event) => setForm({ ...form, name: event.target.value })}
        />
      </label>

      <label>
        Department
        <input
          maxLength={150}
          value={form.department ?? ""}
          onChange={(event) =>
            setForm({ ...form, department: event.target.value })
          }
        />
      </label>

      <label>
        Status
        <select
          value={form.status}
          onChange={(event) =>
            setForm({ ...form, status: event.target.value as EmployeeStatus })
          }
        >
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
      </label>

      <button className="primary-button" disabled={isSaving} type="submit">
        {isSaving ? "Saving..." : employee ? "Update employee" : "Create employee"}
      </button>
    </form>
  );
}
