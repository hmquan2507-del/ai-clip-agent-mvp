from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.v1.router import api_router
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.middleware.request_id import RequestIDMiddleware

configure_logging()

app = FastAPI(
    title="AI Clip Agent API",
    version="1.0.0",
)

app.add_middleware(RequestIDMiddleware)

app.include_router(api_router)
app.include_router(health_router)

register_exception_handlers(app)


@app.get("/")
def root():
    return {
        "name": "AI Clip Agent API",
        "status": "running",
        "version": "1.0.0",
    }