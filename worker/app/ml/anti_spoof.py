from dataclasses import dataclass
from typing import Any

from app.config.settings import settings
from app.ml.deepface_client import load_deepface


@dataclass(frozen=True)
class AntiSpoofResult:
    passed: bool
    image_path: str
    confidence: float
    message: str


def _extract_liveness_result(extract_faces_result: Any) -> tuple[bool, float]:
    if not isinstance(extract_faces_result, list) or not extract_faces_result:
        raise ValueError("No face detected for anti-spoofing.")

    first_face = extract_faces_result[0]
    if not isinstance(first_face, dict):
        raise ValueError("DeepFace returned an unexpected anti-spoofing format.")

    if "is_real" not in first_face:
        raise ValueError("DeepFace anti-spoofing result does not include is_real.")

    score = first_face.get("antispoof_score", first_face.get("anti_spoofing_score", 0.0))
    return bool(first_face["is_real"]), float(score or 0.0)


def check_liveness(
    image_path: str,
    *,
    detector_backend: str = settings.deepface_detector_backend,
    enforce_detection: bool = settings.deepface_enforce_detection,
    align: bool = settings.deepface_align,
    anti_spoofing_enabled: bool = settings.deepface_anti_spoofing,
) -> AntiSpoofResult:
    normalized_path = image_path.strip()
    if not normalized_path:
        return AntiSpoofResult(
            passed=False,
            image_path=image_path,
            confidence=0.0,
            message="Image path is empty.",
        )

    if not anti_spoofing_enabled:
        return AntiSpoofResult(
            passed=True,
            image_path=normalized_path,
            confidence=0.0,
            message="DeepFace anti-spoofing is disabled by configuration.",
        )

    try:
        faces = load_deepface().extract_faces(
            img_path=normalized_path,
            detector_backend=detector_backend,
            enforce_detection=enforce_detection,
            align=align,
            anti_spoofing=True,
        )
        is_real, score = _extract_liveness_result(faces)
    except Exception as exc:
        return AntiSpoofResult(
            passed=False,
            image_path=normalized_path,
            confidence=0.0,
            message=str(exc),
        )

    return AntiSpoofResult(
        passed=is_real,
        image_path=normalized_path,
        confidence=score,
        message="Live face verified by DeepFace." if is_real else "Spoof face detected by DeepFace.",
    )


def require_live_face(image_path: str) -> AntiSpoofResult:
    result = check_liveness(image_path)
    if not result.passed:
        raise ValueError(result.message)

    return result
