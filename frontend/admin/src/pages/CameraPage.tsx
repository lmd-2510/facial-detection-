import { useEffect, useState } from "react";
import { createCamera, listCameras } from "../api/cameras";
import CameraForm from "../components/CameraForm";
import type { Camera, CameraPayload } from "../types/camera";

interface CameraPageProps {
  token: string;
  onCamerasChange: (cameras: Camera[]) => void;
}

export default function CameraPage({ token, onCamerasChange }: CameraPageProps) {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  async function loadCameras() {
    setIsLoading(true);
    setError(null);
    try {
      const data = await listCameras(token);
      setCameras(data);
      onCamerasChange(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Cannot load cameras");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadCameras();
  }, [token]);

  async function handleCreateCamera(payload: CameraPayload) {
    setIsSaving(true);
    setError(null);
    setMessage(null);
    try {
      await createCamera(token, payload);
      setMessage("Camera created.");
      await loadCameras();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Cannot create camera");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <section className="page-stack">
      <div className="page-header">
        <div>
          <p className="eyebrow">Entry points</p>
          <h2>Camera management</h2>
        </div>
        <button className="secondary-button" onClick={() => void loadCameras()}>
          Refresh
        </button>
      </div>

      {error ? <div className="alert error">{error}</div> : null}
      {message ? <div className="alert success">{message}</div> : null}

      <div className="split-layout">
        <CameraForm isSaving={isSaving} onSubmit={handleCreateCamera} />
        <div className="panel table-panel">
          {isLoading ? (
            <div className="state-panel">Loading cameras...</div>
          ) : cameras.length === 0 ? (
            <div className="state-panel">No cameras yet.</div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Location</th>
                  <th>Stream</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {cameras.map((camera) => (
                  <tr key={camera.id}>
                    <td>{camera.name}</td>
                    <td>{camera.location ?? "-"}</td>
                    <td className="path-cell">{camera.stream_url ?? "-"}</td>
                    <td>
                      <span className={`status-pill ${camera.status}`}>
                        {camera.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </section>
  );
}
