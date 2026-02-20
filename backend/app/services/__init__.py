"""In-memory хранилище и сервисный слой (замените на БД в production)."""
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from core.analysis import analyze_call
from core.models import Agent, AnalysisResult, CallRecord, CallStatus


_agents: Dict[str, Agent] = {}
_calls: Dict[str, CallRecord] = {}
_results: Dict[str, AnalysisResult] = {}


# ── Agents ───────────────────────────────────────────────────────────────────

def create_agent(name: str, department: str = "", email: str = "") -> Agent:
    agent = Agent(id=str(uuid.uuid4()), name=name, department=department, email=email)
    _agents[agent.id] = agent
    return agent


def get_agent(agent_id: str) -> Optional[Agent]:
    return _agents.get(agent_id)


def list_agents() -> List[Agent]:
    return list(_agents.values())


# ── Calls ────────────────────────────────────────────────────────────────────

def create_call(agent_id: str, customer_phone: str, started_at: Optional[datetime] = None) -> CallRecord:
    call = CallRecord(
        id=str(uuid.uuid4()),
        agent_id=agent_id,
        customer_phone=customer_phone,
        started_at=started_at or datetime.utcnow(),
    )
    _calls[call.id] = call
    return call


def get_call(call_id: str) -> Optional[CallRecord]:
    return _calls.get(call_id)


def list_calls() -> List[CallRecord]:
    return list(_calls.values())


def update_transcript(call_id: str, transcript: str, duration_seconds: int = 0) -> Optional[CallRecord]:
    call = _calls.get(call_id)
    if not call:
        return None
    call.transcript = transcript
    call.duration_seconds = duration_seconds
    call.status = CallStatus.COMPLETED
    return call


# ── Analysis ─────────────────────────────────────────────────────────────────

def run_analysis(call_id: str) -> Optional[AnalysisResult]:
    call = _calls.get(call_id)
    if not call:
        return None
    result = analyze_call(call)
    _results[call_id] = result
    return result


def get_analysis(call_id: str) -> Optional[AnalysisResult]:
    return _results.get(call_id)


def list_analyses() -> List[AnalysisResult]:
    return list(_results.values())
