import json
import librosa
import numpy as np
import whisper
from typing import List, Dict, Any, Optional
import warnings
from scipy.signal import butter, filtfilt

warnings.filterwarnings("ignore", category=UserWarning)


class AudioProcessor:
    """Загрузка, ресемплинг, high-pass фильтр, нормализация громкости."""

    def __init__(self, target_sr: int = 16000):
        self.target_sr = target_sr

    @staticmethod
    def _high_pass_filter(
        audio: np.ndarray, sr: int, cutoff: float = 80.0
    ) -> np.ndarray:
        """Удаляет низкочастотный гул (например, от кондиционера, вентиляции)."""
        nyquist = 0.5 * sr
        normal_cutoff = cutoff / nyquist
        b, a = butter(4, normal_cutoff, btype="high", analog=False)
        return filtfilt(b, a, audio)

    @staticmethod
    def _remove_dc_offset(audio: np.ndarray) -> np.ndarray:
        """Убирает постоянную составляющую (смещение нуля)."""
        return audio - np.mean(audio)

    def load_and_preprocess(
        self,
        audio_path: str,
        denoise: bool = False,  # по умолчанию выключено, т.к. старый метод вредил
        high_pass: bool = True,
        normalize_volume: bool = True,
        remove_dc: bool = True,
    ) -> np.ndarray:
        audio, sr = librosa.load(audio_path, sr=None, mono=True)

        # Ресемплинг до целевой частоты
        if sr != self.target_sr:
            audio = librosa.resample(audio, orig_sr=sr, target_sr=self.target_sr)
            sr = self.target_sr

        # Удаление DC offset
        if remove_dc:
            audio = self._remove_dc_offset(audio)

        # High-pass фильтр (убирает низкие частоты, шум)
        if high_pass:
            audio = self._high_pass_filter(audio, sr, cutoff=80.0)

        # Нормализация громкости: пик к 0.9
        if normalize_volume:
            max_val = np.max(np.abs(audio))
            if max_val > 0:
                audio = audio / max_val * 0.9

        # Шумоподавление noisereduce – ОСТОРОЖНО! Используем только если очень нужно.
        # Для этого требуется установка noisereduce. Я оставляю как опцию, но по умолчанию False.
        if denoise:
            try:
                import noisereduce as nr

                noise_sample = audio[: int(0.5 * self.target_sr)]
                audio = nr.reduce_noise(
                    y=audio, sr=self.target_sr, y_noise=noise_sample
                )
            except ImportError:
                warnings.warn("noisereduce not installed, skipping denoise")

        return audio


class SpeechRecognizer:
    """Whisper-транскрипция с временными метками и поддержкой prompt."""

    def __init__(self, model_name: str = "small"):  # изменили default с base на small
        self.model = whisper.load_model(model_name)

    def transcribe_with_timestamps(
        self,
        audio: np.ndarray,
        language: str = "ru",
        prompt: Optional[str] = None,
        word_timestamps: bool = False,
        temperature: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """
        Параметры:
            prompt - текст, который направляет модель (например, ключевые слова диалога)
            temperature - 0.0 даёт детерминированный, но точный результат;
                           выше (0.2) – больше вариантов, но может ошибаться.
        """
        # Подготовка опций
        options = {
            "language": language,
            "word_timestamps": word_timestamps,
            "temperature": temperature,
        }
        if prompt:
            options["initial_prompt"] = prompt

        result = self.model.transcribe(audio, **options)

        segments = []
        for seg in result["segments"]:
            segments.append(
                {
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"].strip(),
                }
            )
        return segments


def transcribe_audio(
    audio_path: str,
    model_name: str = "small",
    denoise: bool = False,
    high_pass: bool = True,
    prompt: Optional[str] = None,
    language: str = "ru",
) -> Dict[str, Any]:
    """
    Основная функция.
    Возвращает словарь:
        "segments": [{"start": float, "end": float, "text": str}, ...]
        "full_text": str
    """
    processor = AudioProcessor(target_sr=16000)
    audio = processor.load_and_preprocess(
        audio_path, denoise=denoise, high_pass=high_pass
    )

    recognizer = SpeechRecognizer(model_name=model_name)
    segments = recognizer.transcribe_with_timestamps(
        audio, language=language, prompt=prompt
    )

    full_text = " ".join(seg["text"] for seg in segments)
    return {"segments": segments, "full_text": full_text}


class CallAnalyzer:
    """Совместимость с внешним сервером, который ожидает метод analyze(audio_path)."""

    def __init__(
        self,
        asr_model_name: str = "small",
        sr: int = 16000,
        denoise: bool = False,
        prompt: Optional[str] = None,
    ) -> None:
        self.asr_model_name = asr_model_name
        self.sr = sr
        self.denoise = denoise
        self.prompt = prompt

    def analyze(self, audio_path: str) -> Dict[str, Any]:
        return transcribe_audio(
            audio_path,
            model_name=self.asr_model_name,
            denoise=self.denoise,
            prompt=self.prompt,
        )


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="ASR: транскрипция аудио с улучшенной обработкой"
    )
    parser.add_argument("audio_file", help="Путь к аудиофайлу")
    parser.add_argument(
        "--output", "-o", default=None, help="Сохранить результат в JSON"
    )
    parser.add_argument(
        "--model", default="small", help="Модель Whisper (tiny/base/small/medium/large)"
    )
    parser.add_argument(
        "--no-highpass",
        action="store_false",
        dest="high_pass",
        help="Отключить high-pass фильтр (80 Гц)",
    )
    parser.add_argument(
        "--denoise",
        action="store_true",
        help="Включить шумоподавление noisereduce (осторожно!)",
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="Клиент, оператор, подключение, тариф, интернет, заявка, техподдержка",
        help="Начальный prompt для Whisper",
    )
    args = parser.parse_args()

    # Вызываем улучшенную транскрипцию
    result = transcribe_audio(
        audio_path=args.audio_file,
        model_name=args.model,
        denoise=args.denoise,
        high_pass=args.high_pass,
        prompt=args.prompt,
    )

    json_str = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(json_str)
        print(f"Результат сохранён в {args.output}")
    else:
        print(json_str)


if __name__ == "__main__":
    main()
