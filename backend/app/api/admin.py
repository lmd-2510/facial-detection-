from fastapi import APIRouter

from app.config.redis import check_redis_connection, get_redis_client
from app.core.deps import AdminUser
from app.db.health import check_database_connection


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/status")
def read_admin_status(current_user: AdminUser) -> dict[str, object]:
    database_ok, database_error = check_database_connection()
    redis_ok, redis_error = check_redis_connection()

    queue_lengths: dict[str, int] = {}
    if redis_ok:
        redis_client = get_redis_client()
        queue_lengths = {
            "embedding_jobs": int(redis_client.llen("embedding_jobs")),
            "access_jobs": int(redis_client.llen("access_jobs")),
        }

    return {
        "status": "ok" if database_ok and redis_ok else "degraded",
        "database": "ok" if database_ok else "error",
        "database_error": database_error,
        "redis": "ok" if redis_ok else "error",
        "redis_error": redis_error,
        "queue_lengths": queue_lengths,
    }
