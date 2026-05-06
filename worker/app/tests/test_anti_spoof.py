import pytest

from app.ml.anti_spoof import check_liveness, require_live_face


def test_check_liveness_passes_for_supported_fake_flow():
    result = check_liveness("/app/storage/uploads/employee_1.jpg")

    assert result.passed is True
    assert result.image_path == "/app/storage/uploads/employee_1.jpg"
    assert result.confidence == 1.0
    assert result.message == "Fake anti-spoof check passed."


def test_check_liveness_rejects_empty_image_path():
    result = check_liveness("")

    assert result.passed is False
    assert result.confidence == 0.0
    assert result.message == "Image path is empty."


def test_require_live_face_returns_passed_result():
    result = require_live_face("/app/storage/uploads/employee_1.jpg")

    assert result.passed is True


def test_require_live_face_raises_for_empty_image_path():
    with pytest.raises(ValueError, match="Image path is empty"):
        require_live_face("")
