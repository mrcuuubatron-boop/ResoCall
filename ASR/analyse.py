import json
import ollama
from typing import Dict, Any


def analyze_call(transcript: str, model_name: str) -> Dict[str, Any]:
    """
    Анализирует текст звонка с помощью LLM.
    Возвращает словарь:
        "dialogue": [{"role": "client"|"operator", "text": str}, ...]
        "assessment": {
            "client_mood": "позитивное/нейтральное/негативное",
            "overall_rating": "позитивная/нейтральная/негативная",
            "work_rating": int (1-10),
            "professionalism": int (1-10),
            "friendliness": int (1-10),
            "politeness": int (1-10)
        }
    """
    system_prompt = (
        "Ты — эксперт по анализу телефонных разговоров. "
        "Ты всегда отвечаешь строго в формате JSON без каких-либо пояснений."
    )

    user_prompt = f"""
Проанализируй приведённый ниже телефонный разговор и определи:
- Роли участников (клиент или оператор) для каждой реплики.
- Настроение клиента, общую оценку звонка и оценки по шкале 1-10 для параметров: работа, профессионализм, доброжелательность, вежливость.

Разговор:
{transcript}

Верни **только** JSON-объект с такой структурой:
{{
  "dialogue": [
    {{"role": "client" или "operator", "text": "реплика"}},
    ...
  ],
  "assessment": {{
    "client_mood": "позитивное/нейтральное/негативное",
    "overall_rating": "позитивная/нейтральная/негативная",
    "work_rating": число,
    "professionalism": число,
    "friendliness": число,
    "politeness": число
  }}
}}
Не добавляй никаких комментариев, только JSON.
"""
    response = ollama.chat(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        options={"temperature": 0},
    )

    raw_content = response["message"]["content"].strip()
    # Иногда модель добавляет лишний текст до/после JSON, удаляем
    # Пытаемся найти первый '{' и последний '}'
    start_idx = raw_content.find("{")
    end_idx = raw_content.rfind("}")
    if start_idx == -1 or end_idx == -1:
        raise ValueError("Модель не вернула JSON: " + raw_content)

    json_str = raw_content[start_idx : end_idx + 1]
    result = json.loads(json_str)
    return result


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Анализ текста звонка")
    parser.add_argument("--model", required=True, help="Идентификатор модели Ollama")
    parser.add_argument("--file", required=True, help="Файл с текстом звонка")
    parser.add_argument(
        "--output", "-o", default=None, help="Сохранить результат в JSON (иначе stdout)"
    )
    args = parser.parse_args()

    with open(args.file, "r", encoding="utf-8") as f:
        transcript = f.read()

    result = analyze_call(transcript, model_name=args.model)

    json_str = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(json_str)
        print(f"Результат сохранён в {args.output}")
    else:
        print(json_str)


if __name__ == "__main__":
    main()
