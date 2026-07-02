from fastapi import FastAPI

app = FastAPI(
    title="AI Clip Agent API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/")
def root():
    return {
        "name": "AI Clip Agent API",
        "status": "running",
        "version": "0.1.0",
    }