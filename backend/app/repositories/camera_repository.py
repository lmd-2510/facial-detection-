from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.camera import Camera
from app.schemas.camera import CameraCreate, CameraUpdate


def list_cameras(db: Session) -> list[Camera]:
    return list(db.scalars(select(Camera).order_by(Camera.id)))


def get_camera_by_id(db: Session, camera_id: int) -> Camera | None:
    return db.get(Camera, camera_id)


def create_camera(db: Session, payload: CameraCreate) -> Camera:
    camera = Camera(**payload.model_dump())
    db.add(camera)
    db.commit()
    db.refresh(camera)
    return camera


def update_camera(db: Session, camera: Camera, payload: CameraUpdate) -> Camera:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(camera, field, value)

    db.commit()
    db.refresh(camera)
    return camera


def soft_delete_camera(db: Session, camera: Camera) -> Camera:
    camera.status = "inactive"
    db.commit()
    db.refresh(camera)
    return camera
