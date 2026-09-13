"""Loopback development adapter. Future adapters call the same Core commands."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

from .commands import TaskRequest, ToolCall
from .config import Settings
from .core import Core


def create_app(settings=None):
    settings = settings or Settings.from_env()
    core = Core(settings)

    @asynccontextmanager
    async def lifespan(app):
        await core.start()
        try:
            yield
        finally:
            await core.stop()

    app = FastAPI(title="Aphrael local foundation", lifespan=lifespan)
    app.state.core = core

    @app.middleware("http")
    async def local_boundary(request: Request, call_next):
        # Prevent DNS rebinding and foreign web pages from driving local tools.
        host = request.url.hostname
        if host not in {"127.0.0.1", "localhost", "::1", "testserver"}:
            return JSONResponse({"error": "Local host required"}, status_code=403)
        origin = request.headers.get("origin")
        if origin and origin != f"{request.url.scheme}://{request.url.netloc}":
            return JSONResponse({"error": "Same-origin requests required"}, status_code=403)
        if request.headers.get("sec-fetch-site") == "cross-site":
            return JSONResponse({"error": "Cross-site request denied"}, status_code=403)
        if request.method == "POST" and request.headers.get("content-type", "").split(";")[0] != "application/json":
            return JSONResponse({"error": "JSON body required"}, status_code=415)
        try:
            length = int(request.headers.get("content-length", "0"))
        except ValueError:
            return JSONResponse({"error": "Invalid content length"}, status_code=400)
        if length < 0:
            return JSONResponse({"error": "Invalid content length"}, status_code=400)
        if length > 65536:
            return JSONResponse({"error": "Request too large"}, status_code=413)
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        return response

    @app.exception_handler(ValueError)
    async def invalid(request, exc):
        return JSONResponse({"error": str(exc)}, status_code=400)

    @app.exception_handler(PermissionError)
    async def denied(request, exc):
        return JSONResponse({"error": str(exc)}, status_code=403)

    @app.exception_handler(KeyError)
    async def missing(request, exc):
        return JSONResponse({"error": "Task not found"}, status_code=404)

    @app.get("/", response_class=HTMLResponse)
    def index():
        return Path(__file__).with_name("index.html").read_text(encoding="utf-8")

    @app.get("/api/health")
    def health():
        result = core.health()
        return JSONResponse(result, status_code=200 if result["healthy"] else 503)

    @app.get("/api/tools")
    def tools():
        return core.registry.describe()

    @app.get("/api/profiles")
    def profiles():
        return core.profiles()

    @app.post("/api/tools/invoke")
    async def invoke(body: ToolCall):
        return await core.immediate(body.tool, body.arguments)

    @app.post("/api/tasks", status_code=201)
    def create(body: TaskRequest):
        return core.create_task(body.model_dump())

    @app.get("/api/tasks")
    def recent(limit: int = 50):
        return core.store.recent(max(1, min(limit, 100)))

    @app.get("/api/tasks/{task_id}")
    def get_task(task_id: str):
        return core.store.get(task_id)

    @app.post("/api/tasks/{task_id}/cancel")
    def cancel(task_id: str):
        return core.cancel(task_id)

    return app
