import importlib

import pytest

from app.ml import anti_spoof
from app.ml.anti_spoof import check_liveness, require_live_face


class LiveDeepFace:
    calls = []

    @staticmethod
    def extract_faces(**kwargs):
        LiveDeepFace.calls.append(kwargs)
        return [{"is_real": True, "antispoof_score": 0.94}]


def test_worker_settings_default_disables_anti_spoofing(monkeypatch):
    monkeypatch.delenv("DEEPFACE_ANTI_SPOOFING", raising=False)

    import app.config.settings as settings_module

    reloaded_settings_module = importlib.reload(settings_module)

    assert reloaded_settings_module.settings.deepface_anti_spoofing is False


def test_worker_settings_can_enable_anti_spoofing(monkeypatch):
    monkeypatch.setenv("DEEPFACE_ANTI_SPOOFING", "true")

    import app.config.settings as settings_module

    reloaded_settings_module = importlib.reload(settings_module)

    assert reloaded_settings_module.settings.deepface_anti_spoofing is True


def test_check_liveness_default_does_not_call_deepface_when_disabled(monkeypatch):
    class FailingDeepFace:
        @staticmethod
        def extract_faces(**kwargs):
            raise AssertionError("DeepFace should not be called by default")

    monkeypatch.setattr(anti_spoof, "load_deepface", lambda: FailingDeepFace)

    result = check_liveness("/app/storage/uploads/employee_1.jpg")

    assert result.passed is True
    assert result.confidence == 0.0
    assert result.message == "DeepFace anti-spoofing is disabled by configuration."


def test_check_liveness_uses_deepface_anti_spoofing(monkeypatch):
    LiveDeepFace.calls = []
    monkeypatch.setattr(anti_spoof, "load_deepface", lambda: LiveDeepFace)

    result = check_liveness(
        "/app/storage/uploads/employee_1.jpg",
        anti_spoofing_enabled=True,
    )

    assert result.passed is True
    assert result.image_path == "/app/storage/uploads/employee_1.jpg"
    assert result.confidence == 0.94
    assert result.message == "Live face verified by DeepFace."
    assert LiveDeepFace.calls == [
        {
            "img_path": "/app/storage/uploads/employee_1.jpg",
            "detector_backend": "opencv",
            "enforce_detection": True,
            "align": True,
            "anti_spoofing": True,
        }
    ]


def test_check_liveness_fails_for_spoof(monkeypatch):
    class SpoofDeepFace:
        @staticmethod
        def extract_faces(**kwargs):
            return [{"is_real": False, "antispoof_score": 0.88}]

    monkeypatch.setattr(anti_spoof, "load_deepface", lambda: SpoofDeepFace)

    result = check_liveness(
        "/app/storage/uploads/spoof.jpg",
        anti_spoofing_enabled=True,
    )

    assert result.passed is False
    assert result.confidence == 0.88
    assert result.message == "Spoof face detected by DeepFace."


def test_check_liveness_can_be_disabled_without_claiming_anti_spoofing(monkeypatch):
    result = check_liveness(
        "/app/storage/uploads/employee_1.jpg",
        anti_spoofing_enabled=False,
    )

    assert result.passed is True
    assert result.confidence == 0.0
    assert result.message == "DeepFace anti-spoofing is disabled by configuration."


def test_check_liveness_rejects_empty_image_path():
    result = check_liveness("")

    assert result.passed is False
    assert result.confidence == 0.0
    assert result.message == "Image path is empty."


def test_check_liveness_rejects_unexpected_deepface_format(monkeypatch):
    class BadDeepFace:
        @staticmethod
        def extract_faces(**kwargs):
            return [{"missing_is_real": True}]

    monkeypatch.setattr(anti_spoof, "load_deepface", lambda: BadDeepFace)

    result = check_liveness(
        "/app/storage/uploads/employee_1.jpg",
        anti_spoofing_enabled=True,
    )

    assert result.passed is False
    assert "does not include is_real" in result.message


def test_require_live_face_returns_passed_result(monkeypatch):
    monkeypatch.setattr(anti_spoof, "load_deepface", lambda: LiveDeepFace)

    result = require_live_face(
        "/app/storage/uploads/employee_1.jpg",
        anti_spoofing_enabled=True,
    )

    assert result.passed is True


def test_require_live_face_raises_for_spoof(monkeypatch):
    class SpoofDeepFace:
        @staticmethod
        def extract_faces(**kwargs):
            return [{"is_real": False, "antispoof_score": 0.88}]

    monkeypatch.setattr(anti_spoof, "load_deepface", lambda: SpoofDeepFace)

    with pytest.raises(ValueError, match="Spoof face detected"):
        require_live_face(
            "/app/storage/uploads/spoof.jpg",
            anti_spoofing_enabled=True,
        )
