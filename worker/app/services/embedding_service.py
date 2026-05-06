from dataclasses import dataclass

from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from app.db.schema import employees, face_embeddings
from app.ml.anti_spoof import require_live_face
from app.ml.detector import require_face
from app.ml.embedder import FAKE_MODEL_NAME, create_fake_embedding


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

    require_face(image_path)
    require_live_face(image_path)
    embedding = create_fake_embedding(image_path)

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
        model_name=FAKE_MODEL_NAME,
        image_path=embedding.image_path,
    )
