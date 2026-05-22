import logging

# Фикстура для логирования в файл
import pytest

@pytest.fixture(autouse=True)
def log_test(request):
    log_path = os.environ.get("RESOCALL_TEST_LOG", "test_log.txt")
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_path, encoding="utf-8")
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    # Удаляем старые хендлеры, чтобы не дублировать логи
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(handler)
    # Явный print для вывода в терминал (pytest может перехватывать stdout, но print всегда работает с -s)
    print(f"START {request.node.name}")
    logger.info(f"START {request.node.name}")
    yield
    print(f"END {request.node.name}")
    logger.info(f"END {request.node.name}")
    logger.removeHandler(handler)

# Автоматизированные тесты для backend ResoCall
# (на основе плана тестирования)

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
from app.services.audio_pipeline import PipelineConfig, ProcessingPipeline
from app.services.call_store import CallStore
from app.config import Settings

# Тесты для сентимент-анализа
def test_simple_sentiment_positive():
    pipeline = ProcessingPipeline(PipelineConfig())
    label, score = pipeline._simple_sentiment("Спасибо, вы мне очень помогли!")
    logging.getLogger("test_logger").info(f"label={label}, score={score}")
    print(f"test_simple_sentiment_positive: label={label}, score={score}")
    assert label == "positive"
    assert score >= 0.7

def test_simple_sentiment_negative():
    pipeline = ProcessingPipeline(PipelineConfig())
    label, score = pipeline._simple_sentiment("Это безобразие, я буду жаловаться!")
    logging.getLogger("test_logger").info(f"label={label}, score={score}")
    print(f"test_simple_sentiment_negative: label={label}, score={score}")
    assert label == "negative"
    assert score >= 0.6

# Тесты для классификации проблем
def test_classify_issue_billing():
    pipeline = ProcessingPipeline(PipelineConfig())
    cat = pipeline._classify_category("У меня не списались деньги за подписку")
    logging.getLogger("test_logger").info(f"cat={cat}")
    print(f"test_classify_issue_billing: cat={cat}")
    assert cat == "consultation"

def test_classify_issue_tech():
    pipeline = ProcessingPipeline(PipelineConfig())
    cat = pipeline._classify_category("Не работает программа, выдает ошибку 151")
    logging.getLogger("test_logger").info(f"cat={cat}")
    print(f"test_classify_issue_tech: cat={cat}")
    assert cat == "technical_support"

def test_classify_issue_other():
    pipeline = ProcessingPipeline(PipelineConfig())
    cat = pipeline._classify_category("Здравствуйте, как ваши дела?")
    logging.getLogger("test_logger").info(f"cat={cat}")
    print(f"test_classify_issue_other: cat={cat}")
    assert cat == "consultation"

# Тесты для проверки скриптов
def test_script_check_greeting():
    pipeline = ProcessingPipeline(PipelineConfig())
    phrases = ["добрый день", "чем могу помочь"]
    transcript = "Добрый день, компания 'Ромашка', меня зовут Иван, чем я могу вам помочь?"
    result = pipeline._script_check(transcript, phrases)
    logging.getLogger("test_logger").info(f"found_phrases={result.found_phrases}, compliance_pct={result.compliance_pct}")
    print(f"test_script_check_greeting: found_phrases={result.found_phrases}, compliance_pct={result.compliance_pct}")
    assert "добрый день" in result.found_phrases
    assert result.compliance_pct == 50.0

def test_script_check_greeting_missing():
    pipeline = ProcessingPipeline(PipelineConfig())
    phrases = ["добрый день", "чем могу помочь"]
    transcript = "Слушаю вас"
    result = pipeline._script_check(transcript, phrases)
    logging.getLogger("test_logger").info(f"found_phrases={result.found_phrases}, compliance_pct={result.compliance_pct}")
    print(f"test_script_check_greeting_missing: found_phrases={result.found_phrases}, compliance_pct={result.compliance_pct}")
    assert result.compliance_pct == 0.0

# Тесты для приоритизации
def test_priority_high():
    pipeline = ProcessingPipeline(PipelineConfig())
    score = pipeline._priority("У меня срочная проблема, всё сломалось, помогите пожалуйста!", "negative", "complaint")
    assert score >= 4

def test_priority_low():
    pipeline = ProcessingPipeline(PipelineConfig())
    score = pipeline._priority("Хотел бы уточнить режим работы офиса", "neutral", "consultation")
    assert score == 1

# Тесты для CallStore (CRUD сотрудников и клиентов)
def test_create_and_delete_employee(tmp_path):
    settings = Settings()
    settings.data_dir = tmp_path
    store = CallStore(settings)
    emp = store.create_employee("Тестовый Сотрудник", "Оператор")
    assert emp["name"] == "Тестовый Сотрудник"
    assert store.delete_employee(emp["id"])

def test_create_and_delete_client(tmp_path):
    settings = Settings()
    settings.data_dir = tmp_path
    store = CallStore(settings)
    client = store.create_client("Тестовый Клиент", "+7 999 000-00-00")
    assert client["name"] == "Тестовый Клиент"
    assert store.delete_client(client["id"])

# Тест создания звонка
def test_create_and_get_call(tmp_path):
    settings = Settings()
    settings.data_dir = tmp_path
    store = CallStore(settings)
    emp = store.create_employee("Оператор", "Оператор")
    client = store.create_client("Клиент", "+7 900 000-00-00")
    call = store.create_call({
        "employee_id": emp["id"],
        "client_id": client["id"],
        "duration": 60,
        "transcript": [],
    })
    assert call["employeeId"] == emp["id"]
    assert call["clientId"] == client["id"]
    got = store.get_call(call["id"])
    assert got is not None
