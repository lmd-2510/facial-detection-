import type { User } from "../types/user";

interface SettingsPageProps {
  user: User;
}

export default function SettingsPage({ user }: SettingsPageProps) {
  return (
    <section className="page-stack">
      <div className="page-header">
        <div>
          <p className="eyebrow">Session</p>
          <h2>Settings</h2>
        </div>
      </div>

      <div className="panel settings-grid">
        <div>
          <span>Signed in as</span>
          <strong>{user.username}</strong>
        </div>
        <div>
          <span>Role</span>
          <strong>{user.role}</strong>
        </div>
        <div>
          <span>API base URL</span>
          <strong>{import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"}</strong>
        </div>
      </div>
    </section>
  );
}
