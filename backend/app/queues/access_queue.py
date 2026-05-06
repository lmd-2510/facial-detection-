import json
from dataclasses import asdict, dataclass
from typing import Literal
from uuid import uuid4

from app.config.redis import get_redis_client


ACCESS_QUEUE_NAME = "access_jobs"


@dataclass(frozen=True)
class AccessJob:
    job_id: str
    type: Literal["access_check"]
    log_id: int
    camera_id: int
    image_path: str

    def to_payload(self) -> dict[str, object]:
        return asdict(self)


def build_access_job(log_id: int, camera_id: int, image_path: str) -> AccessJob:
    return AccessJob(
        job_id=str(uuid4()),
        type="access_check",
        log_id=log_id,
        camera_id=camera_id,
        image_path=image_path,
    )


def enqueue_access_job(log_id: int, camera_id: int, image_path: str) -> AccessJob:
    job = build_access_job(log_id, camera_id, image_path)
    redis_client = get_redis_client()
    redis_client.rpush(ACCESS_QUEUE_NAME, json.dumps(job.to_payload()))
    return job
