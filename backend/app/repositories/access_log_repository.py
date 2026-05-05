from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.access_log import AccessLog


def list_access_logs(db: Session) -> list[AccessLog]:
    return list(db.scalars(select(AccessLog).order_by(AccessLog.created_at.desc())))
