from collections import deque
from time import perf_counter
from typing import Deque, Dict, Any

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, buffer_size: int = 200):
        super().__init__(app)
        self.buffer_size = buffer_size

    async def dispatch(self, request: Request, call_next):
        start = perf_counter()
        client_host = None
        try:
            client_host = request.client.host if request.client is not None else None
        except Exception:
            client_host = None

        try:
            response = await call_next(request)
            status = response.status_code
        except Exception as exc:
            status = 500
            raise
        finally:
            duration = perf_counter() - start
            monitor = getattr(request.app.state, "monitor", None)
            path = request.url.path
            entry: Dict[str, Any] = {
                "ts": request.scope.get("time", None),
                "method": request.method,
                "path": path,
                "client": client_host,
                "status": status,
                "duration_s": round(duration, 4),
            }
            # don't log monitor requests (so the monitor doesn't show itself)
            try:
                ignore_prefixes = ("/api/v1/monitor", "/docs")
                if monitor is not None and not any(path.startswith(p) for p in ignore_prefixes):
                    monitor_requests: Deque = monitor.get("requests")
                    monitor_requests.append(entry)
            except Exception:
                pass
        return response
