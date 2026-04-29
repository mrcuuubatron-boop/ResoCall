import json
from typing import Dict, Any
from ASR import transcribe_audio
from analyse import analyze_call


def process_call(
    audio_path: str,
    asr_model: str = "base",
    analysis_model: str = "llama3.1:8b",
    denoise: bool = True,
) -> Dict[str, Any]:
    """
    Полный пайплайн обработки одного звонка.
    Возвращает итоговый JSON, готовый к сохранению в БД.
    """
    # 1. Транскрипция
    asr_result = transcribe_audio(audio_path, model_name=asr_model, denoise=denoise)
    full_text = asr_result["full_text"]

    # 2. Анализ (диалог + оценки)
    analysis_result = analyze_call(full_text, model_name=analysis_model)

    # 3. Итоговая структура: объединяем сегменты из ASR (опционально) с диалогом
    final_output = {
        "segments": asr_result["segments"],  # временные метки
        "dialogue": analysis_result["dialogue"],  # роли и реплики
        "assessment": analysis_result["assessment"],
    }
    return final_output


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Пайплайн обработки звонка")
    parser.add_argument("audio_file", help="Путь к аудиофайлу")
    parser.add_argument("--asr-model", default="medium", help="Модель Whisper")
    parser.add_argument(
        "--analysis-model", default="llama3.1:8b", help="Модель Ollama для анализа"
    )
    parser.add_argument("--no-denoise", action="store_false", dest="denoise")
    parser.add_argument("--output", "-o", help="Сохранить результат в JSON")
    args = parser.parse_args()

    result = process_call(
        args.audio_file,
        asr_model=args.asr_model,
        analysis_model=args.analysis_model,
        denoise=args.denoise,
    )

    json_str = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(json_str)
        print(f"Результат сохранён в {args.output}")
    else:
        print(json_str)
