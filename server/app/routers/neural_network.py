from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Request

router = APIRouter(prefix="/api/neural-network", tags=["neural-network"])


def _state_dir(request: Request) -> Path:
    path = request.app.state.ctx.settings.data_dir / "state" / "neural_network"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _state_paths(request: Request) -> dict[str, Path]:
    root = _state_dir(request)
    return {
        "status": root / "status.json",
        "logs": root / "logs.json",
        "history": root / "history.json",
        "errors": root / "errors_stats.json",
    }


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as fp:
        return json.load(fp)


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fp:
        json.dump(payload, fp, ensure_ascii=False, indent=2)


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_seed(request: Request) -> None:
    paths = _state_paths(request)
    if not paths["status"].exists():
        _write_json(paths["status"], {"isRunning": True, "isPaused": False})
    if not paths["logs"].exists():
        _write_json(
            paths["logs"],
            [
                {"id": "log-1", "timestamp": _iso_now(), "level": "success", "message": "Нейросеть инициализирована"},
                {"id": "log-2", "timestamp": _iso_now(), "level": "info", "message": "Демо-режим активирован"},
            ],
        )
    if not paths["history"].exists():
        _write_json(
            paths["history"],
            [
                {
                    "id": "1",
                    "startTime": "2026-05-04 09:00",
                    "endTime": "2026-05-04 09:42",
                    "status": "completed",
                    "processed": 38,
                    "errors": 2,
                    "errorList": [
                        {
                            "id": "run1-err1",
                            "audioPath": "/api/calls/audio/call-5.mp3",
                            "errorType": "LowAudioQuality",
                            "message": "Низкое качество аудио",
                        },
                        {
                            "id": "run1-err2",
                            "audioPath": "/api/calls/audio/call-3.mp3",
                            "errorType": "ASRTimeout",
                            "message": "Timeout обработки модели",
                        },
                    ],
                }
            ],
        )
    if not paths["errors"].exists():
        _write_json(
            paths["errors"],
            [
                {
                    "type": "LowAudioQuality",
                    "count": 1,
                    "percentage": 50,
                    "audioFiles": [
                        {"id": "e1", "path": "/api/calls/audio/call-5.mp3", "timestamp": "2026-05-04 09:18"}
                    ],
                },
                {
                    "type": "ASRTimeout",
                    "count": 1,
                    "percentage": 50,
                    "audioFiles": [
                        {"id": "e2", "path": "/api/calls/audio/call-3.mp3", "timestamp": "2026-05-04 09:23"}
                    ],
                },
            ],
        )


@router.get("/status")
def get_status(request: Request):
    _ensure_seed(request)
    return _read_json(_state_paths(request)["status"], {"isRunning": False, "isPaused": False})


@router.get("/logs")
def get_logs(request: Request):
    _ensure_seed(request)
    return _read_json(_state_paths(request)["logs"], [])


@router.get("/history")
def get_history(request: Request):
    _ensure_seed(request)
    return _read_json(_state_paths(request)["history"], [])


@router.get("/errors-stats")
def get_errors_stats(request: Request):
    _ensure_seed(request)
    return _read_json(_state_paths(request)["errors"], [])


@router.post("/{command}")
def command(request: Request, command: str):
    _ensure_seed(request)
    if command not in {"start", "pause", "stop", "restart"}:
        raise HTTPException(status_code=404, detail="Unknown command")

    paths = _state_paths(request)
    status = _read_json(paths["status"], {"isRunning": False, "isPaused": False})
    if command == "start":
        status = {"isRunning": True, "isPaused": False}
        message = "Команда START принята"
    elif command == "pause":
        status = {"isRunning": bool(status.get("isRunning", False)), "isPaused": True}
        message = "Команда PAUSE принята"
    elif command == "stop":
        status = {"isRunning": False, "isPaused": False}
        message = "Команда STOP принята"
    else:
        status = {"isRunning": True, "isPaused": False}
        message = "Команда RESTART принята"

    _write_json(paths["status"], status)
    logs = _read_json(paths["logs"], [])
    logs.insert(0, {"id": f"log-{int(datetime.now().timestamp())}", "timestamp": _iso_now(), "level": "info", "message": message})
    _write_json(paths["logs"], logs[:200])
    return {"ok": True, "command": command, "status": status}
