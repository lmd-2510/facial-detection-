from dataclasses import dataclass

from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from app.db.schema import employees, face_embeddings
from app.ml.anti_spoof import require_live_face
from app.ml.detector import require_face
from app.ml.embedder import create_face_embedding
from app.services.storage_service import resolved_image_file


class EmployeeNotFoundError(Exception):
    pass


@dataclass(frozen=True)
class StoredEmbedding:
    id: int
    employee_id: int
    vector: list[float]
    model_name: str
    image_path: str


def create_employee_embedding(
    db: Session,
    *,
    employee_id: int,
    image_path: str,
) -> StoredEmbedding:
    employee = db.execute(
        select(employees.c.id).where(employees.c.id == employee_id)
    ).first()
    if employee is None:
        raise EmployeeNotFoundError(f"Employee not found: {employee_id}")

    with resolved_image_file(image_path) as resolved_image:
        require_face(resolved_image.normalized_path)
        require_live_face(resolved_image.normalized_path)
        embedding = create_face_embedding(resolved_image.normalized_path)

    result = db.execute(
        insert(face_embeddings).values(
            employee_id=employee_id,
            vector=embedding.vector,
            model_name=embedding.model_name,
        )
    )
    db.commit()

    return StoredEmbedding(
        id=int(result.inserted_primary_key[0]),
        employee_id=employee_id,
        vector=embedding.vector,
        model_name=embedding.model_name,
        image_path=image_path,
    )
