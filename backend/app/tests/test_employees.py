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
from app.models.employee import Employee
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
            Employee(
                code="EMP001",
                name="Nguyen Van A",
                department="Security",
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


def test_list_employees_requires_auth(client):
    response = client.get("/employees")

    assert response.status_code == 401


def test_list_employees(client, auth_headers):
    response = client.get("/employees", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["code"] == "EMP001"


def test_create_employee(client, auth_headers):
    response = client.post(
        "/employees",
        headers=auth_headers,
        json={
            "code": "EMP002",
            "name": "Tran Thi B",
            "department": "Operations",
            "status": "active",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"]
    assert body["code"] == "EMP002"
    assert body["name"] == "Tran Thi B"


def test_create_employee_rejects_duplicate_code(client, auth_headers):
    response = client.post(
        "/employees",
        headers=auth_headers,
        json={
            "code": "EMP001",
            "name": "Duplicate",
            "department": None,
            "status": "active",
        },
    )

    assert response.status_code == 409


def test_get_employee_by_id(client, auth_headers):
    response = client.get("/employees/1", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["code"] == "EMP001"


def test_get_employee_by_id_returns_404(client, auth_headers):
    response = client.get("/employees/999", headers=auth_headers)

    assert response.status_code == 404


def test_update_employee(client, auth_headers):
    response = client.put(
        "/employees/1",
        headers=auth_headers,
        json={
            "name": "Nguyen Van A Updated",
            "department": "Admin",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == "EMP001"
    assert body["name"] == "Nguyen Van A Updated"
    assert body["department"] == "Admin"


def test_delete_employee_soft_deletes_record(client, auth_headers):
    delete_response = client.delete("/employees/1", headers=auth_headers)

    assert delete_response.status_code == 204

    get_response = client.get("/employees/1", headers=auth_headers)
    assert get_response.status_code == 200
    assert get_response.json()["status"] == "inactive"
