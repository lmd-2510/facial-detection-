from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from app.api.access import router as access_router
from app.api.auth import router as auth_router
from app.api.cameras import router as cameras_router
from app.api.employees import router as employees_router
from app.api.logs import router as logs_router
from app.db.health import check_database_connection


app = FastAPI(title="DeepFace Access Control API")
app.include_router(auth_router)
app.include_router(employees_router)
app.include_router(cameras_router)
app.include_router(logs_router)
app.include_router(access_router)


@app.get("/health", response_model=None)
def health_check():
    database_ok, database_error = check_database_connection()

    if not database_ok:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "error",
                "service": "backend",
                "database": "error",
                "database_error": database_error,
            },
        )

    return {"status": "ok", "service": "backend", "database": "ok"}
