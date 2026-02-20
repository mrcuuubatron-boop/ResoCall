"""Анализ звонков: тональность, ключевые слова, метрики качества."""
from typing import List, Tuple

from core.models import AnalysisResult, CallRecord, Sentiment


# Простые словари для демонстрации без внешних зависимостей
_POSITIVE_WORDS = {"спасибо", "отлично", "хорошо", "доволен", "помогли", "решили", "супер"}
_NEGATIVE_WORDS = {"плохо", "ужасно", "недоволен", "проблема", "жалоба", "не работает", "отказали"}


def _detect_sentiment(text: str) -> Tuple[Sentiment, float]:
    """Определить тональность текста по ключевым словам."""
    lower = text.lower()
    pos = sum(1 for w in _POSITIVE_WORDS if w in lower)
    neg = sum(1 for w in _NEGATIVE_WORDS if w in lower)
    total = pos + neg or 1
    score = (pos - neg) / total
    if score > 0.1:
        return Sentiment.POSITIVE, round(score, 2)
    if score < -0.1:
        return Sentiment.NEGATIVE, round(score, 2)
    return Sentiment.NEUTRAL, round(score, 2)


def _extract_keywords(text: str, top_n: int = 10) -> List[str]:
    """Извлечь наиболее частые значимые слова из текста."""
    stop_words = {"и", "в", "на", "с", "по", "для", "не", "что", "как", "это", "я", "вы", "мы"}
    words = [w.strip(".,!?;:\"'()").lower() for w in text.split()]
    freq: dict[str, int] = {}
    for w in words:
        if w and w not in stop_words and len(w) > 2:
            freq[w] = freq.get(w, 0) + 1
    return sorted(freq, key=lambda k: freq[k], reverse=True)[:top_n]


def _quality_score(sentiment_score: float, silence_ratio: float, talk_ratio_agent: float) -> float:
    """Рассчитать итоговую оценку качества звонка (0–100)."""
    sentiment_component = (sentiment_score + 1) / 2 * 40   # 0–40
    silence_component = (1 - silence_ratio) * 30           # 0–30
    balance_component = (1 - abs(talk_ratio_agent - 0.5) * 2) * 30  # 0–30
    return round(sentiment_component + silence_component + balance_component, 1)


def analyze_call(
    call: CallRecord,
    silence_ratio: float = 0.0,
    talk_ratio_agent: float = 0.5,
) -> AnalysisResult:
    """
    Проанализировать звонок и вернуть AnalysisResult.

    Args:
        call: запись звонка с заполненным полем `transcript`.
        silence_ratio: доля тишины (из AudioMetrics).
        talk_ratio_agent: доля речи агента (из AudioMetrics).
    """
    text = call.transcript or ""
    sentiment, score = _detect_sentiment(text)
    keywords = _extract_keywords(text)
    quality = _quality_score(score, silence_ratio, talk_ratio_agent)

    return AnalysisResult(
        call_id=call.id,
        sentiment=sentiment,
        sentiment_score=score,
        keywords=keywords,
        talk_ratio_agent=talk_ratio_agent,
        silence_ratio=silence_ratio,
        quality_score=quality,
        summary=text[:200] if text else "",
    )
