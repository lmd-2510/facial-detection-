import { FormEvent, useEffect, useState } from "react";
import type { Camera, CameraPayload, CameraStatus } from "../types/camera";

interface CameraFormProps {
  camera?: Camera | null;
  isSaving: boolean;
  onCancelEdit: () => void;
  onSubmit: (payload: CameraPayload) => Promise<void>;
}

const initialForm: CameraPayload = {
  name: "",
  location: "",
  stream_url: "",
  status: "active",
};

export default function CameraForm({
  camera,
  isSaving,
  onCancelEdit,
  onSubmit,
}: CameraFormProps) {
  const [form, setForm] = useState<CameraPayload>(initialForm);

  useEffect(() => {
    if (camera) {
      setForm({
        name: camera.name,
        location: camera.location ?? "",
        stream_url: camera.stream_url ?? "",
        status: camera.status,
      });
      return;
    }

    setForm(initialForm);
  }, [camera]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await onSubmit({
      name: form.name.trim(),
      location: form.location?.trim() || null,
      stream_url: form.stream_url?.trim() || null,
      status: form.status,
    });
    if (!camera) {
      setForm(initialForm);
    }
  }

  return (
    <form className="panel form-panel" onSubmit={handleSubmit}>
      <div className="panel-heading">
        <div>
          <p className="eyebrow">{camera ? "Edit camera" : "Entry point"}</p>
          <h2>{camera ? camera.name : "Add camera"}</h2>
        </div>
        {camera ? (
          <button className="ghost-button" onClick={onCancelEdit} type="button">
            Cancel
          </button>
        ) : null}
      </div>

      <label>
        Name
        <input
          required
          maxLength={150}
          value={form.name}
          onChange={(event) => setForm({ ...form, name: event.target.value })}
        />
      </label>

      <label>
        Location
        <input
          maxLength={255}
          value={form.location ?? ""}
          onChange={(event) => setForm({ ...form, location: event.target.value })}
        />
      </label>

      <label>
        Stream URL
        <input
          value={form.stream_url ?? ""}
          onChange={(event) =>
            setForm({ ...form, stream_url: event.target.value })
          }
        />
      </label>

      <label>
        Status
        <select
          value={form.status}
          onChange={(event) =>
            setForm({ ...form, status: event.target.value as CameraStatus })
          }
        >
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
      </label>

      <button className="primary-button" disabled={isSaving} type="submit">
        {isSaving ? "Saving..." : camera ? "Update camera" : "Create camera"}
      </button>
    </form>
  );
}
