from dataclasses import dataclass
from os import getenv


@dataclass(frozen=True)
class Settings:
    database_url: str = getenv(
        "DATABASE_URL",
        "postgresql://deepface:deepface@localhost:5432/deepface_access",
    )
    auth_secret_key: str = getenv(
        "AUTH_SECRET_KEY",
        "deepface-access-dev-secret",
    )
    access_token_expire_minutes: int = int(
        getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
    )


settings = Settings()
