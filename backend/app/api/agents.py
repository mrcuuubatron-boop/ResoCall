"""API-роутер: агенты."""
from typing import List

from fastapi import APIRouter, HTTPException

from backend.app.models import AgentCreate, AgentResponse
from backend.app.services import create_agent, get_agent, list_agents

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.get("/", response_model=List[AgentResponse])
def get_agents():
    """Список всех агентов."""
    return [AgentResponse(id=a.id, name=a.name, department=a.department, email=a.email)
            for a in list_agents()]


@router.post("/", response_model=AgentResponse, status_code=201)
def add_agent(payload: AgentCreate):
    """Создать агента."""
    agent = create_agent(name=payload.name, department=payload.department, email=payload.email)
    return AgentResponse(id=agent.id, name=agent.name, department=agent.department, email=agent.email)


@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent_by_id(agent_id: str):
    """Получить агента по ID."""
    agent = get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Агент не найден")
    return AgentResponse(id=agent.id, name=agent.name, department=agent.department, email=agent.email)
