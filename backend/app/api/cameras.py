from fastapi import APIRouter, status

from app.core.deps import AdminUser, DbSession
from app.schemas.camera import CameraCreate, CameraRead
from app.services.camera_service import add_camera, get_cameras


router = APIRouter(prefix="/cameras", tags=["cameras"])


@router.get("", response_model=list[CameraRead])
def list_camera_records(
    db: DbSession,
    current_user: AdminUser,
) -> list[CameraRead]:
    return get_cameras(db)


@router.post("", response_model=CameraRead, status_code=status.HTTP_201_CREATED)
def create_camera_record(
    payload: CameraCreate,
    db: DbSession,
    current_user: AdminUser,
) -> CameraRead:
    return add_camera(db, payload)
