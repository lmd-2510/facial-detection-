from sqlalchemy.orm import Session

from app.models.camera import Camera
from app.repositories.camera_repository import create_camera, list_cameras
from app.schemas.camera import CameraCreate


def get_cameras(db: Session) -> list[Camera]:
    return list_cameras(db)


def add_camera(db: Session, payload: CameraCreate) -> Camera:
    return create_camera(db, payload)
