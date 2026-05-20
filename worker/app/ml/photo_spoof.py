from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.config.settings import settings
from app.ml.detector import FaceBox

try:
    import cv2
    import numpy as np
except Exception:  # pragma: no cover - optional runtime dependency
    cv2 = None
    np = None


@dataclass(frozen=True)
class PhotoSpoofResult:
    passed: bool
    image_path: str
    brightness_gap: float
    background_color_bins: int
    message: str


def _clip_face_box(face_box: FaceBox, width: int, height: int) -> tuple[int, int, int, int]:
    x1 = max(0, int(face_box.x))
    y1 = max(0, int(face_box.y))
    x2 = min(width, x1 + int(face_box.width))
    y2 = min(height, y1 + int(face_box.height))
    if x2 <= x1 or y2 <= y1:
        raise ValueError("Face bounding box is invalid.")
    return x1, y1, x2, y2


def _quantize_colors(pixels: Any) -> Any:
    quantized = pixels // 32
    return (quantized[:, 0] * 64) + (quantized[:, 1] * 8) + quantized[:, 2]


def check_photo_spoof(
    image_path: str,
    *,
    face_box: FaceBox,
    enabled: bool = settings.photo_check_enabled,
    brightness_gap_threshold: float = settings.photo_brightness_gap_threshold,
    background_color_bins_threshold: int = settings.photo_background_color_bins_threshold,
    background_min_ratio: float = settings.photo_background_min_ratio,
    sample_stride: int = settings.photo_sample_stride,
) -> PhotoSpoofResult:
    normalized_path = image_path.strip()
    if not normalized_path:
        return PhotoSpoofResult(
            passed=False,
            image_path=image_path,
            brightness_gap=0.0,
            background_color_bins=0,
            message="Image path is empty.",
        )

    if not enabled:
        return PhotoSpoofResult(
            passed=True,
            image_path=normalized_path,
            brightness_gap=0.0,
            background_color_bins=0,
            message="Photo spoof check is disabled by configuration.",
        )

    if cv2 is None or np is None:
        return PhotoSpoofResult(
            passed=True,
            image_path=normalized_path,
            brightness_gap=0.0,
            background_color_bins=0,
            message="Photo spoof check skipped because image libs are unavailable.",
        )

    image = cv2.imread(normalized_path)
    if image is None:
        return PhotoSpoofResult(
            passed=False,
            image_path=normalized_path,
            brightness_gap=0.0,
            background_color_bins=0,
            message="Failed to load image for photo spoof check.",
        )

    height, width = image.shape[:2]
    x1, y1, x2, y2 = _clip_face_box(face_box, width=width, height=height)

    total_area = float(height * width)
    face_area = float(max(0, x2 - x1) * max(0, y2 - y1))
    background_ratio = max(0.0, (total_area - face_area) / total_area)
    if background_ratio < float(background_min_ratio):
        return PhotoSpoofResult(
            passed=True,
            image_path=normalized_path,
            brightness_gap=0.0,
            background_color_bins=0,
            message=(
                "Background region is too small for photo spoof check. "
                f"background_ratio={background_ratio:.2f}."
            ),
        )

    stride = max(1, int(sample_stride))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_pixels = gray[y1:y2:stride, x1:x2:stride].astype("float32")

    background_mask = np.ones((height, width), dtype=bool)
    background_mask[y1:y2, x1:x2] = False
    background_mask = background_mask[::stride, ::stride]

    background_gray = gray[::stride, ::stride][background_mask].astype("float32")
    if face_pixels.size == 0 or background_gray.size == 0:
        return PhotoSpoofResult(
            passed=False,
            image_path=normalized_path,
            brightness_gap=0.0,
            background_color_bins=0,
            message="Insufficient pixels for photo spoof check.",
        )

    face_brightness = float(face_pixels.mean())
    background_brightness = float(background_gray.mean())
    brightness_gap = abs(face_brightness - background_brightness)

    background_pixels = image[::stride, ::stride][background_mask]
    if background_pixels.size == 0:
        return PhotoSpoofResult(
            passed=False,
            image_path=normalized_path,
            brightness_gap=brightness_gap,
            background_color_bins=0,
            message="Background region is empty for photo spoof check.",
        )

    color_bins = int(np.unique(_quantize_colors(background_pixels)).size)

    is_photo = (
        brightness_gap >= float(brightness_gap_threshold)
        and color_bins >= int(background_color_bins_threshold)
    )
    if is_photo:
        return PhotoSpoofResult(
            passed=False,
            image_path=normalized_path,
            brightness_gap=brightness_gap,
            background_color_bins=color_bins,
            message=(
                "Photo spoof detected by brightness/background heuristic. "
                f"brightness_gap={brightness_gap:.1f} color_bins={color_bins} "
                f"background_ratio={background_ratio:.2f}."
            ),
        )

    return PhotoSpoofResult(
        passed=True,
        image_path=normalized_path,
        brightness_gap=brightness_gap,
        background_color_bins=color_bins,
        message=(
            "Photo spoof check passed. "
            f"brightness_gap={brightness_gap:.1f} color_bins={color_bins} "
            f"background_ratio={background_ratio:.2f}."
        ),
    )


def require_not_photo(
    image_path: str,
    *,
    face_box: FaceBox,
    enabled: bool = settings.photo_check_enabled,
) -> PhotoSpoofResult:
    result = check_photo_spoof(
        image_path,
        face_box=face_box,
        enabled=enabled,
    )
    if not result.passed:
        raise ValueError(result.message)

    return result
