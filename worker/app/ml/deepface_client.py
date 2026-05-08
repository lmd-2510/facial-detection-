from typing import Any


def load_deepface() -> Any:
    try:
        from deepface import DeepFace
    except ImportError as exc:
        raise RuntimeError(
            "DeepFace is not installed. Install worker requirements or rebuild the worker image."
        ) from exc

    return DeepFace
