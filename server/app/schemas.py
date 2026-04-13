from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    queued = "queued"
    processing = "processing"
    done = "done"
    failed = "failed"


class SegmentOut(BaseModel):
    start: float
    end: float
    text: str
    speaker: str = "unknown"
    sentiment: str = "neutral"
    sentiment_score: float = 0.0
    mean_pitch: float | None = None
    pitch_std: float | None = None
    mean_rms: float | None = None


class ScriptCheckOut(BaseModel):
    required_phrases: list[str]
    found_phrases: list[str]
    missing_phrases: list[str]
    compliance_pct: float


class CallSummaryOut(BaseModel):
    category: str
    priority: int = Field(ge=1, le=5)
    overall_sentiment: str
    warnings: list[str] = Field(default_factory=list)


class AnalysisResultOut(BaseModel):
    task_id: str
    file_name: str
    total_duration: float
    segments: list[SegmentOut]
    script_check: ScriptCheckOut
    summary: CallSummaryOut


class TaskOut(BaseModel):
    task_id: str
    status: TaskStatus
    created_at: str
    updated_at: str
    file_name: str
    error: str | None = None


class TaskCreatedOut(BaseModel):
    task_id: str
    status: TaskStatus


class TasksListOut(BaseModel):
    items: list[TaskOut]


class LoginRequest(BaseModel):
    login: str
    password: str


class LoginResponse(BaseModel):
    ok: bool
    role: str
    token: str


class UserContext(BaseModel):
    login: str
    role: str


class ErrorOut(BaseModel):
    detail: str
    context: dict[str, Any] | None = None


class ModuleSettingsIn(BaseModel):
    settings: dict[str, Any] = Field(default_factory=dict)


class ModuleSettingsOut(BaseModel):
    module_key: str
    settings: dict[str, Any] = Field(default_factory=dict)
    updated_at: str | None = None
