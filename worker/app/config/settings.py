from dataclasses import dataclass
from os import getenv


@dataclass(frozen=True)
class Settings:
    redis_url: str = getenv("REDIS_URL", "redis://localhost:6379/0")
    database_url: str = getenv(
        "DATABASE_URL",
        "postgresql://deepface:deepface@localhost:5432/deepface_access",
    )


settings = Settings()
