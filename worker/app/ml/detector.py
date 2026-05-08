from dataclasses import dataclass
from pathlib import PurePath
from typing import Any

from app.config.settings import settings
from app.ml.deepface_client import load_deepface


SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


@dataclass(frozen=True)
class FaceBox:
    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True)
class FaceDetectionResult:
    detected: bool
    image_path: str
    face_box: FaceBox | None
    confidence: float
    message: str


def _extract_first_face_area(extract_faces_result: Any) -> tuple[FaceBox, float]:
    if not isinstance(extract_faces_result, list) or not extract_faces_result:
        raise ValueError("No face detected by DeepFace.")

    first_face = extract_faces_result[0]
    if not isinstance(first_face, dict):
        raise ValueError("DeepFace returned an unexpected face detection format.")

    facial_area = first_face.get("facial_area")
    if not isinstance(facial_area, dict):
        raise ValueError("DeepFace result does not include facial area.")

    try:
        face_box = FaceBox(
            x=int(facial_area["x"]),
            y=int(facial_area["y"]),
            width=int(facial_area["w"]),
            height=int(facial_area["h"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("DeepFace facial area is incomplete.") from exc

    confidence = first_face.get("face_confidence", first_face.get("confidence", 0.0))
    return face_box, float(confidence or 0.0)


def detect_face(
    image_path: str,
    *,
    detector_backend: str = settings.deepface_detector_backend,
    enforce_detection: bool = settings.deepface_enforce_detection,
    align: bool = settings.deepface_align,
) -> FaceDetectionResult:
    normalized_path = image_path.strip()
    if not normalized_path:
        return FaceDetectionResult(
            detected=False,
            image_path=image_path,
            face_box=None,
            confidence=0.0,
            message="Image path is empty.",
        )

    extension = PurePath(normalized_path).suffix.lower()
    if extension and extension not in SUPPORTED_IMAGE_EXTENSIONS:
        return FaceDetectionResult(
            detected=False,
            image_path=normalized_path,
            face_box=None,
            confidence=0.0,
            message=f"Unsupported image extension: {extension}",
        )

    try:
        faces = load_deepface().extract_faces(
            img_path=normalized_path,
            detector_backend=detector_backend,
            enforce_detection=enforce_detection,
            align=align,
            anti_spoofing=False,
        )
        face_box, confidence = _extract_first_face_area(faces)
    except Exception as exc:
        return FaceDetectionResult(
            detected=False,
            image_path=normalized_path,
            face_box=None,
            confidence=0.0,
            message=str(exc),
        )

    return FaceDetectionResult(
        detected=True,
        image_path=normalized_path,
        face_box=face_box,
        confidence=confidence,
        message="Face detected by DeepFace.",
    )


def require_face(image_path: str) -> FaceDetectionResult:
    result = detect_face(image_path)
    if not result.detected:
        raise ValueError(result.message)

    return result
