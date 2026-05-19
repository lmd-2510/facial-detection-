import { useEffect, useMemo, useState } from "react";
import type { User } from "../types/user";

interface SettingsPageProps {
  camerasCount: number;
  employeesCount: number;
  logsCount: number;
  user: User;
}

interface HealthSnapshot {
  status: "loading" | "ok" | "error";
  environment: string;
  database: string;
  redis: string;
}

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export default function SettingsPage({
  camerasCount,
  employeesCount,
  logsCount,
  user,
}: SettingsPageProps) {
  const [health, setHealth] = useState<HealthSnapshot>({
    status: "loading",
    environment: import.meta.env.MODE ?? "dev",
    database: "unknown",
    redis: "unknown",
  });

  useEffect(() => {
    const controller = new AbortController();

    async function loadHealth() {
      try {
        const response = await fetch(`${apiBaseUrl}/health`, {
          signal: controller.signal,
        });
        const body = (await response.json()) as Partial<HealthSnapshot> & {
          environment?: string;
          database?: string;
          redis?: string;
          status?: string;
        };
        setHealth({
          status: response.ok ? "ok" : "error",
          environment: body.environment ?? (import.meta.env.MODE ?? "dev"),
          database: body.database ?? "unknown",
          redis: body.redis ?? "unknown",
        });
      } catch (_error) {
        if (!controller.signal.aborted) {
          setHealth({
            status: "error",
            environment: import.meta.env.MODE ?? "dev",
            database: "unknown",
            redis: "unknown",
          });
        }
      }
    }

    void loadHealth();
    return () => controller.abort();
  }, []);

  const serviceItems = useMemo(
    () => [
      {
        label: "Backend API",
        value: health.status === "loading" ? "Checking..." : health.status === "ok" ? "Healthy" : "Unavailable",
        tone: health.status === "loading" ? "pending" : health.status === "ok" ? "success" : "error",
      },
      {
        label: "PostgreSQL",
        value: health.database === "ok" ? "Connected" : health.database === "unknown" ? "Checking..." : "Issue detected",
        tone: health.database === "ok" ? "success" : health.database === "unknown" ? "pending" : "error",
      },
      {
        label: "Redis queue",
        value: health.redis === "ok" ? "Connected" : health.redis === "unknown" ? "Checking..." : "Issue detected",
        tone: health.redis === "ok" ? "success" : health.redis === "unknown" ? "pending" : "error",
      },
      {
        label: "Worker / MinIO / Qdrant",
        value: "Coming later",
        tone: "none",
      },
    ],
    [health],
  );

  const configItems = [
    { label: "API base URL", value: apiBaseUrl },
    { label: "Environment", value: health.environment },
    { label: "Detector backend", value: "retinaface" },
    { label: "Embedding model", value: "Facenet512" },
    { label: "Match threshold", value: "0.70" },
    { label: "Anti-spoofing", value: "Off" },
  ];

  const ruleItems = [
    "One person only in each frame.",
    "Multiple faces are rejected immediately.",
    "Realtime access checks run every 2 seconds.",
    "Access is granted only when the best score passes the current threshold.",
  ];

  return (
    <section className="page-stack">
      <div className="page-header">
        <div>
          <p className="eyebrow">Configuration</p>
          <h2>System settings</h2>
        </div>
      </div>

      <div className="settings-sections">
        <div className="panel settings-card">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Session</p>
              <h2>Admin session</h2>
            </div>
            <span className={`status-pill ${user.role}`}>{user.role}</span>
          </div>
          <div className="settings-grid">
            <div>
              <span>Signed in as</span>
              <strong>{user.username}</strong>
            </div>
            <div>
              <span>Role</span>
              <strong>{user.role}</strong>
            </div>
            <div>
              <span>Created</span>
              <strong>{new Date(user.created_at).toLocaleString()}</strong>
            </div>
          </div>
        </div>

        <div className="panel settings-card">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Runtime</p>
              <h2>Current configuration</h2>
            </div>
          </div>
          <div className="settings-grid">
            {configItems.map((item) => (
              <div key={item.label}>
                <span>{item.label}</span>
                <strong>{item.value}</strong>
              </div>
            ))}
          </div>
        </div>

        <div className="panel settings-card">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Health</p>
              <h2>Service status</h2>
            </div>
          </div>
          <div className="settings-list">
            {serviceItems.map((item) => (
              <div className="settings-row" key={item.label}>
                <div>
                  <span>{item.label}</span>
                  <strong>{item.value}</strong>
                </div>
                <span className={`status-pill ${item.tone}`}>{item.value}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="panel settings-card">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Overview</p>
              <h2>Operational snapshot</h2>
            </div>
          </div>
          <div className="settings-grid">
            <div>
              <span>Employees</span>
              <strong>{employeesCount}</strong>
            </div>
            <div>
              <span>Access logs</span>
              <strong>{logsCount}</strong>
            </div>
            <div>
              <span>Cameras in dataset</span>
              <strong>{camerasCount}</strong>
            </div>
          </div>
        </div>

        <div className="panel settings-card">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Rules</p>
              <h2>Access policy</h2>
            </div>
          </div>
          <ul className="settings-rules">
            {ruleItems.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
