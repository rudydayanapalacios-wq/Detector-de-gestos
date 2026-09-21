from fastapi import FastAPI

app = FastAPI(
    title="Detector de Gestos API",
    description="API para detección de gestos mediante visión por computador.",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "message": "Detector de Gestos API funcionando"
    }