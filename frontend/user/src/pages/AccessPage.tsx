import { FormEvent, useState } from "react";
import { checkAccess, uploadAccessSnapshot } from "../api/access";
import CameraView from "../components/CameraView";
import ResultCard from "../components/ResultCard";
import type { AccessCheckResponse } from "../types/access";

interface AccessPageProps {
  token: string;
  onAccessQueued: () => Promise<void>;
}

export default function AccessPage({ token, onAccessQueued }: AccessPageProps) {
  const [cameraId, setCameraId] = useState("1");
  const [snapshotFile, setSnapshotFile] = useState<File | null>(null);
  const [imageKey, setImageKey] = useState("");
  const [result, setResult] = useState<AccessCheckResponse | null>(null);
  const [isChecking, setIsChecking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsChecking(true);
    setError(null);
    try {
      if (!snapshotFile) {
        setError("Choose a snapshot image first.");
        return;
      }
      const upload = await uploadAccessSnapshot(token, snapshotFile);
      const response = await checkAccess(token, {
        camera_id: Number(cameraId),
        image_key: upload.object_key,
      });
      setImageKey(upload.object_key);
      setResult(response);
      await onAccessQueued();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Cannot check access");
    } finally {
      setIsChecking(false);
    }
  }

  return (
    <section className="page-grid">
      <div className="page-stack">
        <div className="page-header">
          <div>
            <p className="eyebrow">Check access</p>
            <h2>Snapshot verification</h2>
          </div>
        </div>

        {error ? <div className="alert error">{error}</div> : null}

        <form className="panel form-panel" onSubmit={handleSubmit}>
          <label>
            Camera ID
            <input
              min={1}
              required
              type="number"
              value={cameraId}
              onChange={(event) => setCameraId(event.target.value)}
            />
          </label>
          <label>
            Snapshot image
            <input
              accept="image/*"
              required
              type="file"
              onChange={(event) =>
                setSnapshotFile(event.target.files?.[0] ?? null)
              }
            />
          </label>
          <button className="primary-button" disabled={isChecking} type="submit">
            {isChecking ? "Queueing..." : "Check access"}
          </button>
        </form>
      </div>

      <div className="page-stack">
        <CameraView imagePath={imageKey || snapshotFile?.name || ""} />
        <ResultCard result={result} />
      </div>
    </section>
  );
}
