from dataclasses import dataclass


@dataclass(frozen=True)
class AntiSpoofResult:
    passed: bool
    image_path: str
    confidence: float
    message: str


def check_liveness(image_path: str) -> AntiSpoofResult:
    normalized_path = image_path.strip()
    if not normalized_path:
        return AntiSpoofResult(
            passed=False,
            image_path=image_path,
            confidence=0.0,
            message="Image path is empty.",
        )

    return AntiSpoofResult(
        passed=True,
        image_path=normalized_path,
        confidence=1.0,
        message="Fake anti-spoof check passed.",
    )


def require_live_face(image_path: str) -> AntiSpoofResult:
    result = check_liveness(image_path)
    if not result.passed:
        raise ValueError(result.message)

    return result
