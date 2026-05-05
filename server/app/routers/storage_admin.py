from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse, FileResponse
from app.security import get_current_user_any
from app.schemas import UserContext

router = APIRouter(prefix="/api/v1", tags=["storage"])


@router.get("/storage/files")
def list_files(request: Request, which: str = "uploads", prefix: str | None = None, limit: int = 200, current_user: UserContext = Depends(get_current_user_any)) -> JSONResponse:
    ctx = getattr(request.app.state, "ctx", None)
    if ctx is None:
        raise HTTPException(status_code=500, detail="app context missing")
    if current_user.role not in {"admin", "engineer"}:
        raise HTTPException(status_code=403, detail="forbidden")
    settings = ctx.settings
    if which == "uploads":
        base = settings.upload_dir
    elif which == "results":
        base = settings.result_dir
    elif which == "logs":
        base = settings.log_dir
    else:
        raise HTTPException(status_code=400, detail="unknown storage area")

    files: list[dict[str, Any]] = []
    if not base.exists():
        return JSONResponse({"files": []})

    for p in sorted(base.iterdir(), key=lambda x: x.name)[:limit]:
        if not p.is_file():
            continue
        stat = p.stat()
        name = p.name
        if prefix and not name.startswith(prefix):
            continue
        files.append({"name": name, "size": stat.st_size, "mtime": stat.st_mtime})

    return JSONResponse({"files": files})


@router.get("/storage/download")
def download(request: Request, which: str, name: str, current_user: UserContext = Depends(get_current_user_any)):
    ctx = getattr(request.app.state, "ctx", None)
    if ctx is None:
        raise HTTPException(status_code=500, detail="app context missing")
    # only admin/engineer may download via admin API
    if current_user.role not in {"admin", "engineer"}:
        raise HTTPException(status_code=403, detail="forbidden")
    settings = ctx.settings
    if which == "uploads":
        base = settings.upload_dir
    elif which == "results":
        base = settings.result_dir
    elif which == "logs":
        base = settings.log_dir
    else:
        raise HTTPException(status_code=400, detail="unknown storage area")

    # prevent path traversal
    path = (base / Path(name).name).resolve()
    try:
        base_res = base.resolve()
    except Exception:
        raise HTTPException(status_code=500, detail="invalid storage base")
    if not str(path).startswith(str(base_res)) or not path.exists():
        raise HTTPException(status_code=404, detail="file not found")

    return FileResponse(path)


@router.post("/storage/upload")
async def upload(request: Request, file: UploadFile = File(...), area: str = Form("uploads"), current_user: UserContext = Depends(get_current_user_any)) -> JSONResponse:
    ctx = getattr(request.app.state, "ctx", None)
    if ctx is None:
        raise HTTPException(status_code=500, detail="app context missing")
    if current_user.role not in {"admin", "engineer"}:
        raise HTTPException(status_code=403, detail="forbidden")
    settings = ctx.settings

    if area == "uploads":
        base = settings.upload_dir
    elif area == "results":
        base = settings.result_dir
    else:
        raise HTTPException(status_code=400, detail="unknown area")

    safe_name = Path(file.filename or "upload.bin").name
    allowed = settings.allowed_extensions_set
    suffix = Path(safe_name).suffix.lower().lstrip('.')
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if allowed and suffix not in allowed:
        raise HTTPException(status_code=400, detail=f"disallowed extension: {suffix}")

    dest = base / safe_name
    dest.parent.mkdir(parents=True, exist_ok=True)

    # stream write and enforce size
    size = 0
    try:
        with dest.open("wb") as out:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                if size > max_bytes:
                    out.close()
                    dest.unlink(missing_ok=True)
                    raise HTTPException(status_code=400, detail="file exceeds max upload size")
                out.write(chunk)
    finally:
        await file.close()

    # record metadata in DB (best-effort) — prefer authenticated user
    uploader = getattr(current_user, "login", None)
    if not uploader:
        try:
            auth = request.headers.get("authorization")
            if auth and auth.lower().startswith("basic "):
                import base64

                token = auth.split(None, 1)[1]
                decoded = base64.b64decode(token).decode(errors="ignore")
                parts = decoded.split(":", 1)
                if parts:
                    uploader = parts[0]
        except Exception:
            uploader = None

    try:
        ctx.db.record_upload(dest.name, area, size, uploader)
    except Exception:
        pass

    return JSONResponse({"name": dest.name, "size": size, "path": str(dest), "uploader": uploader})


