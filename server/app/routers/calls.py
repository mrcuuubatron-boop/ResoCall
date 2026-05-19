from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import FileResponse

from app.schemas import CallCreateRequest, ClientCreateRequest, EmployeeCreateRequest
from app.schemas import UserContext
from app.security import get_current_user, get_current_user_any

router = APIRouter(prefix="/api", tags=["calls"])


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


@router.get("/employees")
def list_employees(request: Request):
    return request.app.state.ctx.calls.list_employees()


@router.post("/employees")
def create_employee(request: Request, payload: EmployeeCreateRequest, user=Depends(get_current_user_any)):
    if user.role not in {"admin", "engineer"}:
        raise HTTPException(status_code=403, detail="forbidden")
    ctx = request.app.state.ctx
    try:
        employee = ctx.calls.create_employee(payload.name, payload.position, payload.hire_date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"created": True, "employee": employee}


@router.delete("/employees/{employee_id}")
def delete_employee(request: Request, employee_id: str, user=Depends(get_current_user_any)):
    if user.role not in {"admin", "engineer"}:
        raise HTTPException(status_code=403, detail="forbidden")
    ctx = request.app.state.ctx
    if not ctx.calls.delete_employee(employee_id):
        raise HTTPException(status_code=404, detail="employee not found")
    return {"deleted": True, "id": employee_id}


@router.get("/clients")
def list_clients(request: Request):
    return request.app.state.ctx.calls.list_clients()


@router.post("/clients")
def create_client(request: Request, payload: ClientCreateRequest, user=Depends(get_current_user_any)):
    if user.role not in {"admin", "engineer"}:
        raise HTTPException(status_code=403, detail="forbidden")
    ctx = request.app.state.ctx
    try:
        client = ctx.calls.create_client(payload.name, payload.phone)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"created": True, "client": client}


@router.delete("/clients/{client_id}")
def delete_client(request: Request, client_id: str, user=Depends(get_current_user_any)):
    if user.role not in {"admin", "engineer"}:
        raise HTTPException(status_code=403, detail="forbidden")
    ctx = request.app.state.ctx
    if not ctx.calls.delete_client(client_id):
        raise HTTPException(status_code=404, detail="client not found")
    return {"deleted": True, "id": client_id}


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


@router.post("/calls")
def create_call(request: Request, payload: CallCreateRequest, user=Depends(get_current_user_any)):
    if user.role not in {"admin", "engineer"}:
        raise HTTPException(status_code=403, detail="forbidden")
    ctx = request.app.state.ctx
    try:
        created = ctx.calls.create_call(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"created": True, "call": created}


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


@router.post("/calls/{call_id}/process")
def process_call(request: Request, call_id: str, user: UserContext = Depends(get_current_user)):
    """Trigger processing of a call's audio via the ML pipeline (background job).

    The job writes the analysis result to `storage.result_path(call_id)`, updates
    the call's `transcript.json` and `meta.json` in the calls state directory.
    """
    ctx = request.app.state.ctx
    call = ctx.calls.get_call(call_id, include_deleted=False)
    if call is None:
        raise HTTPException(status_code=404, detail="Call not found")

    # Resolve audio file path
    audio_url = str(call.get("audioUrl") or "")
    file_name = Path(audio_url).name if audio_url else f"{call_id}.mp3"
    audio_path = str(ctx.calls._audio_path(file_name))
    required_phrases = ctx.storage.read_default_script()

    def _worker(cid: str) -> None:
        try:
            payload = ctx.get_pipeline().process(
                task_id=cid, file_name=file_name, audio_path=audio_path, required_phrases=required_phrases
            )

            # write analysis result to storage/results
            result_path = ctx.storage.result_path(cid)
            ctx.storage.write_json(result_path, payload)

            # update call directory: transcript and meta
            call_dir = ctx.calls._call_dir(cid, deleted=False)
            # build simple transcript entries from segments
            transcript_entries = []
            for seg in payload.get("segments", []):
                start = int(seg.get("start", 0))
                timestamp = f"{start//60:02d}:{start%60:02d}"
                transcript_entries.append({
                    "speaker": seg.get("speaker", "unknown"),
                    "text": seg.get("text", ""),
                    "timestamp": timestamp,
                })

            # update meta.json
            meta_path = call_dir / "meta.json"
            meta = {}
            if meta_path.exists():
                with meta_path.open("r", encoding="utf-8") as fp:
                    meta = json.load(fp)

            meta["isProcessed"] = True
            meta["sentiment"] = payload.get("summary", {}).get("overall_sentiment")
            meta["scriptCompliance"] = int(payload.get("script_check", {}).get("compliance_pct", 0))
            meta["category"] = payload.get("summary", {}).get("category")

            ctx.calls._write_json(meta_path, meta)
            ctx.calls._write_json(call_dir / "transcript.json", transcript_entries)
        except Exception as exc:
            ctx.storage.write_error(call_id, str(exc))

    ctx.tasks.submit(call_id, _worker)
    return {"status": "processing", "id": call_id}
