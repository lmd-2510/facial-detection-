import json
from dataclasses import asdict, dataclass
from typing import Literal
from uuid import uuid4

from app.config.redis import get_redis_client


EMBEDDING_QUEUE_NAME = "embedding_jobs"


@dataclass(frozen=True)
class EmbeddingJob:
    job_id: str
    type: Literal["embedding"]
    employee_id: int
    image_path: str

    def to_payload(self) -> dict[str, object]:
        return asdict(self)


def build_embedding_job(employee_id: int, image_path: str) -> EmbeddingJob:
    return EmbeddingJob(
        job_id=str(uuid4()),
        type="embedding",
        employee_id=employee_id,
        image_path=image_path,
    )


def enqueue_embedding_job(employee_id: int, image_path: str) -> EmbeddingJob:
    job = build_embedding_job(employee_id, image_path)
    redis_client = get_redis_client()
    redis_client.rpush(EMBEDDING_QUEUE_NAME, json.dumps(job.to_payload()))
    return job
