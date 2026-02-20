"""Обработка аудио: транскрибация и базовые метрики."""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class AudioMetrics:
    """Базовые метрики аудиофайла."""
    duration_seconds: float
    sample_rate: int
    channels: int
    silence_ratio: float      # доля тишины (0–1)
    talk_ratio_agent: float   # доля речи агента (0–1)


def get_audio_metrics(audio_path: str) -> AudioMetrics:
    """
    Вернуть метрики аудиофайла.

    В реальной реализации здесь используется librosa / pyAudioAnalysis.
    Сейчас возвращает заглушку для демонстрации структуры.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Аудиофайл не найден: {audio_path}")

    # TODO: заменить на реальную обработку через librosa
    return AudioMetrics(
        duration_seconds=0.0,
        sample_rate=16000,
        channels=1,
        silence_ratio=0.0,
        talk_ratio_agent=0.5,
    )


def transcribe(audio_path: str, language: str = "ru") -> Optional[str]:
    """
    Транскрибировать аудиофайл в текст.

    В реальной реализации здесь используется Whisper / Vosk.
    Сейчас возвращает None (заглушка).
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Аудиофайл не найден: {audio_path}")

    # TODO: заменить на реальную транскрибацию (openai-whisper / vosk)
    return None
