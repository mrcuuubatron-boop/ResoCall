from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Callable
from uuid import uuid4

from app.schemas import TaskStatus


@dataclass
class TaskRecord:
    task_id: str
    file_name: str
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    result_path: str | None = None
    error: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "file_name": self.file_name,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "error": self.error,
        }


class TaskManager:
    def __init__(self, max_workers: int) -> None:
        self._pool = ThreadPoolExecutor(max_workers=max_workers)
        self._lock = Lock()
        self._tasks: dict[str, TaskRecord] = {}

    def create_task(self, file_name: str) -> TaskRecord:
        with self._lock:
            now = datetime.now(timezone.utc)
            task = TaskRecord(
                task_id=str(uuid4()),
                file_name=file_name,
                status=TaskStatus.queued,
                created_at=now,
                updated_at=now,
            )
            self._tasks[task.task_id] = task
            return task

    def submit(self, task_id: str, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Future:
        self.set_status(task_id, TaskStatus.processing)
        return self._pool.submit(fn, task_id, *args, **kwargs)

    def set_status(self, task_id: str, status: TaskStatus, error: str | None = None) -> None:
        with self._lock:
            task = self._tasks[task_id]
            task.status = status
            task.updated_at = datetime.now(timezone.utc)
            task.error = error

    def set_result_path(self, task_id: str, result_path: str) -> None:
        with self._lock:
            task = self._tasks[task_id]
            task.result_path = result_path
            task.updated_at = datetime.now(timezone.utc)

    def get(self, task_id: str) -> TaskRecord | None:
        with self._lock:
            return self._tasks.get(task_id)

    def list(self) -> list[TaskRecord]:
        with self._lock:
            return sorted(self._tasks.values(), key=lambda t: t.created_at, reverse=True)
