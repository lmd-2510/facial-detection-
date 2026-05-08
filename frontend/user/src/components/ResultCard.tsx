import type { AccessCheckResponse } from "../types/access";

interface ResultCardProps {
  result: AccessCheckResponse | null;
}

export default function ResultCard({ result }: ResultCardProps) {
  if (!result) {
    return (
      <section className="panel result-card idle">
        <span>Ready</span>
        <strong>Waiting for access check</strong>
      </section>
    );
  }

  return (
    <section className={`panel result-card ${result.status}`}>
      <span>{result.status}</span>
      <strong>Log #{result.log_id}</strong>
      <p>{result.message}</p>
      <dl>
        <div>
          <dt>Camera</dt>
          <dd>{result.camera_id}</dd>
        </div>
        <div>
          <dt>Employee</dt>
          <dd>{result.employee_id ?? "-"}</dd>
        </div>
        <div>
          <dt>Score</dt>
          <dd>{result.score === null ? "-" : result.score.toFixed(3)}</dd>
        </div>
      </dl>
    </section>
  );
}
