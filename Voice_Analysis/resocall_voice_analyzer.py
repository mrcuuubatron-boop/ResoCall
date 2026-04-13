"""
Интеграция Voice Emotion Analyzer с ResoCall
Добавляет анализ психологического состояния к обработанным записям
"""

from .voice_emotion_analyzer import VoiceEmotionAnalyzer
from typing import Dict, Any, Optional
import os


class ResoCallVoiceAnalyzer:
    """
    Интеграция анализатора эмоций с pipelines ResoCall
    
    Использование:
    ```python
    from resocall_voice_analyzer import ResoCallVoiceAnalyzer
    
    analyzer = ResoCallVoiceAnalyzer()
    
    # Добавить результаты эмоций к существующему результату анализа
    analysis_result = {...}  # результат из audio_pipeline
    result_with_emotion = analyzer.add_emotion_analysis(audio_file, analysis_result)
    ```
    """
    
    def __init__(self):
        """Инициализируем анализатор"""
        self.emotion_analyzer = VoiceEmotionAnalyzer()
    
    def add_emotion_analysis(self, audio_path: str, analysis_result: Dict) -> Dict:
        """
        Добавляет анализ эмоций к существующему результату анализа.
        
        Args:
            audio_path: Путь к аудиофайлу
            analysis_result: Существующий результат анализа (из audio_pipeline)
            
        Returns:
            Расширенный результат с добавленными полями эмоций
        """
        
        try:
            emotion_result = self.emotion_analyzer.analyze(audio_path)
            
            # Добавляем результаты эмоций
            analysis_result['emotion'] = {
                'state': emotion_result.state.value,
                'confidence': round(emotion_result.confidence, 3),
                'intensity': round(emotion_result.intensity_score, 2),
                'stability': round(emotion_result.stability_score, 2),
                'tempo': round(emotion_result.tempo_score, 2),
            }
            
            # Добавляем детальные акустические параметры
            analysis_result['acoustics'] = {
                'pitch_hz': round(emotion_result.mean_pitch, 1),
                'pitch_variance': round(emotion_result.pitch_variance, 2),
                'energy_db': round(emotion_result.mean_energy, 1),
                'speech_rate': round(emotion_result.speech_rate, 2),
                'has_pauses': emotion_result.has_pauses,
                'pause_count': emotion_result.pause_count,
            }
            
        except Exception as e:
            # Если анализ эмоций не сработал, добавляем информацию об ошибке
            analysis_result['emotion'] = {
                'state': 'error',
                'error': str(e),
                'confidence': 0.0,
            }
            analysis_result['acoustics'] = None
        
        return analysis_result
    
    def get_state_label(self, state: str) -> str:
        """Возвращает метку для состояния"""
        state_labels = {
            'спокойно': 'CALM',
            'стресс': 'STRESSED',
            'радость': 'HAPPY',
            'грусть': 'SAD',
            'злость': 'ANGRY',
            'нейтральное': 'NEUTRAL'
        }
        return state_labels.get(state, 'UNKNOWN')
    
    def format_emotion_summary(self, analysis_result: Dict) -> str:
        """Возвращает форматированное резюме эмоций"""
        
        if 'emotion' not in analysis_result:
            return "Анализ эмоций не выполнен"
        
        emotion = analysis_result['emotion']
        
        if emotion.get('state') == 'error':
            return f"ERROR: Ошибка анализа: {emotion.get('error')}"
        
        state = emotion.get('state', 'неизвестно')
        confidence = emotion.get('confidence', 0) * 100
        intensity = emotion.get('intensity', 0)
        label = self.get_state_label(state)
        
        return f"{label} ({confidence:.0f}%) | Интенсивность: {intensity:.1f}/10"
    
    def get_health_recommendation(self, analysis_result: Dict) -> Optional[str]:
        """Возвращает рекомендацию на основе анализа эмоций"""
        
        if 'emotion' not in analysis_result:
            return None
        
        emotion = analysis_result['emotion']
        state = emotion.get('state', '')
        confidence = emotion.get('confidence', 0)
        
        # Только если уверенность высокая
        if confidence < 0.7:
            return None
        
        recommendations = {
            'злость': 'WARNING: Требуется деэскалация - рекомендуется передать более опытному оператору',
            'стресс': 'INFO: Оператор в состоянии стресса - рекомендуется предложить перерыв',
            'грусть': 'INFO: Клиент может быть расстроен - требуется эмоциональная поддержка',
            'радость': 'GOOD: Позитивное общение - хорошее время для предложений',
            'спокойно': 'OK: Благоприятная обстановка для переговоров',
        }
        
        return recommendations.get(state)


