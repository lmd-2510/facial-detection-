import logging
from typing import Any


def handle_embedding_job(payload: dict[str, Any]) -> None:
    job_id = payload.get("job_id")
    employee_id = payload.get("employee_id")
    image_path = payload.get("image_path")

    if not job_id or not employee_id or not image_path:
        raise ValueError(f"Invalid embedding job payload: {payload}")

    logging.info(
        "Received embedding job: job_id=%s employee_id=%s image_path=%s",
        job_id,
        employee_id,
        image_path,
    )
    logging.info("Embedding AI pipeline is not implemented yet; job logged only.")
