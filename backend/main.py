from fastapi import FastAPI

from app.routers.auth import router as auth_router


app = FastAPI(
    title="Detector de Gestos API",
    description="API para detección de gestos mediante visión por computador.",
    version="1.0.0"
)


app.include_router(auth_router)


@app.get("/")
def root():
    return {
        "message": "Detector de Gestos API funcionando"
    }