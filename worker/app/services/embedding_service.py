from dataclasses import dataclass

from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from app.db.schema import employees, face_embeddings
from app.ml.anti_spoof import require_live_face
from app.ml.detector import require_face
from app.ml.embedder import create_face_embedding, create_face_embedding_from_face
from app.ml.photo_spoof import require_not_photo
from app.services.storage_service import resolved_image_file
from app.services.vector_store_service import upsert_face_embedding


class EmployeeNotFoundError(Exception):
    pass


@dataclass(frozen=True)
class StoredEmbedding:
    id: int
    employee_id: int
    vector: list[float]
    model_name: str
    image_path: str
    source_image_key: str


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
        detection = require_face(resolved_image.normalized_path)
        if detection.face_box is None:
            raise ValueError("Face bounding box is missing for photo check.")
        require_not_photo(
            resolved_image.normalized_path,
            face_box=detection.face_box,
        )
        require_live_face(resolved_image.normalized_path)
        face_image = getattr(detection, "face_image", None)
        embedding = (
            create_face_embedding_from_face(
                face_image,
                source_image_path=resolved_image.normalized_path,
            )
            if face_image is not None
            else create_face_embedding(resolved_image.normalized_path)
        )

    result = db.execute(
        insert(face_embeddings).values(
            employee_id=employee_id,
            vector=embedding.vector,
            model_name=embedding.model_name,
            source_image_key=image_path,
        )
    )
    embedding_id = int(result.inserted_primary_key[0])
    try:
        upsert_face_embedding(
            embedding_id=embedding_id,
            employee_id=employee_id,
            vector=embedding.vector,
            model_name=embedding.model_name,
        )
    except Exception:
        db.rollback()
        raise

    db.commit()

    return StoredEmbedding(
        id=embedding_id,
        employee_id=employee_id,
        vector=embedding.vector,
        model_name=embedding.model_name,
        image_path=image_path,
        source_image_key=image_path,
    )
