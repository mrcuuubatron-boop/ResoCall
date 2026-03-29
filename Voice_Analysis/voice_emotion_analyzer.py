"""
Voice Emotion and Psychological State Analysis Module
Анализ психологического состояния по акустическим характеристикам голоса
"""

import numpy as np
import librosa
import soundfile as sf
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import warnings

warnings.filterwarnings('ignore')


class PsychologicalState(Enum):
    """Психологическое состояние человека"""
    CALM = "спокойно"  # Низкая энергия, стабильный питч
    STRESSED = "стресс"  # Высокая энергия, нестабильный питч
    HAPPY = "радость"  # Высокий питч, высокая энергия
    SAD = "грусть"  # Низкий питч, низкая энергия
    ANGRY = "злость"  # Очень высокая энергия, агрессивный темп
    NEUTRAL = "нейтральное"  # Средние значения


@dataclass
class VoiceAnalysisResult:
    """Результаты анализа голоса"""
    state: PsychologicalState
    confidence: float  # 0.0 - 1.0
    
    # Акустические характеристики
    mean_pitch: float  # Средняя частота основного тона (Hz)
    pitch_variance: float  # Вариативность питча (нестабильность)
    mean_energy: float  # Средняя энергия сигнала
    energy_variance: float  # Вариативность энергии
    speech_rate: float  # Темп речи (слогов/сек)
    
    # Детальные оценки
    intensity_score: float  # 0-10 (интенсивность)
    stability_score: float  # 0-10 (стабильность)
    tempo_score: float  # 0-10 (быстрота речи)
    
    # Дополнительная информация
    duration: float  # Длительность аудио (сек)
    has_pauses: bool  # Наличие пауз
    pause_count: int  # Количество пауз


