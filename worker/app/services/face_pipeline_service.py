from dataclasses import dataclass

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.db.schema import access_logs, employees, face_embeddings
from app.ml.anti_spoof import require_live_face
from app.ml.detector import require_face
from app.ml.embedder import create_face_embedding
from app.ml.matcher import DEFAULT_MATCH_THRESHOLD, MatchCandidate, find_best_match
from app.services.storage_service import resolved_image_file


class AccessLogNotFoundError(Exception):
    pass


@dataclass(frozen=True)
class AccessDecision:
    log_id: int
    status: str
    employee_id: int | None
    score: float | None
    image_path: str
    message: str


def _load_active_embedding_candidates(
    db: Session,
    *,
    model_name: str,
) -> list[MatchCandidate]:
    rows = db.execute(
        select(
            face_embeddings.c.employee_id,
            face_embeddings.c.vector,
            face_embeddings.c.model_name,
        )
        .join(employees, employees.c.id == face_embeddings.c.employee_id)
        .where(employees.c.status == "active")
        .where(face_embeddings.c.model_name == model_name)
    )

    return [
        MatchCandidate(
            employee_id=int(row.employee_id),
            vector=row.vector,
            model_name=row.model_name,
        )
        for row in rows
    ]


def _update_access_log(
    db: Session,
    *,
    log_id: int,
    status: str,
    employee_id: int | None,
    score: float | None,
) -> None:
    result = db.execute(
        update(access_logs)
        .where(access_logs.c.id == log_id)
        .values(status=status, employee_id=employee_id, score=score)
    )
    if result.rowcount == 0:
        db.rollback()
        raise AccessLogNotFoundError(f"Access log not found: {log_id}")

    db.commit()


def process_access_check(
    db: Session,
    *,
    log_id: int,
    image_path: str,
    threshold: float = DEFAULT_MATCH_THRESHOLD,
) -> AccessDecision:
    existing_log = db.execute(
        select(access_logs.c.id).where(access_logs.c.id == log_id)
    ).first()
    if existing_log is None:
        raise AccessLogNotFoundError(f"Access log not found: {log_id}")

    try:
        with resolved_image_file(image_path) as resolved_image:
            require_face(resolved_image.normalized_path)
            require_live_face(resolved_image.normalized_path)
            embedding = create_face_embedding(resolved_image.normalized_path)
            match = find_best_match(
                embedding.vector,
                _load_active_embedding_candidates(db, model_name=embedding.model_name),
                threshold=threshold,
            )

        if match.matched:
            status = "granted"
            employee_id = match.employee_id
        else:
            status = "denied"
            employee_id = None

        _update_access_log(
            db,
            log_id=log_id,
            status=status,
            employee_id=employee_id,
            score=match.score,
        )
        return AccessDecision(
            log_id=log_id,
            status=status,
            employee_id=employee_id,
            score=match.score,
            image_path=image_path,
            message=match.message,
        )
    except Exception as exc:
        _update_access_log(
            db,
            log_id=log_id,
            status="error",
            employee_id=None,
            score=None,
        )
        return AccessDecision(
            log_id=log_id,
            status="error",
            employee_id=None,
            score=None,
            image_path=image_path,
            message=str(exc),
        )
