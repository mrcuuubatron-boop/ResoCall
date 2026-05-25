import pytest
import json
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from ASR import transcribe_audio, AudioProcessor, SpeechRecognizer, CallAnalyzer
from analyse import analyze_call
from pipeline import process_call


# ======================== Фикстуры и вспомогательные данные ========================


@pytest.fixture
def mock_audio_processor():
    with patch("ASR.AudioProcessor.load_and_preprocess") as mock:
        # возвращаем синтетический аудио-массив
        mock.return_value = np.zeros(16000 * 5, dtype=np.float32)
        yield mock


@pytest.fixture
def mock_whisper_model():
    with patch("ASR.whisper.load_model") as mock_load:
        mock_model = Mock()
        # стандартный ответ whisper
        mock_model.transcribe.return_value = {
            "segments": [
                {
                    "start": 0.0,
                    "end": 2.5,
                    "text": "Добрый день, компания Ромашка, меня зовут Иван.",
                },
                {
                    "start": 2.5,
                    "end": 5.0,
                    "text": "У меня не списываются деньги за подписку.",
                },
            ]
        }
        mock_load.return_value = mock_model
        yield mock_model


@pytest.fixture
def mock_ollama():
    with patch("analyse.ollama.chat") as mock_chat:
        # стандартный ответ LLM
        mock_response = {
            "message": {
                "content": json.dumps(
                    {
                        "dialogue": [
                            {
                                "role": "operator",
                                "text": "Добрый день, компания Ромашка, меня зовут Иван.",
                            },
                            {
                                "role": "client",
                                "text": "У меня не списываются деньги за подписку.",
                            },
                        ],
                        "assessment": {
                            "client_mood": "негативное",
                            "overall_rating": "негативная",
                            "work_rating": 4,
                            "professionalism": 6,
                            "friendliness": 5,
                            "politeness": 7,
                        },
                    }
                )
            }
        }
        mock_chat.return_value = mock_response
        yield mock_chat


# ======================== 1. Блочное тестирование ASR ========================


def test_transcribe_audio_positive(mock_audio_processor, mock_whisper_model):
    """Б1: Позитивный тест ASR (распознавание)"""
    result = transcribe_audio("dummy.wav", model_name="base", denoise=True)

    assert "segments" in result
    assert "full_text" in result
    assert len(result["segments"]) == 2
    assert (
        result["full_text"]
        == "Добрый день, компания Ромашка, меня зовут Иван. У меня не списываются деньги за подписку."
    )
    mock_whisper_model.transcribe.assert_called_once()


def test_transcribe_audio_empty_audio(mock_audio_processor, mock_whisper_model):
    """Б2: Негативный тест – пустой аудиофайл (тишина)"""
    # Меняем возвращаемое значение Whisper: пустая транскрипция
    mock_whisper_model.transcribe.return_value = {"segments": []}

    result = transcribe_audio("silence.wav", denoise=True)

    assert result["segments"] == []
    assert result["full_text"] == ""


def test_transcribe_audio_no_denoise(mock_audio_processor, mock_whisper_model):
    """Проверка, что аргумент denoise передаётся в процессор"""
    with patch("ASR.AudioProcessor.load_and_preprocess") as mock_load:
        mock_load.return_value = np.zeros(1000)
        transcribe_audio("dummy.wav", denoise=False)
        # проверяем, что load_and_preprocess вызван с denoise=False
        mock_load.assert_called_once_with("dummy.wav", denoise=False)


def test_call_analyzer_compatibility():
    """Б22 (частично): тест обёртки CallAnalyzer, которая используется сервером"""
    with patch("ASR.transcribe_audio") as mock_transcribe:
        mock_transcribe.return_value = {"segments": [], "full_text": "test"}
        analyzer = CallAnalyzer(asr_model_name="tiny", denoise=False)
        result = analyzer.analyze("audio.wav")
        mock_transcribe.assert_called_once_with(
            "audio.wav", model_name="tiny", denoise=False
        )
        assert result == mock_transcribe.return_value


# ======================== 2. Блочное тестирование analyse ========================