@router.get("/admin/users")
def list_users(request: Request, current_user: UserContext = Depends(get_current_user_any)) -> JSONResponse:
    ctx = getattr(request.app.state, "ctx", None)
    if ctx is None:
        raise HTTPException(status_code=500, detail="app context missing")
    if current_user.role not in {"admin", "engineer"}:
        raise HTTPException(status_code=403, detail="forbidden")
    users = []
    try:
        users = ctx.db.list_users()
    except Exception:
        users = []
    return JSONResponse({"users": users})


@router.get("/storage/uploads")
def list_uploads(
    request: Request,
    area: str | None = None,
    uploader: str | None = None,
    include_deleted: bool = False,
    limit: int = 100,
    offset: int = 0,
    current_user: UserContext = Depends(get_current_user_any),
) -> JSONResponse:
    ctx = getattr(request.app.state, "ctx", None)
    if ctx is None:
        raise HTTPException(status_code=500, detail="app context missing")
    if current_user.role not in {"admin", "engineer"}:
        raise HTTPException(status_code=403, detail="forbidden")
    try:
        rows = ctx.db.list_uploads(
            area=area,
            limit=limit,
            offset=offset,
            include_deleted=include_deleted,
            uploader=uploader,
        )
    except Exception:
        rows = []
    return JSONResponse({"uploads": rows})


@router.delete("/storage/file")
def delete_file(request: Request, which: str, name: str, current_user: UserContext = Depends(get_current_user_any)) -> JSONResponse:
    ctx = getattr(request.app.state, "ctx", None)
    if ctx is None:
        raise HTTPException(status_code=500, detail="app context missing")
    if current_user.role not in {"admin", "engineer"}:
        raise HTTPException(status_code=403, detail="forbidden")

    settings = ctx.settings
    if which == "uploads":
        base = settings.upload_dir
    elif which == "results":
        base = settings.result_dir
    elif which == "logs":
        base = settings.log_dir
    else:
        raise HTTPException(status_code=400, detail="unknown storage area")

    path = (base / Path(name).name).resolve()
    try:
        base_res = base.resolve()
    except Exception:
        raise HTTPException(status_code=500, detail="invalid storage base")
    if not str(path).startswith(str(base_res)):
        raise HTTPException(status_code=400, detail="invalid path")

    existed = path.exists()
    if existed:
        path.unlink(missing_ok=True)

    # mark metadata as deleted too (best-effort)
    try:
        affected = ctx.db.soft_delete_upload_by_name(Path(name).name, which, current_user.login)
    except Exception:
        affected = 0
    return JSONResponse({"deleted": existed, "metadata_soft_deleted": affected})


@router.post("/storage/uploads/{upload_id}/soft-delete")
def soft_delete_upload(upload_id: int, request: Request, purge_file: bool = False, current_user: UserContext = Depends(get_current_user_any)) -> JSONResponse:
    ctx = getattr(request.app.state, "ctx", None)
    if ctx is None:
        raise HTTPException(status_code=500, detail="app context missing")
    if current_user.role not in {"admin", "engineer"}:
        raise HTTPException(status_code=403, detail="forbidden")

    ok = ctx.db.soft_delete_upload(upload_id, current_user.login)
    if not ok:
        raise HTTPException(status_code=404, detail="upload metadata not found or already deleted")

    purged = False
    if purge_file:
        meta = ctx.db.get_upload(upload_id)
        if meta:
            area = str(meta.get("area") or "")
            name = str(meta.get("name") or "")
            if area == "uploads":
                base = ctx.settings.upload_dir
            elif area == "results":
                base = ctx.settings.result_dir
            elif area == "logs":
                base = ctx.settings.log_dir
            else:
                base = None

            if base is not None:
                path = (base / Path(name).name).resolve()
                try:
                    base_res = base.resolve()
                    if str(path).startswith(str(base_res)) and path.exists():
                        path.unlink(missing_ok=True)
                        purged = True
                except Exception:
                    purged = False

    return JSONResponse({"soft_deleted": True, "file_purged": purged})
