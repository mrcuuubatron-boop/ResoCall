from __future__ import annotations

from dataclasses import dataclass
import importlib.util
from threading import Lock
from typing import Any

import librosa
import noisereduce as nr
import numpy as np
import whisper

from app.schemas import AnalysisResultOut, CallSummaryOut, ScriptCheckOut, SegmentOut


@dataclass
class PipelineConfig:
    sample_rate: int = 16000
    asr_model: str = "base"
    denoise: bool = True
    use_external_asr_module: bool = True
    external_asr_module_path: str = "../ASR/ASR.py"


class ProcessingPipeline:
    """Single-process voice processing pipeline with lazy ASR model loading."""

    def __init__(self, cfg: PipelineConfig) -> None:
        self.cfg = cfg
        self._model_lock = Lock()
        self._model = None
        self._external_asr_status = "disabled"
        self._external_asr_error: str | None = None
        self._external_analyzer = self._build_external_analyzer()

    def _build_external_analyzer(self):
        if not self.cfg.use_external_asr_module:
            self._external_asr_status = "disabled"
            self._external_asr_error = None
            return None

        try:
            module_spec = importlib.util.spec_from_file_location("resocall_external_asr", self.cfg.external_asr_module_path)
            if module_spec is None or module_spec.loader is None:
                self._external_asr_status = "unavailable"
                self._external_asr_error = "Cannot load module spec"
                return None
            module = importlib.util.module_from_spec(module_spec)
            module_spec.loader.exec_module(module)
            analyzer_cls = getattr(module, "CallAnalyzer", None)
            if analyzer_cls is None:
                self._external_asr_status = "unavailable"
                self._external_asr_error = "CallAnalyzer class is missing"
                return None
            analyzer = analyzer_cls(asr_model_name=self.cfg.asr_model, sr=self.cfg.sample_rate, denoise=self.cfg.denoise)
            self._external_asr_status = "active"
            self._external_asr_error = None
            return analyzer
        except Exception as exc:
            # Fallback to internal pipeline when external module is unavailable.
            self._external_asr_status = "unavailable"
            self._external_asr_error = str(exc)
            return None

    def runtime_info(self) -> dict[str, Any]:
        return {
            "external_asr_enabled": self.cfg.use_external_asr_module,
            "external_asr_status": self._external_asr_status,
            "external_asr_module_path": self.cfg.external_asr_module_path,
            "external_asr_error": self._external_asr_error,
            "asr_model": self.cfg.asr_model,
        }

    def reload_model(self, model_name: str) -> None:
        with self._model_lock:
            self._model = whisper.load_model(model_name)
            self.cfg.asr_model = model_name

    def _get_model(self):
        with self._model_lock:
            if self._model is None:
                self._model = whisper.load_model(self.cfg.asr_model)
            return self._model

    def _load_audio(self, audio_path: str) -> np.ndarray:
        audio, sr = librosa.load(audio_path, sr=None, mono=True)
        if sr != self.cfg.sample_rate:
            audio = librosa.resample(audio, orig_sr=sr, target_sr=self.cfg.sample_rate)
        if self.cfg.denoise and len(audio) > int(0.5 * self.cfg.sample_rate):
            noise_sample = audio[: int(0.5 * self.cfg.sample_rate)]
            audio = nr.reduce_noise(y=audio, sr=self.cfg.sample_rate, y_noise=noise_sample)
        return audio

    def _audio_quality_warnings(self, audio: np.ndarray) -> list[str]:
        warnings: list[str] = []
        rms = float(np.sqrt(np.mean(np.square(audio)))) if len(audio) else 0.0
        if rms < 0.01:
            warnings.append("Audio RMS is low, recognition quality may degrade")

        silent_share = float(np.mean(np.abs(audio) < 0.003)) if len(audio) else 1.0
        if silent_share > 0.5:
            warnings.append("High silence ratio detected")

        return warnings

    def _transcribe(self, audio: np.ndarray) -> list[dict[str, Any]]:
        model = self._get_model()
        result = model.transcribe(audio, language="ru", word_timestamps=False)
        output: list[dict[str, Any]] = []
        for segment in result.get("segments", []):
            output.append(
                {
                    "start": float(segment["start"]),
                    "end": float(segment["end"]),
                    "text": segment["text"].strip(),
                }
            )
        return output

    def _acoustic_metrics(self, audio: np.ndarray, start: float, end: float) -> tuple[float | None, float | None, float | None]:
        start_sample = int(start * self.cfg.sample_rate)
        end_sample = int(end * self.cfg.sample_rate)
        chunk = audio[start_sample:end_sample]
        if len(chunk) == 0:
            return None, None, None

        f0, _, _ = librosa.pyin(
            chunk,
            fmin=75,
            fmax=300,
            sr=self.cfg.sample_rate,
            frame_length=2048,
            hop_length=512,
        )
        f0_clean = f0[~np.isnan(f0)] if f0 is not None else np.array([])
        mean_pitch = float(np.mean(f0_clean)) if len(f0_clean) else None
        pitch_std = float(np.std(f0_clean)) if len(f0_clean) else None

        rms_arr = librosa.feature.rms(y=chunk, frame_length=2048, hop_length=512)[0]
        mean_rms = float(np.mean(rms_arr)) if len(rms_arr) else None
        return mean_pitch, pitch_std, mean_rms

    def _simple_sentiment(self, text: str) -> tuple[str, float]:
        text_l = text.lower()
        neg_words = ["жалоба", "ужас", "плохо", "претенз", "не работает", "ошибка", "расторг"]
        pos_words = ["спасибо", "хорошо", "отлично", "помогло", "благодар"]

        neg_score = sum(1 for w in neg_words if w in text_l)
        pos_score = sum(1 for w in pos_words if w in text_l)

        if neg_score > pos_score:
            return "negative", min(1.0, 0.5 + 0.1 * neg_score)
        if pos_score > neg_score:
            return "positive", min(1.0, 0.5 + 0.1 * pos_score)
        return "neutral", 0.5

    def _script_check(self, transcript: str, required_phrases: list[str]) -> ScriptCheckOut:
        transcript_l = transcript.lower()
        found = [p for p in required_phrases if p.lower() in transcript_l]
        missing = [p for p in required_phrases if p not in found]
        compliance = 100.0 if not required_phrases else (len(found) / len(required_phrases)) * 100.0
        return ScriptCheckOut(
            required_phrases=required_phrases,
            found_phrases=found,
            missing_phrases=missing,
            compliance_pct=round(compliance, 2),
        )

    def _classify_category(self, transcript: str) -> str:
        t = transcript.lower()
        if any(k in t for k in ["оплат", "счет", "биллинг", "тариф"]):
            return "billing"
        if any(k in t for k in ["не работает", "ошибка", "интернет", "техподдерж", "сбой"]):
            return "technical_support"
        if any(k in t for k in ["жалоба", "претенз", "расторг"]):
            return "complaint"
        return "consultation"

    def _priority(self, first_part: str, overall_sentiment: str, category: str) -> int:
        score = 1
        if overall_sentiment == "negative":
            score += 2
        if category == "complaint":
            score += 2
        if any(w in first_part.lower() for w in ["срочно", "немедленно", "плохо", "жалоба"]):
            score += 1
        return max(1, min(5, score))

    def process(self, task_id: str, file_name: str, audio_path: str, required_phrases: list[str]) -> dict[str, Any]:
        audio = self._load_audio(audio_path)
        quality_warnings = self._audio_quality_warnings(audio)

        external_segments: list[dict[str, Any]] | None = None
        if self._external_analyzer is not None:
            try:
                external_result = self._external_analyzer.analyze(audio_path)
                external_segments = external_result.get("segments", [])
                self._external_asr_status = "active"
                self._external_asr_error = None
            except Exception as exc:
                self._external_asr_status = "runtime_failed"
                self._external_asr_error = str(exc)
                external_segments = None

        if external_segments is not None:
            segments_raw = [
                {
                    "start": float(segment.get("start", 0.0)),
                    "end": float(segment.get("end", 0.0)),
                    "text": str(segment.get("text", "")).strip(),
                    "mean_pitch": segment.get("mean_pitch"),
                    "pitch_std": segment.get("pitch_std"),
                    "mean_rms": segment.get("mean_rms"),
                }
                for segment in external_segments
            ]
        else:
            segments_raw = self._transcribe(audio)

        segments_out: list[SegmentOut] = []
        sentiment_scores: list[float] = []
        sentiment_labels: list[str] = []
        full_text = []

        for segment in segments_raw:
            sentiment, sentiment_score = self._simple_sentiment(segment["text"])
            if "mean_pitch" in segment or "pitch_std" in segment or "mean_rms" in segment:
                mean_pitch = segment.get("mean_pitch")
                pitch_std = segment.get("pitch_std")
                mean_rms = segment.get("mean_rms")
            else:
                mean_pitch, pitch_std, mean_rms = self._acoustic_metrics(audio, segment["start"], segment["end"])

            sentiment_scores.append(sentiment_score)
            sentiment_labels.append(sentiment)
            full_text.append(segment["text"])

            segments_out.append(
                SegmentOut(
                    start=segment["start"],
                    end=segment["end"],
                    text=segment["text"],
                    speaker="unknown",
                    sentiment=sentiment,
                    sentiment_score=round(float(sentiment_score), 3),
                    mean_pitch=mean_pitch,
                    pitch_std=pitch_std,
                    mean_rms=mean_rms,
                )
            )

        transcript_text = " ".join(full_text).strip()
        script_check = self._script_check(transcript_text, required_phrases)

        avg_sentiment = float(np.mean(sentiment_scores)) if sentiment_scores else 0.5
        if avg_sentiment > 0.6 and sentiment_labels.count("positive") > sentiment_labels.count("negative"):
            overall_sentiment = "positive"
        elif avg_sentiment < 0.5 and sentiment_labels.count("negative") >= sentiment_labels.count("positive"):
            overall_sentiment = "negative"
        else:
            overall_sentiment = "neutral"

        category = self._classify_category(transcript_text)
        first_part = " ".join(full_text[: max(1, int(len(full_text) * 0.3))])
        priority = self._priority(first_part, overall_sentiment, category)

        total_duration = segments_out[-1].end if segments_out else 0.0

        result = AnalysisResultOut(
            task_id=task_id,
            file_name=file_name,
            total_duration=total_duration,
            segments=segments_out,
            script_check=script_check,
            summary=CallSummaryOut(
                category=category,
                priority=priority,
                overall_sentiment=overall_sentiment,
                warnings=quality_warnings,
            ),
        )
        return result.model_dump()
