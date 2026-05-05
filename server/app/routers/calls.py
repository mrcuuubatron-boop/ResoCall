from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import FileResponse

from app.security import get_current_user_any

router = APIRouter(prefix="/api", tags=["calls"])


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


@router.get("/employees")
def list_employees(request: Request):
    return request.app.state.ctx.calls.list_employees()


@router.get("/clients")
def list_clients(request: Request):
    return request.app.state.ctx.calls.list_clients()


@router.get("/calls")
def list_calls(
    request: Request,
    from_: str | None = Query(default=None, alias="from"),
    to: str | None = None,
    include_deleted: bool = False,
):
    return request.app.state.ctx.calls.list_calls(
        from_dt=_parse_iso(from_),
        to_dt=_parse_iso(to),
        include_deleted=include_deleted,
    )


@router.get("/calls/deleted")
def list_deleted_calls(request: Request):
    return request.app.state.ctx.calls.list_deleted_calls()


@router.get("/calls/unprocessed")
def list_unprocessed_calls(request: Request):
    return request.app.state.ctx.calls.list_unprocessed_calls()


@router.get("/calls/{call_id}")
def get_call(request: Request, call_id: str):
    call = request.app.state.ctx.calls.get_call(call_id, include_deleted=True)
    if call is None:
        raise HTTPException(status_code=404, detail="Call not found")
    return call


@router.get("/calls/audio/{file_name}")
def get_call_audio(request: Request, file_name: str):
    file_path = request.app.state.ctx.settings.data_dir / "state" / "calls" / "audio" / Path(file_name).name
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(path=file_path, media_type="audio/mpeg", filename=file_path.name)


@router.delete("/calls/{call_id}")
def delete_call(request: Request, call_id: str, user=Depends(get_current_user_any)):
    if not request.app.state.ctx.calls.soft_delete_call(call_id, deleted_by=user.login):
        raise HTTPException(status_code=404, detail="Call not found or already deleted")
    return {"status": "deleted", "id": call_id}


@router.post("/calls/{call_id}/restore")
def restore_call(request: Request, call_id: str, user=Depends(get_current_user_any)):
    if not request.app.state.ctx.calls.restore_call(call_id):
        raise HTTPException(status_code=404, detail="Call not found or not deleted")
    return {"status": "restored", "id": call_id, "restoredBy": user.login}
