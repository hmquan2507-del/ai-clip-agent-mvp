from fastapi import FastAPI

from app.api.v1.router import api_router

app = FastAPI(
    title="AI Clip Agent API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(api_router)


@app.get("/")
def root():
    return {
        "name": "AI Clip Agent API",
        "status": "running",
        "version": "0.1.0",
    }