from dataclasses import dataclass
from pathlib import Path


SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


@dataclass(frozen=True)
class ResolvedImagePath:
    original_path: str
    normalized_path: str
    exists: bool


def resolve_image_path(image_path: str) -> ResolvedImagePath:
    normalized_path = image_path.strip()
    if not normalized_path:
        raise ValueError("Image path is empty.")

    extension = Path(normalized_path).suffix.lower()
    if extension and extension not in SUPPORTED_IMAGE_EXTENSIONS:
        raise ValueError(f"Unsupported image extension: {extension}")

    return ResolvedImagePath(
        original_path=image_path,
        normalized_path=normalized_path,
        exists=Path(normalized_path).is_file(),
    )
