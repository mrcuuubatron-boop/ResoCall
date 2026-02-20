"""Модели данных для ResoCall (используют dataclasses для минимальных зависимостей)."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class CallStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


@dataclass
class Agent:
    """Агент колл-центра."""
    id: str
    name: str
    department: str = ""
    email: str = ""


@dataclass
class CallRecord:
    """Запись звонка."""
    id: str
    agent_id: str
    customer_phone: str
    started_at: datetime
    duration_seconds: int = 0
    status: CallStatus = CallStatus.PENDING
    audio_path: Optional[str] = None
    transcript: Optional[str] = None


@dataclass
class AnalysisResult:
    """Результат анализа звонка."""
    call_id: str
    sentiment: Sentiment = Sentiment.NEUTRAL
    sentiment_score: float = 0.0          # от -1.0 (негатив) до 1.0 (позитив)
    keywords: List[str] = field(default_factory=list)
    talk_ratio_agent: float = 0.5         # доля речи агента (0–1)
    silence_ratio: float = 0.0            # доля тишины (0–1)
    quality_score: float = 0.0            # итоговая оценка качества (0–100)
    summary: str = ""
    analyzed_at: datetime = field(default_factory=datetime.utcnow)
