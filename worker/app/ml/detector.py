from dataclasses import dataclass
from hashlib import sha256
from pathlib import PurePath


NO_FACE_MARKERS = ("no_face", "noface", "empty", "blank")
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


def detect_face(image_path: str) -> FaceDetectionResult:
    normalized_path = image_path.strip()
    if not normalized_path:
        return FaceDetectionResult(
            detected=False,
            image_path=image_path,
            face_box=None,
            confidence=0.0,
            message="Image path is empty.",
        )

    file_name = PurePath(normalized_path).name.lower()
    extension = PurePath(normalized_path).suffix.lower()
    if extension and extension not in SUPPORTED_IMAGE_EXTENSIONS:
        return FaceDetectionResult(
            detected=False,
            image_path=normalized_path,
            face_box=None,
            confidence=0.0,
            message=f"Unsupported image extension: {extension}",
        )

    if any(marker in file_name for marker in NO_FACE_MARKERS):
        return FaceDetectionResult(
            detected=False,
            image_path=normalized_path,
            face_box=None,
            confidence=0.0,
            message="No face detected by fake detector.",
        )

    digest = sha256(normalized_path.encode("utf-8")).digest()
    face_box = FaceBox(
        x=20 + digest[0] % 40,
        y=20 + digest[1] % 40,
        width=96 + digest[2] % 64,
        height=96 + digest[3] % 64,
    )
    confidence = round(0.8 + (digest[4] / 255) * 0.19, 4)

    return FaceDetectionResult(
        detected=True,
        image_path=normalized_path,
        face_box=face_box,
        confidence=confidence,
        message="Face detected by fake detector.",
    )


def require_face(image_path: str) -> FaceDetectionResult:
    result = detect_face(image_path)
    if not result.detected:
        raise ValueError(result.message)

    return result
