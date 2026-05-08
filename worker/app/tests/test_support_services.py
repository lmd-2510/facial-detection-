import pytest

from app.services.reindex_service import check_reindex_readiness, reindex_face_embeddings
from app.services.storage_service import resolve_image_path


def test_resolve_image_path_normalizes_supported_image_path():
    result = resolve_image_path("  /app/storage/uploads/employee_1.jpg  ")

    assert result.original_path == "  /app/storage/uploads/employee_1.jpg  "
    assert result.normalized_path == "/app/storage/uploads/employee_1.jpg"
    assert result.exists is False


def test_resolve_image_path_rejects_empty_path():
    with pytest.raises(ValueError, match="Image path is empty"):
        resolve_image_path("")


def test_resolve_image_path_rejects_unsupported_extension():
    with pytest.raises(ValueError, match="Unsupported image extension"):
        resolve_image_path("/app/storage/uploads/not_an_image.txt")


def test_reindex_readiness_explains_missing_source_image_path():
    readiness = check_reindex_readiness()

    assert readiness.ready is False
    assert "source image_path" in readiness.reason


def test_reindex_face_embeddings_raises_until_source_images_are_persisted():
    with pytest.raises(NotImplementedError, match="source image_path"):
        reindex_face_embeddings()
