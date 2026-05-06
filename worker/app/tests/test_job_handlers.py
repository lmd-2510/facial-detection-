from contextlib import contextmanager

from app.tasks.access_job import handle_access_job
from app.tasks.embedding_job import handle_embedding_job


@contextmanager
def fake_db_session():
    yield "db-session"


def test_handle_embedding_job_calls_embedding_service(monkeypatch):
    calls = []

    class FakeEmbedding:
        id = 10
        model_name = "fake-hash-embedding-v1"

    def fake_create_employee_embedding(db, *, employee_id: int, image_path: str):
        calls.append(
            {
                "db": db,
                "employee_id": employee_id,
                "image_path": image_path,
            }
        )
        return FakeEmbedding()

    monkeypatch.setattr("app.tasks.embedding_job.get_db_session", fake_db_session)
    monkeypatch.setattr(
        "app.tasks.embedding_job.create_employee_embedding",
        fake_create_employee_embedding,
    )

    handle_embedding_job(
        {
            "job_id": "job-1",
            "employee_id": 1,
            "image_path": "/app/storage/uploads/employee_1.jpg",
        }
    )

    assert calls == [
        {
            "db": "db-session",
            "employee_id": 1,
            "image_path": "/app/storage/uploads/employee_1.jpg",
        }
    ]


def test_handle_access_job_calls_access_pipeline(monkeypatch):
    calls = []

    class FakeDecision:
        status = "granted"
        employee_id = 1
        score = 1.0

    def fake_process_access_check(db, *, log_id: int, image_path: str):
        calls.append(
            {
                "db": db,
                "log_id": log_id,
                "image_path": image_path,
            }
        )
        return FakeDecision()

    monkeypatch.setattr("app.tasks.access_job.get_db_session", fake_db_session)
    monkeypatch.setattr(
        "app.tasks.access_job.process_access_check",
        fake_process_access_check,
    )

    handle_access_job(
        {
            "job_id": "job-1",
            "log_id": 1,
            "camera_id": 1,
            "image_path": "/app/storage/uploads/snapshot.jpg",
        }
    )

    assert calls == [
        {
            "db": "db-session",
            "log_id": 1,
            "image_path": "/app/storage/uploads/snapshot.jpg",
        }
    ]
