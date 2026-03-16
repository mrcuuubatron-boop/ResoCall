from fastapi import FastAPI

from app.dependencies import build_context
from app.routers.analysis import router as analysis_router
from app.routers.auth import router as auth_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="ResoCall Voice Processing Server",
        version="0.1.0",
        description="Backend service for call audio processing, ASR and quality analytics.",
    )

    app.state.ctx = build_context()
    app.include_router(auth_router)
    app.include_router(analysis_router)
    return app


app = create_app()
