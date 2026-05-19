import { useEffect, useState } from "react";
import { listCameras } from "../api/cameras";
import CameraForm from "../components/CameraForm";
import type { Camera } from "../types/camera";

interface CameraPageProps {
  token: string;
  onCamerasChange: (cameras: Camera[]) => void;
}

export default function CameraPage({ token, onCamerasChange }: CameraPageProps) {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [showInactive, setShowInactive] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const visibleCameras = showInactive
    ? cameras
    : cameras.filter((camera) => camera.status === "active");
  const activeCount = cameras.filter((camera) => camera.status === "active").length;
  const inactiveCount = cameras.length - activeCount;

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

  return (
    <section className="page-stack">
      <div className="page-header">
        <div>
          <p className="eyebrow">Entry points</p>
          <h2>Camera management</h2>
        </div>
        <div className="page-header-actions">
          <button
            className="secondary-button"
            onClick={() => setShowInactive((current) => !current)}
            type="button"
          >
            {showInactive ? "Hide inactive" : `Show inactive (${inactiveCount})`}
          </button>
          <button className="secondary-button" onClick={() => void loadCameras()}>
            Refresh
          </button>
        </div>
      </div>

      {error ? <div className="alert error">{error}</div> : null}

      <div className="split-layout">
        <CameraForm />
        <div className="panel table-panel">
          {isLoading ? (
            <div className="state-panel">Loading cameras...</div>
          ) : visibleCameras.length === 0 ? (
            <div className="state-panel">No cameras yet.</div>
          ) : (
            <>
              <div className="camera-list-summary">
                <span>{activeCount} active camera(s)</span>
                <span>{inactiveCount} archived camera(s)</span>
              </div>
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
                  {visibleCameras.map((camera) => (
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
            </>
          )}
        </div>
      </div>
    </section>
  );
}
