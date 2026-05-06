import logging
from typing import Any


def handle_access_job(payload: dict[str, Any]) -> None:
    job_id = payload.get("job_id")
    log_id = payload.get("log_id")
    camera_id = payload.get("camera_id")
    image_path = payload.get("image_path")

    if not job_id or not log_id or not camera_id or not image_path:
        raise ValueError(f"Invalid access job payload: {payload}")

    logging.info(
        "Received access job: job_id=%s log_id=%s camera_id=%s image_path=%s",
        job_id,
        log_id,
        camera_id,
        image_path,
    )
    logging.info("Access AI pipeline is not implemented yet; job logged only.")