def test_analyze_call_positive(mock_ollama):
    """Б3, Б4, Б5, Б6: Позитивные тесты сентимент-анализа, классификации (пока нет классификации в коде)"""
    transcript = "Клиент: Здравствуйте. Оператор: Добрый день. Клиент: У меня проблема с оплатой."
    result = analyze_call(transcript, model_name="llama3.1:8b")

    assert "dialogue" in result
    assert "assessment" in result
    assert isinstance(result["assessment"]["work_rating"], int)
    assert 1 <= result["assessment"]["work_rating"] <= 10
    assert result["assessment"]["client_mood"] in [
        "позитивное",
        "нейтральное",
        "негативное",
    ]


def test_analyze_call_malformed_json(mock_ollama):
    """Негативный тест: LLM вернула невалидный JSON"""
    mock_ollama.return_value = {"message": {"content": "Извините, я не могу ответить."}}
    with pytest.raises(ValueError, match="Модель не вернула JSON"):
        analyze_call("текст", "model")


def test_analyze_call_extra_text_around_json(mock_ollama):
    """Модель добавила пояснения до/после JSON – должно распарситься корректно"""
    mock_ollama.return_value = {
        "message": {
            "content": 'Вот результат:\n{"dialogue": [], "assessment": {"client_mood": "нейтральное", "overall_rating": "нейтральная", "work_rating": 5, "professionalism": 5, "friendliness": 5, "politeness": 5}}\nКонец.'
        }
    }
    result = analyze_call("текст", "model")
    assert result["assessment"]["work_rating"] == 5


# ======================== 3. Интеграционное тестирование pipeline ========================


def test_process_call_full_pipeline(
    mock_audio_processor, mock_whisper_model, mock_ollama
):
    """И‑1: Полный цикл загрузки и анализа (позитивный)"""
    result = process_call(
        audio_path="call.wav",
        asr_model="base",
        analysis_model="llama3.1:8b",
        denoise=True,
    )

    # проверяем структуру результата
    assert "segments" in result
    assert "dialogue" in result
    assert "assessment" in result
    # ASR-сегменты должны быть те, что вернул whisper
    assert len(result["segments"]) == 2
    # Диалог из LLM
    assert len(result["dialogue"]) == 2
    assert result["assessment"]["client_mood"] == "негативное"


def test_process_call_custom_models(
    mock_audio_processor, mock_whisper_model, mock_ollama
):
    """Проверка передачи параметров моделей в подфункции"""
    with (
        patch("pipeline.transcribe_audio") as mock_transcribe,
        patch("pipeline.analyze_call") as mock_analyze,
    ):
        mock_transcribe.return_value = {"segments": [], "full_text": ""}
        mock_analyze.return_value = {"dialogue": [], "assessment": {}}

        process_call(
            "audio.wav", asr_model="large", analysis_model="llama2", denoise=False
        )

        mock_transcribe.assert_called_once_with(
            "audio.wav", model_name="large", denoise=False
        )
        mock_analyze.assert_called_once_with("", model_name="llama2")


# ======================== 4. Негативные и граничные тесты ========================


def test_transcribe_audio_invalid_file():
    """Б19: недопустимый формат файла (или отсутствующий файл) – должно выбросить исключение"""
    with pytest.raises(
        Exception
    ):  # librosa.load выбросит FileNotFoundError или OSError
        transcribe_audio("nonexistent.xyz")


def test_analyze_call_empty_transcript(mock_ollama):
    """Анализ пустого текста – LLM всё равно должна вернуть структуру (или ошибку)"""
    mock_ollama.return_value = {
        "message": {
            "content": '{"dialogue": [], "assessment": {"client_mood": "нейтральное", "overall_rating": "нейтральная", "work_rating": 5, "professionalism": 5, "friendliness": 5, "politeness": 5}}'
        }
    }
    result = analyze_call("", "model")
    assert result["dialogue"] == []
    assert result["assessment"]["work_rating"] == 5


def test_call_analyzer_denoise_flag():
    """Проверка, что CallAnalyzer передаёт параметр denoise в transcribe_audio"""
    with patch("ASR.transcribe_audio") as mock_transcribe:
        analyzer = CallAnalyzer(asr_model_name="small", denoise=True)
        analyzer.analyze("file.wav")
        mock_transcribe.assert_called_once_with(
            "file.wav", model_name="small", denoise=True
        )

        analyzer2 = CallAnalyzer(denoise=False)
        analyzer2.analyze("file2.wav")
        # второй вызов – другой экземпляр
        assert mock_transcribe.call_count == 2
        # проверяем последний вызов
        mock_transcribe.assert_called_with(
            "file2.wav", model_name="base", denoise=False
        )


# ======================== 5. Запуск тестов ========================
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
