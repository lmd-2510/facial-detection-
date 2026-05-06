from fastapi import APIRouter, HTTPException, status

from app.core.deps import CurrentUser, DbSession
from app.schemas.access import AccessCheckRequest, AccessCheckResponse
from app.services.access_service import CameraNotFoundError, check_access


router = APIRouter(prefix="/access", tags=["access"])


@router.post(
    "/check",
    response_model=AccessCheckResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def check_access_record(
    payload: AccessCheckRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> AccessCheckResponse:
    try:
        access_log, job = check_access(db, payload)
    except CameraNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found",
        ) from exc

    return AccessCheckResponse(
        log_id=access_log.id,
        job_id=job.job_id,
        status=access_log.status,
        employee_id=access_log.employee_id,
        camera_id=access_log.camera_id,
        score=access_log.score,
        image_path=access_log.image_path,
        message="Access check queued. Worker will process it in background.",
        created_at=access_log.created_at,
    )
