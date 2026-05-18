import { FormEvent, useEffect, useState } from "react";
import { createUser, deleteUser, listUsers, updateUser } from "../api/users";
import type { User, UserPayload, UserRole } from "../types/user";


interface UserPageProps {
  currentUser: User;
  token: string;
}


const emptyForm: UserPayload = {
  username: "",
  password: "",
  role: "user",
};


export default function UserPage({ currentUser, token }: UserPageProps) {
  const [users, setUsers] = useState<User[]>([]);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [form, setForm] = useState<UserPayload>(emptyForm);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadUsers() {
    setIsLoading(true);
    setError(null);
    try {
      setUsers(await listUsers(token));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Cannot load users");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadUsers();
  }, [token]);

  function startEdit(user: User) {
    setEditingUser(user);
    setForm({
      username: user.username,
      password: "",
      role: user.role,
    });
    setError(null);
    setMessage(null);
  }

  function cancelEdit() {
    setEditingUser(null);
    setForm(emptyForm);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    setError(null);
    setMessage(null);
    try {
      if (editingUser) {
        const payload: Partial<UserPayload> = {
          username: form.username.trim(),
          role: form.role,
        };
        if (form.password?.trim()) {
          payload.password = form.password;
        }
        await updateUser(token, editingUser.id, payload);
        setMessage("User updated.");
      } else {
        await createUser(token, {
          username: form.username.trim(),
          password: form.password,
          role: form.role,
        });
        setMessage("User created.");
      }
      cancelEdit();
      await loadUsers();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Cannot save user");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleDelete(userId: number) {
    setError(null);
    setMessage(null);
    try {
      await deleteUser(token, userId);
      setMessage("User deleted.");
      if (editingUser?.id === userId) {
        cancelEdit();
      }
      await loadUsers();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Cannot delete user");
    }
  }

  return (
    <section className="page-stack">
      <div className="page-header">
        <div>
          <p className="eyebrow">Accounts</p>
          <h2>User management</h2>
        </div>
        <button className="secondary-button" onClick={() => void loadUsers()}>
          Refresh
        </button>
      </div>

      {error ? <div className="alert error">{error}</div> : null}
      {message ? <div className="alert success">{message}</div> : null}

      <div className="split-layout">
        <form className="panel form-panel" onSubmit={handleSubmit}>
          <div className="panel-heading">
            <div>
              <p className="eyebrow">{editingUser ? "Edit" : "Create"}</p>
              <h2>{editingUser ? editingUser.username : "New user"}</h2>
            </div>
            {editingUser ? (
              <button className="ghost-button" type="button" onClick={cancelEdit}>
                Cancel
              </button>
            ) : null}
          </div>

          <label>
            Username
            <input
              required
              value={form.username}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  username: event.target.value,
                }))
              }
            />
          </label>

          <label>
            Password
            <input
              required={!editingUser}
              type="password"
              value={form.password ?? ""}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  password: event.target.value,
                }))
              }
            />
          </label>

          <label>
            Role
            <select
              value={form.role}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  role: event.target.value as UserRole,
                }))
              }
            >
              <option value="user">user</option>
              <option value="admin">admin</option>
            </select>
          </label>

          <button className="primary-button" disabled={isSaving} type="submit">
            {isSaving ? "Saving..." : editingUser ? "Update user" : "Create user"}
          </button>
        </form>

        <div className="panel table-panel">
          {isLoading ? (
            <div className="state-panel">Loading users...</div>
          ) : users.length === 0 ? (
            <div className="state-panel">No users yet.</div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Username</th>
                  <th>Role</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id}>
                    <td>{user.username}</td>
                    <td>
                      <span className={`status-pill ${user.role}`}>
                        {user.role}
                      </span>
                    </td>
                    <td>{new Date(user.created_at).toLocaleString()}</td>
                    <td className="row-actions">
                      <button className="small-button" onClick={() => startEdit(user)}>
                        Edit
                      </button>
                      <button
                        className="danger-button"
                        disabled={user.id === currentUser.id}
                        onClick={() => void handleDelete(user.id)}
                      >
                        Delete
                      </button>
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
