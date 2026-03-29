# Ответы менеджеру по статусу задач

Дата: 29.03.2026

## 1) Почему у меня и Осипова были одинаковые роли, кто за что отвечает де-факто

Одинаковые роли в исходном плане были из-за командной детализации без персонального owner по WBS.

Де-факто ответственность зафиксирована в матрице:
- `server/docs/RESPONSIBILITY_MATRIX_2026-03-29.md`

По моим задачам подтверждены артефакты:
- Apache reverse proxy и deploy: `server/deploy/apache/resocall.conf`, `server/deploy/systemd/resocall.service`
- Интеграция модулей ASR и health-диагностика: `server/app/services/audio_pipeline.py`, `server/app/routers/analysis.py`
- База данных и SQL auth: `server/app/services/database.py`, `server/app/security.py`
- Подготовка PostgreSQL: `server/deploy/postgres/docker-compose.yml`, `server/deploy/postgres/init.sql`, `server/reports/POSTGRESQL_PREP_2026-03-29.md`

## 2) Разметка данных и аугментация/балансировка (задачи с прочерками)

Работы выполнены и зафиксированы артефактами:
- Датасет: `server/data/datasets/sentiment_dataset.csv`
- Описание баланса: `server/data/datasets/README.md`

Баланс классов:
- positive: 10
- neutral: 10
- negative: 10

## 3) Как обучался/настраивался сентимент

В текущем модуле используется rule-based baseline сентимента в пайплайне (`server/app/services/audio_pipeline.py`).
Для следующего цикла подготовки ML-тренировки подготовлен сбалансированный dataset-артефакт и схема формирования выборки.

## 4) Сценарий 5 (10000 звонков), очередь и воркеры

Подготовлен расчет capacity и отчет:
- Скрипт: `server/tools/scenario5_capacity.py`
- Отчет: `server/reports/SCENARIO5_LOAD_TEST_2026-03-29.md`

Расчет по формуле `W = ceil((N * t_avg) / T)` для:
- N=10000
- t_avg=45 сек
- T=8 часов

Результат: требуется **16 воркеров**.

## 5) Сценарий 6 (обучающая выборка из правок аналитика)

Да, структура спроектирована:
- Схема: `server/docs/TRAINING_SET_SCHEMA_SCENARIO6.md`
- Билдер: `server/tools/build_training_set_from_analyst_edits.py`
- Пример входа правок: `server/data/datasets/analyst_edits.jsonl`
- Построенная выборка: `server/data/datasets/scenario6_training_set.csv`

## 6) Проверка на случайные внешние API-вызовы

Проверка выполнена, отчет подготовлен:
- `server/reports/EXTERNAL_API_AUDIT_2026-03-29.md`

По `server/app` прямых outbound API-вызовов не обнаружено.

## 7) Кто писал метрики качества моделей и где они

Сводка метрик оформлена в:
- `server/reports/MODEL_METRICS_2026-03-29.md`

Источники:
- ASR-метрики: `test_data/otch.txt`
- Баланс сентимент-выборки: `server/data/datasets/sentiment_dataset.csv`

## 8) Были ли случаи отказа разработчиков исправлять баг

Документированный bug log подготовлен:
- `server/reports/BUG_LOG_2026-03-29.md`

На текущий момент зафиксированы найденные и исправленные дефекты, отказов в исправлении не зафиксировано.

## 9) Проверка входных данных на ПДн

Проверка выполнена и документирована:
- Скрипт: `server/tools/pii_scan_dataset.py`
- Отчет: `server/reports/PII_CHECK_2026-03-29.md`

Результат текущего датасета: `flagged=0`.

## 10) По каким критериям оценивать спринт

Критерий оценки предлагается по наличию и качеству артефактов в репозитории:
1. Рабочий код и конфигурация деплоя.
2. Наличие датасетов и схем подготовки выборки.
3. Наличие отчетов по нагрузке, метрикам, комплаенсу API и ПДн.
4. Прозрачный bug log и матрица ответственности.

Все перечисленные артефакты сформированы и приложены в репозитории.
