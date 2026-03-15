import json
import librosa
import noisereduce as nr
import numpy as np
import soundfile as sf
import whisper
from typing import List, Dict, Any, Optional
import warnings
warnings.filterwarnings("ignore", category=UserWarning)  # для чистоты вывода

class AudioProcessor:
    """
    Класс для обработки аудио: загрузка, ресемплинг, шумоподавление.
    """
    def __init__(self, target_sr: int = 16000):
        self.target_sr = target_sr

    def load_and_preprocess(self, audio_path: str, denoise: bool = True) -> np.ndarray:
        """
        Загружает аудио, приводит к нужной частоте дискретизации, применяет шумоподавление.
        Возвращает массив float32 в диапазоне [-1, 1].
        """
        # Загрузка с сохранением исходной частоты
        audio, sr = librosa.load(audio_path, sr=None, mono=True)
        # Ресемплинг при необходимости
        if sr != self.target_sr:
            audio = librosa.resample(audio, orig_sr=sr, target_sr=self.target_sr)
        # Шумоподавление (вычитание профиля шума из первых 0.5 сек)
        if denoise:
            # Предполагаем, что первые 0.5 сек - тишина или шум
            noise_sample = audio[:int(0.5 * self.target_sr)]
            audio = nr.reduce_noise(y=audio, sr=self.target_sr, y_noise=noise_sample)
        return audio


class SpeechRecognizer:
    """
    Распознавание речи с помощью Whisper с таймстемпами.
    """
    def __init__(self, model_name: str = "base"):
        self.model = whisper.load_model(model_name)
        self.model_name = model_name

    def transcribe_with_timestamps(self, audio: np.ndarray) -> List[Dict[str, Any]]:
        """
        Принимает аудио (numpy массив с частотой 16000 Гц), возвращает список сегментов
        с текстом и временными метками (start, end).
        """
        # Whisper ожидает на вход или путь к файлу, или аудио в float32 с частотой 16000
        # Используем опцию word_timestamps=True для точных границ слов (требует модели large?)
        # Для простоты получаем сегменты с фразами.
        result = self.model.transcribe(audio, language="ru", word_timestamps=False)
        segments = []
        for seg in result["segments"]:
            segments.append({
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].strip()
            })
        return segments


class AcousticAnalyzer:
    """
    Анализ акустических характеристик: высота голоса (pitch), интенсивность (RMS).
    Может быть расширен для классификации эмоций.
    """
    def __init__(self, sr: int = 16000, frame_length: int = 2048, hop_length: int = 512):
        self.sr = sr
        self.frame_length = frame_length
        self.hop_length = hop_length

    def analyze_segment(self, audio: np.ndarray, start: float, end: float) -> Dict[str, Any]:
        """
        Для заданного временного интервала аудио вычисляет средний pitch и RMS.
        """
        # Индексы сэмплов
        start_sample = int(start * self.sr)
        end_sample = int(end * self.sr)
        segment_audio = audio[start_sample:end_sample]

        if len(segment_audio) == 0:
            return {"mean_pitch": None, "mean_rms": None, "pitch_std": None}

        # Вычисление основного тона (pitch) через librosa.pyin
        # fmin и fmax можно подстроить под человеческий голос (75-300 Гц)
        f0, voiced_flag, voiced_probs = librosa.pyin(
            segment_audio,
            fmin=75,
            fmax=300,
            sr=self.sr,
            frame_length=self.frame_length,
            hop_length=self.hop_length
        )
        # Убираем NaN (неопределённый pitch)
        f0_clean = f0[~np.isnan(f0)]
        mean_pitch = float(np.mean(f0_clean)) if len(f0_clean) > 0 else None
        pitch_std = float(np.std(f0_clean)) if len(f0_clean) > 0 else None

        # Среднеквадратичная энергия (громкость)
        rms = librosa.feature.rms(y=segment_audio, frame_length=self.frame_length, hop_length=self.hop_length)[0]
        mean_rms = float(np.mean(rms))

        return {
            "mean_pitch": mean_pitch,
            "pitch_std": pitch_std,
            "mean_rms": mean_rms
        }


class CallAnalyzer:
    """
    Основной класс, объединяющий все этапы.
    """
    def __init__(self, asr_model_name: str = "base", sr: int = 16000, denoise: bool = True):
        self.sr = sr
        self.denoise = denoise
        self.audio_processor = AudioProcessor(target_sr=sr)
        self.speech_recognizer = SpeechRecognizer(model_name=asr_model_name)
        self.acoustic_analyzer = AcousticAnalyzer(sr=sr)

    def analyze(self, audio_path: str) -> Dict[str, Any]:
        """
        Основной метод: обрабатывает аудио и возвращает структурированный результат.
        """
        # 1. Предобработка
        audio = self.audio_processor.load_and_preprocess(audio_path, denoise=self.denoise)

        # 2. Распознавание речи (получаем сегменты)
        segments = self.speech_recognizer.transcribe_with_timestamps(audio)

        # 3. Для каждого сегмента – акустический анализ
        enhanced_segments = []
        for seg in segments:
            acoustic = self.acoustic_analyzer.analyze_segment(audio, seg["start"], seg["end"])
            seg.update(acoustic)
            # Заглушка для эмоций (можно заменить реальной моделью)
            seg["emotion"] = "unknown"
            enhanced_segments.append(seg)

        # 4. Общая статистика
        all_pitches = [s["mean_pitch"] for s in enhanced_segments if s["mean_pitch"] is not None]
        overall_stats = {
            "avg_pitch": float(np.mean(all_pitches)) if all_pitches else None,
            "pitch_range": float(np.ptp(all_pitches)) if all_pitches else None,
            "total_duration": segments[-1]["end"] if segments else 0.0
        }

        result = {
            "file": audio_path,
            "segments": enhanced_segments,
            "overall_stats": overall_stats
        }
        return result

    def save_json(self, data: Dict[str, Any], output_path: str):
        """Сохранение результатов в JSON."""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    """Пример использования."""
    import argparse
    parser = argparse.ArgumentParser(description="Анализ звонка: распознавание речи + акустика")
    parser.add_argument("audio_file", help="Путь к аудиофайлу")
    parser.add_argument("--output", "-o", default="result.json", help="Путь для сохранения JSON")
    parser.add_argument("--model", default="base", help="Модель Whisper (tiny/base/small/medium/large)")
    parser.add_argument("--no-denoise", action="store_false", dest="denoise", help="Отключить шумоподавление")
    args = parser.parse_args()

    analyzer = CallAnalyzer(asr_model_name=args.model, denoise=args.denoise)
    result = analyzer.analyze(args.audio_file)
    analyzer.save_json(result, args.output)
    print(f"Результат сохранён в {args.output}")
    # Можно вывести краткую информацию
    print(f"Всего сегментов: {len(result['segments'])}")
    if result['overall_stats']['avg_pitch']:
        print(f"Средняя частота голоса: {result['overall_stats']['avg_pitch']:.1f} Гц")

if __name__ == "__main__":
    main()
