from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.v1.router import api_router
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.middleware.request_id import RequestIDMiddleware
from app.api.v1.hook_detection import router as hook_detection_router
from app.api.v1.story_engine import router as story_engine_router
from app.api.v1.emotion_engine import router as emotion_engine_router
from app.api.v1.ai_brain import router as ai_brain_router
from app.api.v1.editing_style import router as editing_style_router
from app.api.v1.decision_engine import router as decision_engine_router
from app.api.v1.editing_execution_planner import router as editing_execution_planner_router


configure_logging()

app = FastAPI(
    title="AI Clip Agent API",
    version="1.0.0",
)

app.add_middleware(RequestIDMiddleware)
app.include_router(hook_detection_router, prefix="/api/v1")
app.include_router(api_router)
app.include_router(health_router)
app.include_router(story_engine_router, prefix="/api/v1")
register_exception_handlers(app)
app.include_router(emotion_engine_router, prefix="/api/v1")
app.include_router(ai_brain_router, prefix="/api/v1")
app.include_router(editing_style_router, prefix="/api/v1")
app.include_router(decision_engine_router, prefix="/api/v1")
app.include_router(editing_execution_planner_router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "name": "AI Clip Agent API",
        "status": "running",
        "version": "1.0.0",
    }