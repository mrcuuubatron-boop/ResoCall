import json
import librosa
import noisereduce as nr
import numpy as np
import whisper
from typing import List, Dict, Any
import warnings

warnings.filterwarnings("ignore", category=UserWarning)


class AudioProcessor:
    """Загрузка, ресемплинг, шумоподавление."""

    def __init__(self, target_sr: int = 16000):
        self.target_sr = target_sr

    def load_and_preprocess(self, audio_path: str, denoise: bool = True) -> np.ndarray:
        audio, sr = librosa.load(audio_path, sr=None, mono=True)
        if sr != self.target_sr:
            audio = librosa.resample(audio, orig_sr=sr, target_sr=self.target_sr)
        if denoise:
            noise_sample = audio[: int(0.5 * self.target_sr)]
            audio = nr.reduce_noise(y=audio, sr=self.target_sr, y_noise=noise_sample)
        return audio


class SpeechRecognizer:
    """Whisper-транскрипция с временными метками."""

    def __init__(self, model_name: str = "base"):
        self.model = whisper.load_model(model_name)

    def transcribe_with_timestamps(self, audio: np.ndarray) -> List[Dict[str, Any]]:
        result = self.model.transcribe(audio, language="ru", word_timestamps=False)
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
    audio_path: str, model_name: str = "base", denoise: bool = True
) -> Dict[str, Any]:
    """
    Основная функция модуля.
    Возвращает словарь:
        "segments": [{"start": float, "end": float, "text": str}, ...]
        "full_text": str – полная расшифровка
    """
    processor = AudioProcessor(target_sr=16000)
    audio = processor.load_and_preprocess(audio_path, denoise=denoise)

    recognizer = SpeechRecognizer(model_name=model_name)
    segments = recognizer.transcribe_with_timestamps(audio)

    full_text = " ".join(seg["text"] for seg in segments)

    return {"segments": segments, "full_text": full_text}


class CallAnalyzer:
    """Compatibility wrapper so server's external analyzer can import this module

    Provides a simple `analyze(audio_path)` method returning a dict with
    a `segments` list compatible with the server's expectations.
    """

    def __init__(self, asr_model_name: str = "base", sr: int = 16000, denoise: bool = True) -> None:
        self.asr_model_name = asr_model_name
        self.sr = sr
        self.denoise = denoise

    def analyze(self, audio_path: str) -> Dict[str, Any]:
        # Reuse transcribe_audio to produce the same structure the server expects.
        return transcribe_audio(audio_path, model_name=self.asr_model_name, denoise=self.denoise)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="ASR: транскрипция аудио")
    parser.add_argument("audio_file", help="Путь к аудиофайлу")
    parser.add_argument(
        "--output", "-o", default=None, help="Сохранить результат в JSON (иначе stdout)"
    )
    parser.add_argument(
        "--model", default="base", help="Модель Whisper (tiny/base/small/medium/large)"
    )
    parser.add_argument(
        "--no-denoise",
        action="store_false",
        dest="denoise",
        help="Отключить шумоподавление",
    )
    args = parser.parse_args()

    result = self.model.transcribe(
        audio,
        language="ru",
        prompt="Клиент, оператор, подключение, тариф, интернет, заявка, техподдержка",
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
