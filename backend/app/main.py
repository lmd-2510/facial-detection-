from fastapi import FastAPI


app = FastAPI(title="DeepFace Access Control API")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "backend"}
