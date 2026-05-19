from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.access_log import AccessLog


def list_access_logs(db: Session) -> list[AccessLog]:
    return list(
        db.scalars(
            select(AccessLog)
            .options(selectinload(AccessLog.employee))
            .order_by(AccessLog.created_at.desc())
        )
    )


def create_access_log(
    db: Session,
    *,
    employee_id: int | None,
    camera_id: int | None,
    status: str,
    score: float | None,
    image_path: str | None,
    message: str | None = None,
) -> AccessLog:
    access_log = AccessLog(
        employee_id=employee_id,
        camera_id=camera_id,
        status=status,
        score=score,
        image_path=image_path,
        message=message,
    )
    db.add(access_log)
    db.commit()
    db.refresh(access_log)
    return access_log
