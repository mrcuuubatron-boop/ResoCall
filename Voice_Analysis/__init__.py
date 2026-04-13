"""
Voice Emotion Analyzer Package
Анализ психологического состояния по голосу

Использование:
    from voice_emotion_analyzer import VoiceEmotionAnalyzer
    
    analyzer = VoiceEmotionAnalyzer()
    result = analyzer.analyze('audio.wav')
"""

from .voice_emotion_analyzer import (
    VoiceEmotionAnalyzer,
    VoiceAnalysisResult,
    PsychologicalState,
)

from .resocall_voice_analyzer import (
    ResoCallVoiceAnalyzer,
    AudioPipelineWithEmotion,
)

__version__ = "1.0.0"
__author__ = "ResoCall Team"

__all__ = [
    'VoiceEmotionAnalyzer',
    'VoiceAnalysisResult',
    'PsychologicalState',
    'ResoCallVoiceAnalyzer',
    'AudioPipelineWithEmotion',
]
