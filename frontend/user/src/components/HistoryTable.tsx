import type { AccessLog } from "../types/log";

interface HistoryTableProps {
  logs: AccessLog[];
  isLoading: boolean;
}

export default function HistoryTable({ logs, isLoading }: HistoryTableProps) {
  if (isLoading) {
    return <section className="panel state-panel">Loading history...</section>;
  }

  if (logs.length === 0) {
    return <section className="panel state-panel">No access history yet.</section>;
  }

  return (
    <section className="panel table-panel">
      <table>
        <thead>
          <tr>
            <th>Status</th>
            <th>Camera</th>
            <th>Employee</th>
            <th>Score</th>
            <th>Image path</th>
            <th>Created</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => (
            <tr key={log.id}>
              <td>
                <span className={`status-pill ${log.status}`}>{log.status}</span>
              </td>
              <td>{log.camera_id ?? "-"}</td>
              <td>{log.employee_id ?? "-"}</td>
              <td>{log.score === null ? "-" : log.score.toFixed(3)}</td>
              <td className="path-cell">{log.image_path ?? "-"}</td>
              <td>{new Date(log.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
