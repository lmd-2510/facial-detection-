import logging
from typing import Any

from app.config.database import get_db_session
from app.services.embedding_service import create_employee_embedding


def handle_embedding_job(payload: dict[str, Any]) -> None:
    job_id = payload.get("job_id")
    employee_id = payload.get("employee_id")
    image_path = payload.get("image_key") or payload.get("image_path")

    if not job_id or not employee_id or not image_path:
        raise ValueError(f"Invalid embedding job payload: {payload}")

    logging.info(
        "Received embedding job: job_id=%s employee_id=%s image_path=%s",
        job_id,
        employee_id,
        image_path,
    )
    with get_db_session() as db:
        embedding = create_employee_embedding(
            db,
            employee_id=int(employee_id),
            image_path=str(image_path),
        )

    logging.info(
        "Embedding job completed: job_id=%s employee_id=%s embedding_id=%s model=%s",
        job_id,
        employee_id,
        embedding.id,
        embedding.model_name,
    )
