from dataclasses import dataclass
from os import getenv


def _get_bool(name: str, default: bool) -> bool:
    value = getenv(name)
    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_float(name: str, default: float) -> float:
    value = getenv(name)
    if value is None:
        return default

    return float(value)


def _get_int(name: str, default: int) -> int:
    value = getenv(name)
    if value is None:
        return default

    return int(value)


@dataclass(frozen=True)
class Settings:
    app_env: str = getenv("APP_ENV", "dev")
    redis_url: str = getenv("REDIS_URL", "redis://localhost:6379/0")
    database_url: str = getenv(
        "DATABASE_URL",
        "postgresql://deepface:deepface@localhost:5432/deepface_access",
    )
    deepface_model_name: str = getenv("DEEPFACE_MODEL_NAME", "Facenet512")
    deepface_detector_backend: str = getenv("DEEPFACE_DETECTOR_BACKEND", "mtcnn")
    deepface_access_detector_backend: str = getenv(
        "DEEPFACE_ACCESS_DETECTOR_BACKEND",
        getenv("DEEPFACE_DETECTOR_BACKEND", "mtcnn"),
    )
    deepface_face_count_backend: str = getenv("DEEPFACE_FACE_COUNT_BACKEND", "")
    deepface_enforce_detection: bool = _get_bool("DEEPFACE_ENFORCE_DETECTION", True)
    deepface_align: bool = _get_bool("DEEPFACE_ALIGN", False)
    deepface_normalization: str = getenv("DEEPFACE_NORMALIZATION", "base")
    deepface_match_threshold: float = _get_float("DEEPFACE_MATCH_THRESHOLD", 0.70)
    deepface_anti_spoofing: bool = _get_bool("DEEPFACE_ANTI_SPOOFING", False)
    deepface_warmup_on_start: bool = _get_bool("DEEPFACE_WARMUP_ON_START", True)
    photo_check_enabled: bool = _get_bool("PHOTO_CHECK_ENABLED", False)
    photo_brightness_gap_threshold: float = _get_float("PHOTO_BRIGHTNESS_GAP_THRESHOLD", 40.0)
    photo_background_color_bins_threshold: int = _get_int(
        "PHOTO_BACKGROUND_COLOR_BINS_THRESHOLD",
        24,
    )
    photo_background_dominant_ratio_min: float = _get_float(
        "PHOTO_BACKGROUND_DOMINANT_RATIO_MIN",
        0.55,
    )
    photo_background_min_ratio: float = _get_float("PHOTO_BACKGROUND_MIN_RATIO", 0.25)
    photo_face_laplacian_var_min: float = _get_float("PHOTO_FACE_LAPLACIAN_VAR_MIN", 35.0)
    photo_face_glare_ratio_threshold: float = _get_float(
        "PHOTO_FACE_GLARE_RATIO_THRESHOLD",
        0.06,
    )
    photo_spoof_score_threshold: float = _get_float("PHOTO_SPOOF_SCORE_THRESHOLD", 0.6)
    photo_face_min_size: int = _get_int("PHOTO_FACE_MIN_SIZE", 32)
    photo_border_ratio: float = _get_float("PHOTO_BORDER_RATIO", 0.08)
    photo_border_edge_ratio_min: float = _get_float("PHOTO_BORDER_EDGE_RATIO_MIN", 0.6)
    photo_border_edge_min_edges: int = _get_int("PHOTO_BORDER_EDGE_MIN_EDGES", 250)
    photo_face_shadow_brightness_ratio: float = _get_float(
        "PHOTO_FACE_SHADOW_BRIGHTNESS_RATIO",
        0.6,
    )
    photo_face_shadow_ratio_threshold: float = _get_float(
        "PHOTO_FACE_SHADOW_RATIO_THRESHOLD",
        0.25,
    )
    photo_face_half_brightness_diff_threshold: float = _get_float(
        "PHOTO_FACE_HALF_BRIGHTNESS_DIFF_THRESHOLD",
        0.35,
    )
    photo_face_overbright_threshold: float = _get_float(
        "PHOTO_FACE_OVERBRIGHT_THRESHOLD",
        45.0,
    )
    photo_spoof_hard_veto: bool = _get_bool("PHOTO_SPOOF_HARD_VETO", True)
    photo_ring_margin_ratio: float = _get_float("PHOTO_RING_MARGIN_RATIO", 0.2)
    photo_ring_min_pixels: int = _get_int("PHOTO_RING_MIN_PIXELS", 600)
    photo_sample_stride: int = _get_int("PHOTO_SAMPLE_STRIDE", 2)


settings = Settings()
