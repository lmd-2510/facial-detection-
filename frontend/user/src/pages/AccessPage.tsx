import { FormEvent, useState } from "react";
import { checkAccessImage } from "../api/access";
import CameraView from "../components/CameraView";
import ResultCard from "../components/ResultCard";
import type { AccessCheckResponse } from "../types/access";

interface AccessPageProps {
  token: string;
  onAccessQueued: () => Promise<void>;
}

export default function AccessPage({ token, onAccessQueued }: AccessPageProps) {
  const [cameraId, setCameraId] = useState("1");
  const [mode, setMode] = useState<"manual" | "realtime">("manual");
  const [snapshotFile, setSnapshotFile] = useState<File | null>(null);
  const [imageKey, setImageKey] = useState("");
  const [result, setResult] = useState<AccessCheckResponse | null>(null);
  const [isChecking, setIsChecking] = useState(false);
  const [isRealtimeActive, setIsRealtimeActive] = useState(false);
  const [isSubmittingFrame, setIsSubmittingFrame] = useState(false);
  const [lastRealtimeAt, setLastRealtimeAt] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const realtimeIntervalMs = 2000;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsChecking(true);
    setError(null);
    try {
      if (!snapshotFile) {
        setError("Choose a snapshot image first.");
        return;
      }
      const response = await checkAccessImage(token, Number(cameraId), snapshotFile);
      setImageKey(response.image_key);
      setResult(response);
      await onAccessQueued();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Cannot check access");
    } finally {
      setIsChecking(false);
    }
  }

  async function handleRealtimeFrame(file: File) {
    if (isSubmittingFrame) {
      return;
    }

    setIsSubmittingFrame(true);
    setError(null);
    try {
      const response = await checkAccessImage(token, Number(cameraId), file);
      setSnapshotFile(file);
      setImageKey(response.image_key || file.name);
      setResult(response);
      setLastRealtimeAt(new Date().toLocaleTimeString());
      await onAccessQueued();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Cannot check realtime frame");
    } finally {
      setIsSubmittingFrame(false);
    }
  }

  function stopRealtime() {
    setIsRealtimeActive(false);
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
          <div className="segmented-control" aria-label="Access check mode">
            <button
              className={mode === "manual" ? "active" : ""}
              type="button"
              onClick={() => {
                setMode("manual");
                stopRealtime();
              }}
            >
              Manual
            </button>
            <button
              className={mode === "realtime" ? "active" : ""}
              type="button"
              onClick={() => {
                setMode("realtime");
                setError(null);
              }}
            >
              Realtime
            </button>
          </div>
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
              disabled={mode === "realtime"}
              type="file"
              onChange={(event) => {
                const file = event.target.files?.[0] ?? null;
                setSnapshotFile(file);
                setImageKey(file?.name ?? "");
                setResult(null);
                setError(null);
              }}
            />
          </label>
          {mode === "realtime" ? (
            <button
              className={isRealtimeActive ? "secondary-button" : "primary-button"}
              type="button"
              onClick={() => setIsRealtimeActive((current) => !current)}
            >
              {isRealtimeActive ? "Stop realtime" : "Start realtime"}
            </button>
          ) : (
            <button className="primary-button" disabled={isChecking} type="submit">
            {isChecking ? "Queueing..." : "Check access"}
            </button>
          )}
          {mode === "realtime" ? (
            <div className="scan-summary">
              <span>{isRealtimeActive ? "Scanning" : "Ready"}</span>
              <strong>
                {isSubmittingFrame
                  ? "Sending frame..."
                  : lastRealtimeAt
                    ? `Last frame ${lastRealtimeAt}`
                    : "No realtime frame yet"}
              </strong>
            </div>
          ) : null}
        </form>
      </div>

      <div className="page-stack">
        <CameraView
          intervalMs={realtimeIntervalMs}
          imagePath={imageKey || snapshotFile?.name || ""}
          isRealtimeActive={mode === "realtime" && isRealtimeActive}
          isSubmittingFrame={isSubmittingFrame}
          onCapture={(file) => {
            setSnapshotFile(file);
            setImageKey(file.name);
            setResult(null);
            setError(null);
          }}
          onRealtimeFrame={handleRealtimeFrame}
          onRealtimeStop={stopRealtime}
        />
        <ResultCard result={result} />
      </div>
    </section>
  );
}
