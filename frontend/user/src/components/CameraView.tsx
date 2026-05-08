interface CameraViewProps {
  imagePath: string;
}

export default function CameraView({ imagePath }: CameraViewProps) {
  return (
    <section className="panel camera-view">
      <div className="scan-frame">
        <span />
        <span />
        <span />
        <span />
      </div>
      <div>
        <p className="eyebrow">Snapshot path</p>
        <strong>{imagePath || "/app/storage/uploads/snapshot.jpg"}</strong>
      </div>
    </section>
  );
}
