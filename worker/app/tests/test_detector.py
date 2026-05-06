import pytest

from app.ml.detector import detect_face, require_face


def test_detect_face_returns_face_for_supported_image_path():
    result = detect_face("/app/storage/uploads/employee_1.jpg")

    assert result.detected is True
    assert result.image_path == "/app/storage/uploads/employee_1.jpg"
    assert result.face_box is not None
    assert result.face_box.width > 0
    assert result.face_box.height > 0
    assert 0.8 <= result.confidence <= 0.99


def test_detect_face_is_deterministic_for_same_image_path():
    first_result = detect_face("/app/storage/uploads/employee_1.jpg")
    second_result = detect_face("/app/storage/uploads/employee_1.jpg")

    assert first_result == second_result


def test_detect_face_rejects_empty_image_path():
    result = detect_face("")

    assert result.detected is False
    assert result.face_box is None
    assert result.confidence == 0.0
    assert result.message == "Image path is empty."


def test_detect_face_rejects_unsupported_extension():
    result = detect_face("/app/storage/uploads/not_an_image.txt")

    assert result.detected is False
    assert result.face_box is None
    assert result.confidence == 0.0
    assert "Unsupported image extension" in result.message


@pytest.mark.parametrize(
    "image_path",
    [
        "/app/storage/uploads/no_face.jpg",
        "/app/storage/uploads/noface.png",
        "/app/storage/uploads/empty.webp",
        "/app/storage/uploads/blank.jpeg",
    ],
)
def test_detect_face_rejects_no_face_markers(image_path: str):
    result = detect_face(image_path)

    assert result.detected is False
    assert result.face_box is None
    assert result.confidence == 0.0
    assert result.message == "No face detected by fake detector."


def test_require_face_returns_detection_for_supported_image_path():
    result = require_face("/app/storage/uploads/employee_1.jpg")

    assert result.detected is True
    assert result.face_box is not None


def test_require_face_raises_when_face_is_not_detected():
    with pytest.raises(ValueError, match="No face detected"):
        require_face("/app/storage/uploads/no_face.jpg")
