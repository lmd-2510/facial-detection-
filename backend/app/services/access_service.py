from sqlalchemy.orm import Session

from app.models.access_log import AccessLog
from app.repositories.access_log_repository import create_access_log
from app.repositories.camera_repository import get_camera_by_id
from app.schemas.access import AccessCheckRequest


class CameraNotFoundError(Exception):
    pass


def check_access(db: Session, payload: AccessCheckRequest) -> AccessLog:
    camera = get_camera_by_id(db, payload.camera_id)
    if camera is None:
        raise CameraNotFoundError

    return create_access_log(
        db,
        employee_id=None,
        camera_id=camera.id,
        status="denied",
        score=None,
        image_path=payload.image_path,
    )
