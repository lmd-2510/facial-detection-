import type { User } from "../types/auth";

interface ProfilePageProps {
  user: User;
}

export default function ProfilePage({ user }: ProfilePageProps) {
  return (
    <section className="page-stack">
      <div className="page-header">
        <div>
          <p className="eyebrow">Profile</p>
          <h2>Current session</h2>
        </div>
      </div>
      <div className="panel profile-grid">
        <div>
          <span>Username</span>
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
    </section>
  );
}
