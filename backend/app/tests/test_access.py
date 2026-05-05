import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.camera import Camera
from app.models.user import User


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    Base.metadata.create_all(bind=engine)

    with testing_session_local() as db:
        db.add(
            User(
                username="admin",
                password_hash=hash_password("admin123"),
                role="admin",
            )
        )
        db.add(
            Camera(
                name="Main Gate",
                location="Lobby",
                stream_url=None,
                status="active",
            )
        )
        db.commit()

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client):
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_access_check_requires_auth(client):
    response = client.post(
        "/access/check",
        json={
            "camera_id": 1,
            "image_path": "/app/storage/uploads/snapshot.jpg",
        },
    )

    assert response.status_code == 401


def test_access_check_returns_404_for_missing_camera(client, auth_headers):
    response = client.post(
        "/access/check",
        headers=auth_headers,
        json={
            "camera_id": 999,
            "image_path": "/app/storage/uploads/snapshot.jpg",
        },
    )

    assert response.status_code == 404


def test_access_check_records_placeholder_log(client, auth_headers):
    response = client.post(
        "/access/check",
        headers=auth_headers,
        json={
            "camera_id": 1,
            "image_path": "/app/storage/uploads/snapshot.jpg",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["log_id"]
    assert body["status"] == "denied"
    assert body["employee_id"] is None
    assert body["camera_id"] == 1
    assert body["score"] is None
    assert body["image_path"] == "/app/storage/uploads/snapshot.jpg"
    assert body["created_at"]

    logs_response = client.get("/logs", headers=auth_headers)
    assert logs_response.status_code == 200
    logs_body = logs_response.json()
    assert len(logs_body) == 1
    assert logs_body[0]["id"] == body["log_id"]
    assert logs_body[0]["status"] == "denied"
