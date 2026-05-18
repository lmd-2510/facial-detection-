import { useEffect, useRef, useState } from "react";

interface CameraViewProps {
  imagePath: string;
  onCapture: (file: File) => void;
}

export default function CameraView({ imagePath, onCapture }: CameraViewProps) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [isCameraOn, setIsCameraOn] = useState(false);
  const [isCapturing, setIsCapturing] = useState(false);

  useEffect(() => {
    return () => {
      streamRef.current?.getTracks().forEach((track) => track.stop());
    };
  }, []);

  async function startCamera() {
    setCameraError(null);
    try {
      if (!navigator.mediaDevices?.getUserMedia) {
        setCameraError("This browser does not support webcam capture.");
        return;
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: "user",
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
        audio: false,
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setIsCameraOn(true);
    } catch (err) {
      setCameraError(
        err instanceof Error ? err.message : "Cannot open the webcam.",
      );
    }
  }

  function stopCamera() {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsCameraOn(false);
  }

  async function captureFrame() {
    const video = videoRef.current;
    if (!video || !isCameraOn) {
      setCameraError("Start the camera before capturing a frame.");
      return;
    }

    setIsCapturing(true);
    setCameraError(null);
    try {
      const canvas = document.createElement("canvas");
      canvas.width = video.videoWidth || 1280;
      canvas.height = video.videoHeight || 720;
      const context = canvas.getContext("2d");
      if (!context) {
        setCameraError("Cannot capture this frame.");
        return;
      }

      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      const blob = await new Promise<Blob | null>((resolve) => {
        canvas.toBlob(resolve, "image/jpeg", 0.92);
      });
      if (!blob) {
        setCameraError("Cannot create a snapshot image.");
        return;
      }

      const file = new File([blob], `webcam-${Date.now()}.jpg`, {
        type: "image/jpeg",
      });
      onCapture(file);
    } finally {
      setIsCapturing(false);
    }
  }

  return (
    <section className="panel camera-view">
      <div className="scan-frame">
        <video
          ref={videoRef}
          autoPlay
          muted
          playsInline
          className={isCameraOn ? "camera-preview active" : "camera-preview"}
        />
        <span />
        <span />
        <span />
        <span />
      </div>
      <div className="camera-actions">
        {isCameraOn ? (
          <button className="secondary-button" type="button" onClick={stopCamera}>
            Stop camera
          </button>
        ) : (
          <button className="secondary-button" type="button" onClick={startCamera}>
            Start camera
          </button>
        )}
        <button
          className="primary-button"
          disabled={!isCameraOn || isCapturing}
          type="button"
          onClick={captureFrame}
        >
          {isCapturing ? "Capturing..." : "Capture frame"}
        </button>
      </div>
      {cameraError ? <div className="alert error">{cameraError}</div> : null}
      <div>
        <p className="eyebrow">Snapshot path</p>
        <strong>{imagePath || "/app/storage/uploads/snapshot.jpg"}</strong>
      </div>
    </section>
  );
}
