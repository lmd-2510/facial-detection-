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
    dominant_ratio: float
    border_edge_ratio: float
    face_laplacian_var: float
    glare_ratio: float
    face_shadow_ratio: float
    face_half_brightness_diff: float
    score: float
    signals: tuple[str, ...]
    message: str


def _build_result(
    *,
    passed: bool,
    image_path: str,
    message: str,
    brightness_gap: float = 0.0,
    background_color_bins: int = 0,
    dominant_ratio: float = 0.0,
    border_edge_ratio: float = 0.0,
    face_laplacian_var: float = 0.0,
    glare_ratio: float = 0.0,
    face_shadow_ratio: float = 0.0,
    face_half_brightness_diff: float = 0.0,
    score: float = 0.0,
    signals: tuple[str, ...] = (),
) -> PhotoSpoofResult:
    return PhotoSpoofResult(
        passed=passed,
        image_path=image_path,
        brightness_gap=brightness_gap,
        background_color_bins=background_color_bins,
        dominant_ratio=dominant_ratio,
        border_edge_ratio=border_edge_ratio,
        face_laplacian_var=face_laplacian_var,
        glare_ratio=glare_ratio,
        face_shadow_ratio=face_shadow_ratio,
        face_half_brightness_diff=face_half_brightness_diff,
        score=score,
        signals=signals,
        message=message,
    )


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
    background_dominant_ratio_min: float = settings.photo_background_dominant_ratio_min,
    face_laplacian_var_min: float = settings.photo_face_laplacian_var_min,
    face_glare_ratio_threshold: float = settings.photo_face_glare_ratio_threshold,
    spoof_score_threshold: float = settings.photo_spoof_score_threshold,
    face_min_size: int = settings.photo_face_min_size,
    border_ratio: float = settings.photo_border_ratio,
    border_edge_ratio_min: float = settings.photo_border_edge_ratio_min,
    border_edge_min_edges: int = settings.photo_border_edge_min_edges,
    face_shadow_brightness_ratio: float = settings.photo_face_shadow_brightness_ratio,
    face_shadow_ratio_threshold: float = settings.photo_face_shadow_ratio_threshold,
    face_half_brightness_diff_threshold: float = settings.photo_face_half_brightness_diff_threshold,
    face_overbright_threshold: float = settings.photo_face_overbright_threshold,
    hard_veto_enabled: bool = settings.photo_spoof_hard_veto,
    ring_margin_ratio: float = settings.photo_ring_margin_ratio,
    ring_min_pixels: int = settings.photo_ring_min_pixels,
    background_min_ratio: float = settings.photo_background_min_ratio,
    sample_stride: int = settings.photo_sample_stride,
) -> PhotoSpoofResult:
    normalized_path = image_path.strip()
    if not normalized_path:
        return _build_result(
            passed=False,
            image_path=image_path,
            message="Image path is empty.",
        )

    if not enabled:
        return _build_result(
            passed=True,
            image_path=normalized_path,
            message="Photo spoof check is disabled by configuration.",
        )

    if cv2 is None or np is None:
        return _build_result(
            passed=True,
            image_path=normalized_path,
            message="Photo spoof check skipped because image libs are unavailable.",
        )

    image = cv2.imread(normalized_path)
    if image is None:
        return _build_result(
            passed=False,
            image_path=normalized_path,
            message="Failed to load image for photo spoof check.",
        )

    height, width = image.shape[:2]
    x1, y1, x2, y2 = _clip_face_box(face_box, width=width, height=height)

    total_area = float(height * width)
    face_area = float(max(0, x2 - x1) * max(0, y2 - y1))
    background_ratio = max(0.0, (total_area - face_area) / total_area)

    stride = max(1, int(sample_stride))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_gray = gray[y1:y2, x1:x2]
    min_face_size = max(8, int(face_min_size))
    if face_gray.shape[0] < min_face_size or face_gray.shape[1] < min_face_size:
        return _build_result(
            passed=True,
            image_path=normalized_path,
            message="Face region is too small for photo spoof check.",
        )

    face_pixels = face_gray[::stride, ::stride].astype("float32")

    background_mask = np.ones((height, width), dtype=bool)
    background_mask[y1:y2, x1:x2] = False
    if background_ratio < float(background_min_ratio):
        margin_x = max(1, int((x2 - x1) * float(ring_margin_ratio)))
        margin_y = max(1, int((y2 - y1) * float(ring_margin_ratio)))
        rx1 = max(0, x1 - margin_x)
        ry1 = max(0, y1 - margin_y)
        rx2 = min(width, x2 + margin_x)
        ry2 = min(height, y2 + margin_y)
        ring_mask = np.zeros((height, width), dtype=bool)
        ring_mask[ry1:ry2, rx1:rx2] = True
        ring_mask[y1:y2, x1:x2] = False
        if int(ring_mask.sum()) >= int(ring_min_pixels):
            background_mask = ring_mask
    background_mask = background_mask[::stride, ::stride]

    background_gray = gray[::stride, ::stride][background_mask].astype("float32")
    if face_pixels.size == 0:
        return _build_result(
            passed=False,
            image_path=normalized_path,
            message="Insufficient pixels for photo spoof check.",
        )

    face_brightness = float(face_pixels.mean())
    background_pixels = image[::stride, ::stride][background_mask]
    background_available = background_gray.size > 0 and background_pixels.size > 0
    if background_available:
        background_brightness = float(background_gray.mean())
        brightness_delta = face_brightness - background_brightness
        brightness_gap = abs(brightness_delta)
    else:
        brightness_delta = 0.0
        brightness_gap = 0.0

    edges = cv2.Canny(gray, 80, 160)
    edge_pixels = edges > 0
    total_edges = int(edge_pixels.sum())
    border_px = max(1, int(min(height, width) * float(border_ratio)))
    border_mask_full = np.zeros((height, width), dtype=bool)
    border_mask_full[:border_px, :] = True
    border_mask_full[-border_px:, :] = True
    border_mask_full[:, :border_px] = True
    border_mask_full[:, -border_px:] = True
    border_edges = int(edge_pixels[border_mask_full].sum())
    border_edge_ratio = float(border_edges / total_edges) if total_edges else 0.0

    mid_x = max(1, face_gray.shape[1] // 2)
    left_brightness = float(face_gray[:, :mid_x].mean())
    right_brightness = float(face_gray[:, mid_x:].mean())
    face_half_brightness_diff = abs(left_brightness - right_brightness) / max(
        left_brightness,
        right_brightness,
        1.0,
    )
    shadow_threshold = float(face_brightness) * float(face_shadow_brightness_ratio)
    face_shadow_ratio = float((face_gray < shadow_threshold).mean())

    if background_available:
        quantized = _quantize_colors(background_pixels)
        unique_bins, counts = np.unique(quantized, return_counts=True)
        color_bins = int(unique_bins.size)
        dominant_ratio = float(counts.max() / counts.sum()) if counts.size else 0.0
        is_uniform_background = (
            dominant_ratio >= float(background_dominant_ratio_min)
            or color_bins <= int(background_color_bins_threshold)
        )
    else:
        color_bins = 0
        dominant_ratio = 0.0
        is_uniform_background = False
    face_laplacian_var = float(cv2.Laplacian(face_gray, cv2.CV_64F).var())
    glare_ratio = float((face_gray >= 240).mean())

    signals = []
    if background_available and brightness_gap >= float(brightness_gap_threshold):
        signals.append("brightness_gap")
    if background_available and brightness_delta >= float(face_overbright_threshold):
        signals.append("face_overbright")
    if background_available and is_uniform_background:
        signals.append("uniform_background")
    if face_laplacian_var <= float(face_laplacian_var_min):
        signals.append("low_texture")
    if glare_ratio >= float(face_glare_ratio_threshold):
        signals.append("glare")
    if (
        total_edges >= int(border_edge_min_edges)
        and border_edge_ratio >= float(border_edge_ratio_min)
    ):
        signals.append("phone_border")
    if (
        face_shadow_ratio >= float(face_shadow_ratio_threshold)
        and face_half_brightness_diff >= float(face_half_brightness_diff_threshold)
    ):
        signals.append("face_shadow")

    hard_veto = False
    if hard_veto_enabled:
        hard_veto = (
            "face_overbright" in signals
            or "phone_border" in signals
            or (
                "brightness_gap" in signals
                and "uniform_background" in signals
                and "low_texture" in signals
            )
            or (
                "glare" in signals
                and "low_texture" in signals
                and "uniform_background" in signals
            )
        )

    score = 0.0
    if "brightness_gap" in signals:
        score += 0.25
    if "face_overbright" in signals:
        score += 0.2
    if "uniform_background" in signals:
        score += 0.2
    if "low_texture" in signals:
        score += 0.2
    if "glare" in signals:
        score += 0.1
    if "phone_border" in signals:
        score += 0.15
    if "face_shadow" in signals:
        score += 0.1

    is_photo = hard_veto or score >= float(spoof_score_threshold)
    if is_photo:
        return _build_result(
            passed=False,
            image_path=normalized_path,
            brightness_gap=brightness_gap,
            background_color_bins=color_bins,
            dominant_ratio=dominant_ratio,
            border_edge_ratio=border_edge_ratio,
            face_laplacian_var=face_laplacian_var,
            glare_ratio=glare_ratio,
            face_shadow_ratio=face_shadow_ratio,
            face_half_brightness_diff=face_half_brightness_diff,
            score=score,
            signals=tuple(signals),
            message=(
                "Photo spoof detected by multi-signal heuristic. "
                f"score={score:.2f} hard_veto={hard_veto} "
                f"brightness_gap={brightness_gap:.1f} face_delta={brightness_delta:.1f} "
                f"color_bins={color_bins} background_ratio={background_ratio:.2f} "
                f"dominant_ratio={dominant_ratio:.2f} border_edge_ratio={border_edge_ratio:.2f} "
                f"laplacian_var={face_laplacian_var:.1f} glare_ratio={glare_ratio:.2f} "
                f"face_shadow_ratio={face_shadow_ratio:.2f} "
                f"face_half_diff={face_half_brightness_diff:.2f}."
            ),
        )

    return _build_result(
        passed=True,
        image_path=normalized_path,
        brightness_gap=brightness_gap,
        background_color_bins=color_bins,
        dominant_ratio=dominant_ratio,
        border_edge_ratio=border_edge_ratio,
        face_laplacian_var=face_laplacian_var,
        glare_ratio=glare_ratio,
        face_shadow_ratio=face_shadow_ratio,
        face_half_brightness_diff=face_half_brightness_diff,
        score=score,
        signals=tuple(signals),
        message=(
            "Photo spoof check passed. "
            f"score={score:.2f} hard_veto={hard_veto} "
            f"brightness_gap={brightness_gap:.1f} face_delta={brightness_delta:.1f} "
            f"color_bins={color_bins} background_ratio={background_ratio:.2f} "
            f"dominant_ratio={dominant_ratio:.2f} border_edge_ratio={border_edge_ratio:.2f} "
            f"laplacian_var={face_laplacian_var:.1f} glare_ratio={glare_ratio:.2f} "
            f"face_shadow_ratio={face_shadow_ratio:.2f} "
            f"face_half_diff={face_half_brightness_diff:.2f}."
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
