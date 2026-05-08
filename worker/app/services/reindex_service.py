from dataclasses import dataclass


@dataclass(frozen=True)
class ReindexReadiness:
    ready: bool
    reason: str


def check_reindex_readiness() -> ReindexReadiness:
    return ReindexReadiness(
        ready=False,
        reason=(
            "Reindex is not available yet because face_embeddings does not store "
            "the source image_path needed to recreate embeddings for a new model."
        ),
    )


def reindex_face_embeddings() -> None:
    readiness = check_reindex_readiness()
    if not readiness.ready:
        raise NotImplementedError(readiness.reason)
