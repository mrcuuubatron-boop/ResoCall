"""Pydantic-схемы для API запросов и ответов."""
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class CallStatusEnum(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class SentimentEnum(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


# ── Agents ──────────────────────────────────────────────────────────────────

class AgentCreate(BaseModel):
    name: str = Field(..., min_length=1)
    department: str = ""
    email: str = ""


class AgentResponse(AgentCreate):
    id: str


# ── Calls ────────────────────────────────────────────────────────────────────

class CallCreate(BaseModel):
    agent_id: str
    customer_phone: str
    started_at: datetime = Field(default_factory=datetime.utcnow)


class CallResponse(BaseModel):
    id: str
    agent_id: str
    customer_phone: str
    started_at: datetime
    duration_seconds: int
    status: CallStatusEnum
    transcript: Optional[str] = None


# ── Analysis ─────────────────────────────────────────────────────────────────

class AnalysisResponse(BaseModel):
    call_id: str
    sentiment: SentimentEnum
    sentiment_score: float
    keywords: List[str]
    talk_ratio_agent: float
    silence_ratio: float
    quality_score: float
    summary: str
    analyzed_at: datetime
