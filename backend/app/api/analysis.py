"""API-роутер: анализ звонков."""
from typing import List

from fastapi import APIRouter, HTTPException

from backend.app.models import AnalysisResponse
from backend.app.services import get_analysis, list_analyses, run_analysis

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.post("/{call_id}", response_model=AnalysisResponse, status_code=201)
def analyze(call_id: str):
    """Запустить анализ звонка."""
    result = run_analysis(call_id)
    if not result:
        raise HTTPException(status_code=404, detail="Звонок не найден")
    return AnalysisResponse(
        call_id=result.call_id,
        sentiment=result.sentiment,
        sentiment_score=result.sentiment_score,
        keywords=result.keywords,
        talk_ratio_agent=result.talk_ratio_agent,
        silence_ratio=result.silence_ratio,
        quality_score=result.quality_score,
        summary=result.summary,
        analyzed_at=result.analyzed_at,
    )


@router.get("/{call_id}", response_model=AnalysisResponse)
def get_analysis_result(call_id: str):
    """Получить результат анализа звонка."""
    result = get_analysis(call_id)
    if not result:
        raise HTTPException(status_code=404, detail="Анализ не найден")
    return AnalysisResponse(
        call_id=result.call_id,
        sentiment=result.sentiment,
        sentiment_score=result.sentiment_score,
        keywords=result.keywords,
        talk_ratio_agent=result.talk_ratio_agent,
        silence_ratio=result.silence_ratio,
        quality_score=result.quality_score,
        summary=result.summary,
        analyzed_at=result.analyzed_at,
    )


@router.get("/", response_model=List[AnalysisResponse])
def get_all_analyses():
    """Список всех результатов анализа."""
    return [
        AnalysisResponse(
            call_id=r.call_id,
            sentiment=r.sentiment,
            sentiment_score=r.sentiment_score,
            keywords=r.keywords,
            talk_ratio_agent=r.talk_ratio_agent,
            silence_ratio=r.silence_ratio,
            quality_score=r.quality_score,
            summary=r.summary,
            analyzed_at=r.analyzed_at,
        )
        for r in list_analyses()
    ]
