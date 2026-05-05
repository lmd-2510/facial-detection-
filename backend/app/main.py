from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from app.db.health import check_database_connection


app = FastAPI(title="DeepFace Access Control API")


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
