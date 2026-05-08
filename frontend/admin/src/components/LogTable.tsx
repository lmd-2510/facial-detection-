import type { AccessLog } from "../types/log";

interface LogTableProps {
  logs: AccessLog[];
  isLoading: boolean;
}

export default function LogTable({ logs, isLoading }: LogTableProps) {
  if (isLoading) {
    return <div className="panel state-panel">Loading access logs...</div>;
  }

  if (logs.length === 0) {
    return <div className="panel state-panel">No access logs yet.</div>;
  }

  return (
    <div className="panel table-panel">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Status</th>
            <th>Employee</th>
            <th>Camera</th>
            <th>Score</th>
            <th>Image</th>
            <th>Created</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => (
            <tr key={log.id}>
              <td>#{log.id}</td>
              <td>
                <span className={`status-pill ${log.status}`}>{log.status}</span>
              </td>
              <td>{log.employee_id ?? "-"}</td>
              <td>{log.camera_id ?? "-"}</td>
              <td>{log.score === null ? "-" : log.score.toFixed(3)}</td>
              <td className="path-cell">{log.image_path ?? "-"}</td>
              <td>{new Date(log.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
