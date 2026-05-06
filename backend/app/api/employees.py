from fastapi import APIRouter, HTTPException, Response, status

from app.core.deps import CurrentUser, DbSession
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeEmbeddingJobRequest,
    EmployeeEmbeddingJobResponse,
    EmployeeRead,
    EmployeeUpdate,
)
from app.services.employee_service import (
    EmployeeCodeAlreadyExistsError,
    EmployeeNotFoundError,
    add_employee,
    delete_employee,
    edit_employee,
    get_embedding_queue_name,
    get_employee,
    get_employees,
    queue_employee_embedding_job,
)


router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("", response_model=list[EmployeeRead])
def list_employee_records(
    db: DbSession,
    current_user: CurrentUser,
) -> list[EmployeeRead]:
    return get_employees(db)


@router.post("", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED)
def create_employee_record(
    payload: EmployeeCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> EmployeeRead:
    try:
        return add_employee(db, payload)
    except EmployeeCodeAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee code already exists",
        ) from exc


@router.get("/{employee_id}", response_model=EmployeeRead)
def read_employee_record(
    employee_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> EmployeeRead:
    employee = get_employee(db, employee_id)
    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    return employee


@router.put("/{employee_id}", response_model=EmployeeRead)
def update_employee_record(
    employee_id: int,
    payload: EmployeeUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> EmployeeRead:
    try:
        employee = edit_employee(db, employee_id, payload)
    except EmployeeCodeAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee code already exists",
        ) from exc

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    return employee


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee_record(
    employee_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> Response:
    employee = delete_employee(db, employee_id)
    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{employee_id}/embedding-jobs",
    response_model=EmployeeEmbeddingJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_employee_embedding_job(
    employee_id: int,
    payload: EmployeeEmbeddingJobRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> EmployeeEmbeddingJobResponse:
    try:
        job = queue_employee_embedding_job(db, employee_id, payload.image_path)
    except EmployeeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        ) from exc

    return EmployeeEmbeddingJobResponse(
        job_id=job.job_id,
        type=job.type,
        employee_id=job.employee_id,
        image_path=job.image_path,
        queue_name=get_embedding_queue_name(),
        message="Embedding job queued. Worker will process it in background.",
    )
