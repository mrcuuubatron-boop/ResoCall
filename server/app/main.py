from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, Response
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app.dependencies import build_context
from app.routers.analysis import router as analysis_router
from app.routers.auth import router as auth_router
from app.routers.module_settings import router as module_settings_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="ResoCall Voice Processing Server",
        version="0.1.0",
        description="Backend service for call audio processing, ASR and quality analytics.",
        docs_url=None,  # Disable default Swagger docs, we use custom monitor instead
        openapi_url=None,
    )

    app.state.ctx = build_context()
    settings = app.state.ctx.settings

    # initialize monitor state: an in-memory ring buffer for recent requests
    from collections import deque

    app.state.monitor = {"requests": deque(maxlen=200)}

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # register request-logging middleware
    try:
        from app.middleware.request_logger import RequestLoggingMiddleware

        app.add_middleware(RequestLoggingMiddleware, buffer_size=200)
    except Exception:
        pass

    app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=settings.trusted_proxy_ips_list)

    app.include_router(auth_router)
    app.include_router(analysis_router)
    from app.routers.calls import router as calls_router
    from app.routers.neural_network import router as neural_network_router

    app.include_router(calls_router)
    app.include_router(neural_network_router)
    # monitor router (runtime metrics and recent requests)
    from app.routers.monitor import router as monitor_router, router_ui as monitor_ui_router
    app.include_router(monitor_router)
    app.include_router(monitor_ui_router)  # This registers /docs and other UI routes
    # storage/admin endpoints (file listing, upload, download, user listing)
    try:
        from app.routers.storage_admin import router as storage_router

        app.include_router(storage_router)
    except Exception:
        pass
    app.include_router(module_settings_router)

    @app.get("/", include_in_schema=False)
    def root_redirect() -> RedirectResponse:
        # Keep browser/manual checks landing on the custom monitor UI.
        return RedirectResponse(url="/docs", status_code=307)

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon() -> Response:
        # Silence common browser favicon probes without polluting logs with 404.
        return Response(status_code=204)

    return app


app = create_app()
