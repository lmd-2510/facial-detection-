from dataclasses import dataclass
from hashlib import sha256
from math import sqrt
from pathlib import Path


FAKE_MODEL_NAME = "fake-hash-embedding-v1"
DEFAULT_EMBEDDING_DIMENSIONS = 16


@dataclass(frozen=True)
class FaceEmbeddingResult:
    image_path: str
    vector: list[float]
    model_name: str
    dimensions: int


def _seed_bytes_from_image(image_path: str) -> bytes:
    path = Path(image_path)
    if path.is_file():
        return path.read_bytes()

    return image_path.encode("utf-8")


def _expand_digest(seed: bytes, dimensions: int) -> bytes:
    chunks: list[bytes] = []
    counter = 0
    while sum(len(chunk) for chunk in chunks) < dimensions:
        chunks.append(sha256(seed + counter.to_bytes(4, "big")).digest())
        counter += 1

    return b"".join(chunks)[:dimensions]


def create_fake_embedding(
    image_path: str,
    dimensions: int = DEFAULT_EMBEDDING_DIMENSIONS,
) -> FaceEmbeddingResult:
    normalized_path = image_path.strip()
    if not normalized_path:
        raise ValueError("Image path is empty.")

    if dimensions <= 0:
        raise ValueError("Embedding dimensions must be greater than zero.")

    digest = _expand_digest(_seed_bytes_from_image(normalized_path), dimensions)
    raw_vector = [(byte / 127.5) - 1.0 for byte in digest]
    magnitude = sqrt(sum(value * value for value in raw_vector))
    if magnitude == 0:
        raise ValueError("Generated embedding has zero magnitude.")

    vector = [round(value / magnitude, 6) for value in raw_vector]
    return FaceEmbeddingResult(
        image_path=normalized_path,
        vector=vector,
        model_name=FAKE_MODEL_NAME,
        dimensions=dimensions,
    )
