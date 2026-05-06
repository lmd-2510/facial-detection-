import math

import pytest

from app.ml.embedder import (
    DEFAULT_EMBEDDING_DIMENSIONS,
    FAKE_MODEL_NAME,
    create_fake_embedding,
)


def test_create_fake_embedding_returns_expected_shape():
    result = create_fake_embedding("/app/storage/uploads/employee_1.jpg")

    assert result.image_path == "/app/storage/uploads/employee_1.jpg"
    assert result.model_name == FAKE_MODEL_NAME
    assert result.dimensions == DEFAULT_EMBEDDING_DIMENSIONS
    assert len(result.vector) == DEFAULT_EMBEDDING_DIMENSIONS
    assert all(-1 <= value <= 1 for value in result.vector)


def test_create_fake_embedding_is_deterministic_for_same_image_path():
    first_result = create_fake_embedding("/app/storage/uploads/employee_1.jpg")
    second_result = create_fake_embedding("/app/storage/uploads/employee_1.jpg")

    assert first_result == second_result


def test_create_fake_embedding_changes_for_different_image_path():
    first_result = create_fake_embedding("/app/storage/uploads/employee_1.jpg")
    second_result = create_fake_embedding("/app/storage/uploads/employee_2.jpg")

    assert first_result.vector != second_result.vector


def test_create_fake_embedding_returns_normalized_vector():
    result = create_fake_embedding("/app/storage/uploads/employee_1.jpg")
    magnitude = math.sqrt(sum(value * value for value in result.vector))

    assert magnitude == pytest.approx(1.0, abs=0.00001)


def test_create_fake_embedding_accepts_custom_dimensions():
    result = create_fake_embedding("/app/storage/uploads/employee_1.jpg", dimensions=8)

    assert result.dimensions == 8
    assert len(result.vector) == 8


def test_create_fake_embedding_rejects_empty_image_path():
    with pytest.raises(ValueError, match="Image path is empty"):
        create_fake_embedding("")


def test_create_fake_embedding_rejects_invalid_dimensions():
    with pytest.raises(ValueError, match="greater than zero"):
        create_fake_embedding("/app/storage/uploads/employee_1.jpg", dimensions=0)
