import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from collections import Counter

from ASR import CallAnalyzer
from asr_checker import calculate_wer, calculate_cer, align_words


class ASREvaluator:
    """
    Объединяет распознавание и оценку качества, сохраняет лог для дообучения.
    """
    def __init__(self, asr_model_name: str = "base", sr: int = 16000, denoise: bool = True):
        self.analyzer = CallAnalyzer(asr_model_name=asr_model_name, sr=sr, denoise=denoise)

    def evaluate(self, audio_path: str, reference_path: Optional[str] = None,
                 log_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Выполняет полный анализ аудио, при наличии эталона вычисляет метрики.
        Результаты сохраняются в лог-файл в указанной директории.
        """
        # 1. Распознавание
        result = self.analyzer.analyze(audio_path)

        # 2. Оценка качества, если передан эталон
        if reference_path and os.path.exists(reference_path):
            with open(reference_path, 'r', encoding='utf-8') as f:
                ref_text = f.read().strip()
            hyp_text = ' '.join([seg['text'] for seg in result['segments']])

            wer_dist, wer_len = calculate_wer(ref_text, hyp_text)
            cer_dist, cer_len = calculate_cer(ref_text, hyp_text)

            # Детальный разбор ошибок
            ref_words = ref_text.split()
            hyp_words = hyp_text.split()
            subs, dels, ins = align_words(ref_words, hyp_words)

            result['evaluation'] = {
                'wer': wer_dist / wer_len if wer_len else 0.0,
                'cer': cer_dist / cer_len if cer_len else 0.0,
                'reference': ref_text,
                'hypothesis': hyp_text,
                'substitutions': subs,
                'deletions': dels,
                'insertions': ins,
                'reference_length': wer_len
            }
        else:
            result['evaluation'] = None

        # 3. Сохранение лога
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
            log_file = Path(log_dir) / (Path(audio_path).stem + "_log.json")
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

        return result


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="ASR с оценкой качества и логированием")
    parser.add_argument("audio", help="Путь к аудиофайлу")
    parser.add_argument("--ref", help="Путь к эталонному тексту (опционально)")
    parser.add_argument("--log_dir", default="asr_logs", help="Директория для логов")
    parser.add_argument("--model", default="base", help="Модель Whisper")
    args = parser.parse_args()

    evaluator = ASREvaluator(asr_model_name=args.model)
    res = evaluator.evaluate(args.audio, args.ref, args.log_dir)
    print(json.dumps(res, ensure_ascii=False, indent=2))
