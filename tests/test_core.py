"""Tests for core analysis and models."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from datetime import datetime

from core.models import Agent, CallRecord, AnalysisResult, CallStatus, Sentiment
from core.analysis import analyze_call, _detect_sentiment, _extract_keywords, _quality_score


# ── Model tests ───────────────────────────────────────────────────────────────

def test_agent_creation():
    agent = Agent(id="a1", name="Иван", department="Продажи", email="ivan@test.ru")
    assert agent.id == "a1"
    assert agent.name == "Иван"
    assert agent.department == "Продажи"


def test_call_record_defaults():
    call = CallRecord(
        id="c1",
        agent_id="a1",
        customer_phone="+79001234567",
        started_at=datetime.utcnow(),
    )
    assert call.status == CallStatus.PENDING
    assert call.duration_seconds == 0
    assert call.transcript is None


def test_analysis_result_defaults():
    result = AnalysisResult(call_id="c1")
    assert result.sentiment == Sentiment.NEUTRAL
    assert result.sentiment_score == 0.0
    assert result.keywords == []
    assert 0 <= result.quality_score <= 100


# ── Sentiment detection tests ─────────────────────────────────────────────────

def test_detect_positive_sentiment():
    sentiment, score = _detect_sentiment("Спасибо, всё отлично, я доволен!")
    assert sentiment == Sentiment.POSITIVE
    assert score > 0


def test_detect_negative_sentiment():
    sentiment, score = _detect_sentiment("Всё плохо, жалоба, недоволен обслуживанием")
    assert sentiment == Sentiment.NEGATIVE
    assert score < 0


def test_detect_neutral_sentiment():
    sentiment, score = _detect_sentiment("Алло, соедините меня с отделом")
    assert sentiment == Sentiment.NEUTRAL


# ── Keyword extraction tests ──────────────────────────────────────────────────

def test_extract_keywords_returns_list():
    keywords = _extract_keywords("привет привет привет мир помощь помощь")
    assert isinstance(keywords, list)
    assert "привет" in keywords
    assert keywords[0] == "привет"  # most frequent first


def test_extract_keywords_excludes_stop_words():
    keywords = _extract_keywords("и в на с по для не что как это")
    assert all(k not in {"и", "в", "на", "с", "по", "для", "не", "что", "как", "это"} for k in keywords)


def test_extract_keywords_top_n():
    text = " ".join([f"word{i}" for i in range(20)])
    keywords = _extract_keywords(text, top_n=5)
    assert len(keywords) <= 5


# ── Quality score tests ───────────────────────────────────────────────────────

def test_quality_score_range():
    for sentiment_score in (-1.0, 0.0, 1.0):
        for silence in (0.0, 0.5, 1.0):
            for agent_ratio in (0.0, 0.5, 1.0):
                score = _quality_score(sentiment_score, silence, agent_ratio)
                assert 0 <= score <= 100, f"Out of range: {score}"


def test_quality_score_best_case():
    score = _quality_score(1.0, 0.0, 0.5)
    assert score == 100.0


def test_quality_score_worst_case():
    score = _quality_score(-1.0, 1.0, 0.0)
    assert score == 0.0


# ── analyze_call integration ──────────────────────────────────────────────────

def test_analyze_call_no_transcript():
    call = CallRecord(id="c1", agent_id="a1", customer_phone="+7900",
                      started_at=datetime.utcnow())
    result = analyze_call(call)
    assert result.call_id == "c1"
    assert result.sentiment == Sentiment.NEUTRAL


def test_analyze_call_with_positive_transcript():
    call = CallRecord(id="c2", agent_id="a1", customer_phone="+7900",
                      started_at=datetime.utcnow(),
                      transcript="Спасибо за помощь, всё отлично, решили проблему!")
    result = analyze_call(call)
    assert result.call_id == "c2"
    assert result.sentiment == Sentiment.POSITIVE
    assert result.quality_score > 50


def test_analyze_call_with_negative_transcript():
    call = CallRecord(id="c3", agent_id="a1", customer_phone="+7900",
                      started_at=datetime.utcnow(),
                      transcript="Всё плохо и ужасно, подаю жалобу, недоволен!")
    result = analyze_call(call)
    assert result.sentiment == Sentiment.NEGATIVE
