import json
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse

from app.schemas import (
    AnalysisResultOut,
    ErrorOut,
    TaskCreatedOut,
    TaskOut,
    TaskStatus,
    TasksListOut,
    UserContext,
)
from app.security import get_current_user

router = APIRouter(prefix="/api/v1", tags=["analysis"])

DEFAULT_REQUIRED_PHRASES = [
    "здравствуйте",
    "чем могу помочь",
    "до свидания",
]


def _parse_required_phrases(raw_value: str | None, fallback: list[str]) -> list[str]:
    if raw_value is None or raw_value.strip() == "":
        return fallback

    try:
        parsed = json.loads(raw_value)
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid required_phrases JSON: {exc.msg}") from exc

    raise HTTPException(status_code=400, detail="required_phrases must be a JSON array")


def _validate_extension(file_name: str, allowed_extensions: set[str]) -> None:
    suffix = Path(file_name).suffix.lower().lstrip(".")
    if suffix not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: .{suffix}. Allowed: {', '.join(sorted(allowed_extensions))}",
        )


@router.post(
    "/analysis/upload-and-analyze",
    response_model=TaskCreatedOut,
    responses={400: {"model": ErrorOut}},
)
async def upload_and_analyze(
    request: Request,
    file: UploadFile = File(...),
    required_phrases: str | None = None,
    user: UserContext = Depends(get_current_user),
) -> TaskCreatedOut:
    ctx = request.app.state.ctx
    _ = user
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing file name")

    _validate_extension(file.filename, ctx.settings.allowed_extensions_set)
    task = ctx.tasks.create_task(file.filename)

    upload_path = ctx.storage.upload_path(task.task_id, file.filename)
    content = await file.read()
    max_size = ctx.settings.max_upload_mb * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(status_code=400, detail=f"File too large, max size is {ctx.settings.max_upload_mb} MB")

    upload_path.write_bytes(content)

    script_phrases = _parse_required_phrases(required_phrases, DEFAULT_REQUIRED_PHRASES)

    def _worker(task_id: str) -> None:
        try:
            payload = ctx.pipeline.process(
                task_id=task_id,
                file_name=file.filename or "uploaded",
                audio_path=str(upload_path),
                required_phrases=script_phrases,
            )
            result_path = ctx.storage.result_path(task_id)
            ctx.storage.write_json(result_path, payload)
            ctx.tasks.set_result_path(task_id, str(result_path))
            ctx.tasks.set_status(task_id, TaskStatus.done)
        except Exception as exc:
            ctx.storage.write_error(task_id, str(exc))
            ctx.tasks.set_status(task_id, TaskStatus.failed, error=str(exc))

    ctx.tasks.submit(task.task_id, _worker)
    return TaskCreatedOut(task_id=task.task_id, status=task.status)


@router.get("/tasks/{task_id}", response_model=TaskOut, responses={404: {"model": ErrorOut}})
def get_task(task_id: str, request: Request, user: UserContext = Depends(get_current_user)) -> TaskOut:
    ctx = request.app.state.ctx
    _ = user
    task = ctx.tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskOut(**task.as_dict())


@router.get("/tasks", response_model=TasksListOut)
def list_tasks(request: Request, user: UserContext = Depends(get_current_user)) -> TasksListOut:
    ctx = request.app.state.ctx
    _ = user
    return TasksListOut(items=[TaskOut(**task.as_dict()) for task in ctx.tasks.list()])


@router.get(
    "/results/{task_id}",
    response_model=AnalysisResultOut,
    responses={404: {"model": ErrorOut}, 409: {"model": ErrorOut}},
)
def get_result(
    task_id: str,
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> AnalysisResultOut:
    ctx = request.app.state.ctx
    _ = user
    task = ctx.tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status == TaskStatus.failed:
        raise HTTPException(status_code=409, detail=f"Task failed: {task.error}")

    if task.status != TaskStatus.done or not task.result_path:
        raise HTTPException(status_code=409, detail="Task is not completed yet")

    payload = ctx.storage.read_json(Path(task.result_path))
    return AnalysisResultOut(**payload)


@router.get("/health")
def health(request: Request) -> JSONResponse:
    ctx = request.app.state.ctx
    pipeline_runtime = ctx.pipeline.runtime_info()
    payload = {
        "status": "ok",
        "workers": ctx.settings.max_workers,
        "asr_model": pipeline_runtime["asr_model"],
        "external_asr_enabled": pipeline_runtime["external_asr_enabled"],
        "external_asr_status": pipeline_runtime["external_asr_status"],
        "external_asr_module_path": pipeline_runtime["external_asr_module_path"],
        "external_asr_error": pipeline_runtime["external_asr_error"],
    }
    return JSONResponse(payload)
