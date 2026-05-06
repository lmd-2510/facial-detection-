from sqlalchemy.orm import Session

from app.models.access_log import AccessLog
from app.queues.access_queue import AccessJob, enqueue_access_job
from app.repositories.access_log_repository import create_access_log
from app.repositories.camera_repository import get_camera_by_id
from app.schemas.access import AccessCheckRequest


class CameraNotFoundError(Exception):
    pass


def check_access(db: Session, payload: AccessCheckRequest) -> tuple[AccessLog, AccessJob]:
    camera = get_camera_by_id(db, payload.camera_id)
    if camera is None:
        raise CameraNotFoundError

    access_log = create_access_log(
        db,
        employee_id=None,
        camera_id=camera.id,
        status="processing",
        score=None,
        image_path=payload.image_path,
    )
    job = enqueue_access_job(
        log_id=access_log.id,
        camera_id=camera.id,
        image_path=payload.image_path,
    )
    return access_log, job
