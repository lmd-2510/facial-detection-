import pytest
from sqlalchemy import create_engine, insert, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.schema import access_logs, employees, face_embeddings, metadata
from app.services.embedding_service import (
    EmployeeNotFoundError,
    create_employee_embedding,
)
from app.services.face_pipeline_service import (
    AccessLogNotFoundError,
    process_access_check,
)


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    metadata.create_all(engine)
    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    db = testing_session_local()
    try:
        yield db
    finally:
        db.close()


def seed_employee(db_session, *, employee_id: int = 1, status: str = "active") -> None:
    db_session.execute(
        insert(employees).values(
            id=employee_id,
            code=f"EMP{employee_id:03d}",
            name=f"Employee {employee_id}",
            department="Security",
            status=status,
        )
    )
    db_session.commit()


def seed_access_log(
    db_session,
    *,
    log_id: int = 1,
    image_path: str = "/app/storage/uploads/snapshot.jpg",
) -> None:
    db_session.execute(
        insert(access_logs).values(
            id=log_id,
            employee_id=None,
            camera_id=1,
            status="processing",
            score=None,
            image_path=image_path,
        )
    )
    db_session.commit()


def get_access_log(db_session, log_id: int):
    return db_session.execute(
        select(access_logs).where(access_logs.c.id == log_id)
    ).first()


def test_create_employee_embedding_stores_fake_embedding(db_session):
    seed_employee(db_session)

    stored_embedding = create_employee_embedding(
        db_session,
        employee_id=1,
        image_path="/app/storage/uploads/employee_1.jpg",
    )

    assert stored_embedding.id == 1
    assert stored_embedding.employee_id == 1
    assert stored_embedding.model_name == "fake-hash-embedding-v1"
    assert len(stored_embedding.vector) == 16

    row = db_session.execute(select(face_embeddings)).first()
    assert row is not None
    assert row.employee_id == 1
    assert row.vector == stored_embedding.vector


def test_create_employee_embedding_rejects_missing_employee(db_session):
    with pytest.raises(EmployeeNotFoundError):
        create_employee_embedding(
            db_session,
            employee_id=999,
            image_path="/app/storage/uploads/employee_1.jpg",
        )


def test_process_access_check_grants_matching_active_employee(db_session):
    seed_employee(db_session)
    create_employee_embedding(
        db_session,
        employee_id=1,
        image_path="/app/storage/uploads/employee_1.jpg",
    )
    seed_access_log(
        db_session,
        log_id=1,
        image_path="/app/storage/uploads/employee_1.jpg",
    )

    decision = process_access_check(
        db_session,
        log_id=1,
        image_path="/app/storage/uploads/employee_1.jpg",
    )

    assert decision.status == "granted"
    assert decision.employee_id == 1
    assert decision.score == 1.0

    row = get_access_log(db_session, 1)
    assert row.status == "granted"
    assert row.employee_id == 1
    assert row.score == 1.0


def test_process_access_check_denies_when_no_embeddings_exist(db_session):
    seed_access_log(db_session, log_id=1)

    decision = process_access_check(
        db_session,
        log_id=1,
        image_path="/app/storage/uploads/snapshot.jpg",
    )

    assert decision.status == "denied"
    assert decision.employee_id is None
    assert decision.score is None

    row = get_access_log(db_session, 1)
    assert row.status == "denied"
    assert row.employee_id is None
    assert row.score is None


def test_process_access_check_marks_log_error_when_pipeline_fails(db_session):
    seed_access_log(
        db_session,
        log_id=1,
        image_path="/app/storage/uploads/no_face.jpg",
    )

    decision = process_access_check(
        db_session,
        log_id=1,
        image_path="/app/storage/uploads/no_face.jpg",
    )

    assert decision.status == "error"
    assert "No face detected" in decision.message

    row = get_access_log(db_session, 1)
    assert row.status == "error"
    assert row.employee_id is None
    assert row.score is None


def test_process_access_check_raises_for_missing_log(db_session):
    with pytest.raises(AccessLogNotFoundError):
        process_access_check(
            db_session,
            log_id=999,
            image_path="/app/storage/uploads/snapshot.jpg",
        )