class AudioPipelineWithEmotion:
    """
    Расширенный pipeline аудиообработки с анализом эмоций
    
    Интегрируется с существующим audio_pipeline.py
    
    Использование:
    ```python
    from resocall_voice_analyzer import AudioPipelineWithEmotion
    
    # Вместо обычного AudioPipeline используем расширенный
    pipeline = AudioPipelineWithEmotion()
    result = await pipeline.process(audio_path)
    
    # Результат теперь содержит эмоциональный анализ
    print(result['emotion'])  # {'state': '...', 'confidence': ...}
    print(result['acoustics'])  # {'pitch_hz': ..., ...}
    ```
    """
    
    def __init__(self):
        """Инициализируем расширенный pipeline"""
        self.voice_analyzer = ResoCallVoiceAnalyzer()
    
    def process_with_emotion(self, audio_path: str, base_result: Dict) -> Dict:
        """
        Обрабатывает аудио и добавляет эмоциональный анализ
        
        Args:
            audio_path: Путь к аудиофайлу
            base_result: Результат базовой обработки (из текущего audio_pipeline)
            
        Returns:
            Расширенный результат с эмоциональным анализом
        """
        return self.voice_analyzer.add_emotion_analysis(audio_path, base_result)


# ============= ПРИМЕРЫ ИНТЕГРАЦИИ =============

def example_1_add_to_audio_pipeline():
    """
    Пример 1: Добавить эмоции к результатам audio_pipeline
    """
    print("\n=== ПРИМЕР 1: Интеграция с audio_pipeline ===\n")
    
    # Предположим, что это результат из audio_pipeline.process()
    base_result = {
        'transcript': 'Здравствуйте, как дела?',
        'sentiment': 'positive',
        'category': 'greeting',
        'script_adherence': True,
        'duration': 2.5,
    }
    
    # Добавляем анализ эмоций
    analyzer = ResoCallVoiceAnalyzer()
    enhanced_result = analyzer.add_emotion_analysis('path/to/audio.wav', base_result)
    
    print("Результат с эмоциями:")
    import json
    print(json.dumps(enhanced_result, indent=2, ensure_ascii=False))


def example_2_fastapi_endpoint():
    """
    Пример 2: FastAPI endpoint для анализа эмоций
    """
    print("\n=== ПРИМЕР 2: FastAPI Endpoint ===\n")
    
    code = '''
from fastapi import File, UploadFile
from resocall_voice_analyzer import ResoCallVoiceAnalyzer
import tempfile
import os

analyzer = ResoCallVoiceAnalyzer()

@app.post("/api/v1/analyze-emotion/")
async def analyze_emotion(file: UploadFile = File(...)):
    """Анализирует эмоциональное состояние в аудио"""
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    
    try:
        # Базовый результат (из существующего анализа)
        base_result = {
            'filename': file.filename,
            'file_size': file.size,
        }
        
        # Добавляем эмоции
        result = analyzer.add_emotion_analysis(tmp_path, base_result)
        
        return {
            "status": "success",
            "emotion": result.get('emotion'),
            "acoustics": result.get('acoustics'),
            "recommendation": analyzer.get_health_recommendation(result)
        }
    finally:
        os.unlink(tmp_path)
'''
    print(code)


def example_3_batch_processing():
    """
    Пример 3: Пакетная обработка звонков
    """
    print("\n=== ПРИМЕР 3: Пакетная обработка ===\n")
    
    code = '''
import glob
from resocall_voice_analyzer import ResoCallVoiceAnalyzer

analyzer = ResoCallVoiceAnalyzer()

# Обрабатываем все wav файлы
for audio_file in glob.glob("recordings/*.wav"):
    # Получаем базовый результат анализа
    base_result = analyze_audio(audio_file)  # Ваша функция
    
    # Добавляем эмоции
    enhanced_result = analyzer.add_emotion_analysis(audio_file, base_result)
    
    # Выводим резюме
    summary = analyzer.format_emotion_summary(enhanced_result)
    print(f"{audio_file}: {summary}")
    
    # Выводим рекомендацию если есть
    recommendation = analyzer.get_health_recommendation(enhanced_result)
    if recommendation:
        print(f"  {recommendation}")
'''
    print(code)


if __name__ == "__main__":
    print("="*70)
    print("РЕЗОКАЛ VOICE EMOTION ANALYZER - ПРИМЕРЫ ИНТЕГРАЦИИ")
    print("="*70)
    
    example_1_add_to_audio_pipeline()
    example_2_fastapi_endpoint()
    example_3_batch_processing()
    
    print("\n" + "="*70)
    print("Для полной интеграции в ResoCall:")
    print("="*70)
    print("""
1. Установите зависимости:
   cd Voice_Analysis
   pip install -r requirements.txt

2. Добавьте в server/app/services/audio_pipeline.py:
   from Voice_Analysis.resocall_voice_analyzer import ResoCallVoiceAnalyzer
   
   # В __init__:
   self.voice_analyzer = ResoCallVoiceAnalyzer()
   
   # В методе process():
   result = self.voice_analyzer.add_emotion_analysis(audio_path, result)

3. Добавьте endpoint в server/app/routers/analysis.py:
   @router.post("/api/v1/analyze-emotion/")
   async def analyze_emotion(file: UploadFile = File(...)):
       # Используйте ResoCallVoiceAnalyzer

4. Тестируйте с test_demo.py:
   python Voice_Analysis/test_demo.py
""")
