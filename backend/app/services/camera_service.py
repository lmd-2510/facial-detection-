from sqlalchemy.orm import Session

from app.models.camera import Camera
from app.repositories.camera_repository import (
    create_camera,
    get_camera_by_id,
    get_latest_active_camera,
    list_cameras,
    soft_delete_camera,
    update_camera,
)
from app.schemas.camera import CameraCreate, CameraUpdate


def get_cameras(db: Session) -> list[Camera]:
    return list_cameras(db)


def get_camera(db: Session, camera_id: int) -> Camera | None:
    return get_camera_by_id(db, camera_id)


def get_default_active_camera(db: Session) -> Camera | None:
    return get_latest_active_camera(db)


def add_camera(db: Session, payload: CameraCreate) -> Camera:
    return create_camera(db, payload)


def edit_camera(
    db: Session,
    camera_id: int,
    payload: CameraUpdate,
) -> Camera | None:
    camera = get_camera_by_id(db, camera_id)
    if camera is None:
        return None

    return update_camera(db, camera, payload)


def delete_camera(db: Session, camera_id: int) -> Camera | None:
    camera = get_camera_by_id(db, camera_id)
    if camera is None:
        return None

    return soft_delete_camera(db, camera)