class VoiceEmotionAnalyzer:
    """
    Анализатор психологического состояния по голосу.
    
    Использует акустические признаки для определения эмоционального состояния.
    Работает полностью локально без интернета.
    """
    
    def __init__(self, sr: int = 16000):
        """
        Args:
            sr: Sample rate для обработки аудио
        """
        self.sr = sr
        self.fmin = 50  # Минимальная частота для питча (Hz)
        self.fmax = 400  # Максимальная частота для питча (Hz)
    
    def analyze(self, audio_path: str) -> VoiceAnalysisResult:
        """
        Анализирует аудиофайл и определяет психологическое состояние.
        
        Args:
            audio_path: Путь к аудиофайлу (wav, mp3, ogg, flac и т.д.)
            
        Returns:
            VoiceAnalysisResult с определенным состоянием и метриками
        """
        # Загружаем аудио
        y, sr = librosa.load(audio_path, sr=self.sr)
        
        # Извлекаем признаки
        features = self._extract_features(y)
        
        # Определяем состояние
        state, confidence = self._classify_state(features)
        
        return VoiceAnalysisResult(
            state=state,
            confidence=confidence,
            mean_pitch=features['mean_pitch'],
            pitch_variance=features['pitch_variance'],
            mean_energy=features['mean_energy'],
            energy_variance=features['energy_variance'],
            speech_rate=features['speech_rate'],
            intensity_score=features['intensity_score'],
            stability_score=features['stability_score'],
            tempo_score=features['tempo_score'],
            duration=features['duration'],
            has_pauses=features['has_pauses'],
            pause_count=features['pause_count']
        )
    
    def _extract_features(self, y: np.ndarray) -> Dict:
        """Извлекает акустические признаки из аудиосигнала"""
        
        # Основные параметры
        duration = librosa.get_duration(y=y, sr=self.sr)
        
        # ===== PITCH (основной тон) =====
        # Используем YIN алгоритм для деткции питча
        f0 = self._extract_pitch(y)
        
        # Фильтруем нули
        f0_valid = f0[f0 > 0]
        
        if len(f0_valid) > 0:
            mean_pitch = np.mean(f0_valid)
            pitch_variance = np.var(f0_valid)
        else:
            mean_pitch = 0
            pitch_variance = 0
        
        # ===== ENERGY (энергия сигнала) =====
        S = librosa.feature.melspectrogram(y=y, sr=self.sr)
        log_S = librosa.power_to_db(S, ref=np.max)
        mean_energy = np.mean(log_S)
        energy_variance = np.var(log_S)
        
        # ===== MFCC (мель-частотные коэффициенты) =====
        mfcc = librosa.feature.mfcc(y=y, sr=self.sr, n_mfcc=13)
        mfcc_mean = np.mean(mfcc, axis=1)
        
        # ===== TEMPO (темп речи) =====
        onset_env = librosa.onset.onset_strength(y=y, sr=self.sr)
        tempogram = librosa.feature.tempogram(onset_envelope=onset_env, sr=self.sr)
        
        # Оцениваем темп по количеству пиков в сек
        speech_rate = np.sum(onset_env > np.mean(onset_env)) / duration if duration > 0 else 0
        
        # ===== ПАУЗЫ =====
        has_pauses, pause_count = self._detect_pauses(y)
        
        # ===== ВЫЧИСЛЯЕМ SCORES (0-10) =====
        # Нормализуем питч (человеческий диапазон ~50-400 Hz)
        normalized_pitch = np.clip(mean_pitch / 200, 0, 2)  # 200 Hz = средний питч
        
        # Интенсивность (громкость + энергия)
        intensity_score = min(10, max(0, (mean_energy + 40) / 8))  # dB шкала
        
        # Стабильность (обратно пропорциональна вариативности)
        stability_score = max(0, 10 - (pitch_variance / 100))
        stability_score = min(10, stability_score)
        
        # Темп речи
        tempo_score = min(10, speech_rate / 5)  # 5 пиков/сек = максимум
        
        return {
            'mean_pitch': float(mean_pitch),
            'pitch_variance': float(pitch_variance),
            'mean_energy': float(mean_energy),
            'energy_variance': float(energy_variance),
            'speech_rate': float(speech_rate),
            'mfcc_mean': mfcc_mean,
            'duration': float(duration),
            'has_pauses': has_pauses,
            'pause_count': pause_count,
            'intensity_score': float(intensity_score),
            'stability_score': float(stability_score),
            'tempo_score': float(tempo_score),
            'normalized_pitch': float(normalized_pitch)
        }
    
    def _extract_pitch(self, y: np.ndarray, frame_length: int = 2048) -> np.ndarray:
        """Извлекает питч (основной тон) используя автокорреляцию"""
        
        hop_length = frame_length // 4
        f0 = np.zeros(len(y) // hop_length)
        
        for i in range(len(f0)):
            frame = y[i*hop_length:i*hop_length + frame_length]
            if len(frame) < frame_length:
                frame = np.pad(frame, (0, frame_length - len(frame)))
            
            # Простая автокорреляция
            autocorr = np.correlate(frame, frame, mode='full')
            autocorr = autocorr[len(autocorr)//2:]
            
            # Ищем питч в диапазоне 50-400 Hz
            min_lag = int(self.sr / self.fmax)
            max_lag = int(self.sr / self.fmin)
            
            if max_lag < len(autocorr):
                lag = np.argmax(autocorr[min_lag:max_lag]) + min_lag
                f0[i] = self.sr / lag
            else:
                f0[i] = 0
        
        return f0
    
    def _detect_pauses(self, y: np.ndarray, threshold_db: float = -40) -> Tuple[bool, int]:
        """Детектирует паузы в речи"""
        
        # Вычисляем энергию фреймов
        S = librosa.feature.melspectrogram(y=y, sr=self.sr)
        log_S = librosa.power_to_db(S, ref=np.max)
        energy = np.mean(log_S, axis=0)
        
        # Ищем фреймы с низкой энергией (паузы)
        silence = energy < threshold_db
        pause_count = np.sum(np.diff(silence.astype(int)) > 0)  # Переходы от звука к тишине
        
        has_pauses = pause_count > 0
        
        return has_pauses, int(pause_count)
    
    def _classify_state(self, features: Dict) -> Tuple[PsychologicalState, float]:
        """
        Классифицирует психологическое состояние на основе признаков.
        
        Используется система правил на основе акустических параметров.
        """
        
        pitch = features['mean_pitch']
        energy = features['mean_energy']
        stability = features['stability_score']
        tempo = features['tempo_score']
        intensity = features['intensity_score']
        pitch_var = features['pitch_variance']
        
        # Нормализуем значения для сравнения
        
        # ===== ПРАВИЛА КЛАССИФИКАЦИИ =====
        
        # ANGRY (злость): высокая энергия, высокий темп, нестабильный питч
        if intensity > 6 and tempo > 5 and stability < 5:
            confidence = min(0.95, (intensity / 10 + tempo / 10 + (10 - stability) / 10) / 3 + 0.3)
            return PsychologicalState.ANGRY, confidence
        
        # STRESSED (стресс): высокая вариативность питча, повышенная энергия, быстрая речь
        if pitch_var > 50 and intensity > 5 and tempo > 4:
            confidence = min(0.95, (pitch_var / 100 + intensity / 10 + tempo / 10) / 3 + 0.2)
            return PsychologicalState.STRESSED, confidence
        
        # HAPPY (радость): высокий питч, высокая энергия, быстрая четкая речь
        if pitch > 150 and intensity > 5 and stability > 6:
            confidence = min(0.95, (pitch / 200 + intensity / 10 + stability / 10) / 3 + 0.2)
            return PsychologicalState.HAPPY, confidence
        
        # SAD (грусть): низкий питч, низкая энергия, медленная речь
        if pitch < 100 and intensity < 4 and tempo < 2:
            confidence = min(0.95, ((200 - pitch) / 200 + (10 - intensity) / 10 + (10 - tempo) / 10) / 3 + 0.2)
            return PsychologicalState.SAD, confidence
        
        # CALM (спокойствие): низкая variability, средняя энергия, стабильный питч
        if stability > 7 and pitch_var < 30 and intensity < 6 and tempo < 3:
            confidence = min(0.95, (stability / 10 + (30 - pitch_var) / 30 + (10 - tempo) / 10) / 3 + 0.2)
            return PsychologicalState.CALM, confidence
        
        # NEUTRAL (нейтральное) - по умолчанию
        confidence = 0.6
        return PsychologicalState.NEUTRAL, confidence
    
    def get_detailed_report(self, result: VoiceAnalysisResult) -> str:
        """Возвращает детальный отчет на русском языке"""
        
        report = f"""
====================================================================
           АНАЛИЗ ПСИХОЛОГИЧЕСКОГО СОСТОЯНИЯ ПО ГОЛОСУ
====================================================================

ОПРЕДЕЛЕННОЕ СОСТОЯНИЕ:
   Состояние: {result.state.value}
   Уверенность: {result.confidence * 100:.1f}%

АКУСТИЧЕСКИЕ ХАРАКТЕРИСТИКИ:
   Базовый тон (питч):       {result.mean_pitch:.1f} Hz
   Вариативность питча:      {result.pitch_variance:.2f}
   Энергия сигнала:          {result.mean_energy:.1f} dB
   Вариативность энергии:    {result.energy_variance:.2f}
   Темп речи:                {result.speech_rate:.2f} слогов/сек
   Длительность:             {result.duration:.1f} сек

ОЦЕНОЧНЫЕ БАЛЛЫ (0-10):
   Интенсивность (громкость):  {result.intensity_score:.1f}/10
   Стабильность:               {result.stability_score:.1f}/10
   Темп речи:                  {result.tempo_score:.1f}/10

ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ:
   Наличие пауз:    {'Да' if result.has_pauses else 'Нет'}
   Количество пауз: {result.pause_count}

ИНТЕРПРЕТАЦИЯ:
"""
        
        # Дополнительные комментарии на основе состояния
        if result.state == PsychologicalState.CALM:
            report += "   • Человек находится в расслабленном, спокойном состоянии\n"
            report += "   • Речь ровная и стабильная\n"
            report += "   • Подходит для серьезных переговоров\n"
        
        elif result.state == PsychologicalState.STRESSED:
            report += "   • Признаки стресса и напряжения\n"
            report += "   • Нестабильный тон голоса\n"
            report += "   • Рекомендуется предложить передышку\n"
        
        elif result.state == PsychologicalState.HAPPY:
            report += "   • Позитивное, дружелюбное состояние\n"
            report += "   • Высокий и четкий голос\n"
            report += "   • Хорошее время для позитивного общения\n"
        
        elif result.state == PsychologicalState.SAD:
            report += "   • Признаки грусти или низкого настроения\n"
            report += "   • Низкий и медленный голос\n"
            report += "   • Может потребоваться эмоциональная поддержка\n"
        
        elif result.state == PsychologicalState.ANGRY:
            report += "   • ВНИМАНИЕ: Признаки раздражения/гнева\n"
            report += "   • Высокая интенсивность и быстрая речь\n"
            report += "   • Требуется деэскалация\n"
        
        else:
            report += "   • Нейтральное состояние\n"
            report += "   • Параметры находятся в среднем диапазоне\n"
        
        report += "\n" + "═" * 64 + "\n"
        
        return report


def main():
    """Пример использования"""
    import sys
    
    if len(sys.argv) < 2:
        print("Использование: python voice_emotion_analyzer.py <audio_file>")
        print("Поддерживаемые форматы: wav, mp3, ogg, flac")
        return
    
    audio_path = sys.argv[1]
    
    analyzer = VoiceEmotionAnalyzer()
    result = analyzer.analyze(audio_path)
    
    print(analyzer.get_detailed_report(result))


if __name__ == "__main__":
    main()
