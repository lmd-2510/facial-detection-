from sqlalchemy.exc import SQLAlchemyError

from app.db.base import Base
from app.db.session import engine

# Import models so SQLAlchemy registers every table before create_all runs.
import app.models  # noqa: F401


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def main() -> None:
    try:
        create_tables()
    except SQLAlchemyError as exc:
        raise SystemExit(f"Database initialization failed: {exc}") from exc

    print("Database tables are ready.")


if __name__ == "__main__":
    main()
