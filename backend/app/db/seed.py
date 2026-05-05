from os import getenv

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.init_db import create_tables
from app.db.session import SessionLocal
from app.models.user import User


DEMO_USERS = [
    {
        "username": getenv("SEED_ADMIN_USERNAME", "admin"),
        "password": getenv("SEED_ADMIN_PASSWORD", "admin123"),
        "role": "admin",
    },
    {
        "username": getenv("SEED_USER_USERNAME", "user"),
        "password": getenv("SEED_USER_PASSWORD", "user123"),
        "role": "user",
    },
]


def seed_users(db: Session) -> int:
    created_count = 0

    for demo_user in DEMO_USERS:
        existing_user = db.scalar(
            select(User).where(User.username == demo_user["username"])
        )
        if existing_user is not None:
            continue

        db.add(
            User(
                username=demo_user["username"],
                password_hash=hash_password(demo_user["password"]),
                role=demo_user["role"],
            )
        )
        created_count += 1

    db.commit()
    return created_count


def main() -> None:
    try:
        create_tables()
        with SessionLocal() as db:
            created_count = seed_users(db)
    except SQLAlchemyError as exc:
        raise SystemExit(f"Database seed failed: {exc}") from exc

    print(f"Seed data is ready. Created users: {created_count}.")


if __name__ == "__main__":
    main()
