"""API-роутер: звонки."""
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.models import CallCreate, CallResponse
from backend.app.services import create_call, get_call, list_calls, update_transcript

router = APIRouter(prefix="/calls", tags=["Calls"])


@router.get("/", response_model=List[CallResponse])
def get_calls():
    """Список всех звонков."""
    return [
        CallResponse(
            id=c.id,
            agent_id=c.agent_id,
            customer_phone=c.customer_phone,
            started_at=c.started_at,
            duration_seconds=c.duration_seconds,
            status=c.status,
            transcript=c.transcript,
        )
        for c in list_calls()
    ]


@router.post("/", response_model=CallResponse, status_code=201)
def add_call(payload: CallCreate):
    """Зарегистрировать новый звонок."""
    call = create_call(
        agent_id=payload.agent_id,
        customer_phone=payload.customer_phone,
        started_at=payload.started_at,
    )
    return CallResponse(
        id=call.id,
        agent_id=call.agent_id,
        customer_phone=call.customer_phone,
        started_at=call.started_at,
        duration_seconds=call.duration_seconds,
        status=call.status,
        transcript=call.transcript,
    )


@router.get("/{call_id}", response_model=CallResponse)
def get_call_by_id(call_id: str):
    """Получить звонок по ID."""
    call = get_call(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Звонок не найден")
    return CallResponse(
        id=call.id,
        agent_id=call.agent_id,
        customer_phone=call.customer_phone,
        started_at=call.started_at,
        duration_seconds=call.duration_seconds,
        status=call.status,
        transcript=call.transcript,
    )


class TranscriptUpdate(BaseModel):
    transcript: str
    duration_seconds: int = 0


@router.patch("/{call_id}/transcript", response_model=CallResponse)
def set_transcript(call_id: str, body: TranscriptUpdate):
    """Сохранить транскрипт звонка."""
    call = update_transcript(call_id, body.transcript, body.duration_seconds)
    if not call:
        raise HTTPException(status_code=404, detail="Звонок не найден")
    return CallResponse(
        id=call.id,
        agent_id=call.agent_id,
        customer_phone=call.customer_phone,
        started_at=call.started_at,
        duration_seconds=call.duration_seconds,
        status=call.status,
        transcript=call.transcript,
    )
