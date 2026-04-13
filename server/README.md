# ResoCall Voice Server

Бэкенд-сервис для загрузки и анализа аудиозвонков.

## Что реализовано

- FastAPI API для загрузки файлов и асинхронной обработки.
- ASR-пайплайн (Whisper), базовая оценка тональности и проверка скрипта.
- Оценка категории и приоритета обращения.
- Жизненный цикл задач: `queued -> processing -> done/failed`.
- Простая аутентификация под демо-роли интерфейса.

## API

- `POST /api/v1/auth/login` - проверка логина/пароля и возврат роли.
- `POST /api/v1/analysis/upload-and-analyze` - загрузка `.wav`/`.mp3` и запуск анализа.
- `GET /api/v1/tasks` - список задач.
- `GET /api/v1/tasks/{task_id}` - статус задачи.
- `GET /api/v1/results/{task_id}` - результат анализа.
- `GET /api/v1/modules/{module_key}/settings` - получить сохраненные настройки модуля для текущего пользователя.
- `PUT /api/v1/modules/{module_key}/settings` - сохранить настройки модуля для текущего пользователя.
- `GET /api/v1/health` - проверка состояния сервиса.

Swagger UI доступен по адресу `/docs`.

## Локальный запуск

```bash
cd server
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## База данных (PostgreSQL)

Сервер работает только с PostgreSQL для SQL-запросов аутентификации.

Переменная подключения:

- `RESOCALL_POSTGRES_DSN=postgresql://resocall:resocall@127.0.0.1:5432/resocall`

Таблица пользователей:

- `users(login, password, role)`

Endpoint входа `POST /api/v1/auth/login` проверяет данные через SQL-запрос в выбранной БД.
Endpoint входа `POST /api/v1/auth/login` проверяет данные через SQL-запрос в PostgreSQL.

### Подготовка PostgreSQL

Готовые артефакты:

- `deploy/postgres/docker-compose.yml`
- `deploy/postgres/init.sql`

Запуск локального PostgreSQL:

```bash
cd server/deploy/postgres
docker compose up -d
```

Далее в `.env`:

```bash
RESOCALL_POSTGRES_DSN=postgresql://resocall:resocall@127.0.0.1:5432/resocall
```

Проверка состояния БД через health:

```bash
curl http://127.0.0.1/api/v1/health
```

В ответе должны быть поля:

- `db_backend: postgresql` - активный backend БД.
- `database_ok: true` - SQL-запрос `SELECT 1` выполнился успешно.

## Примеры запросов

Вход:

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"login":"engineer","password":"engineer"}'
```

Демо-учетки:

- `admin/admin`
- `engineer/engineer`
- `user/user`

Защищенные endpoint'ы требуют заголовки:

- `x-login`
- `x-password`

Запуск анализа:

```bash
curl -X POST "http://localhost:8000/api/v1/analysis/upload-and-analyze" \
  -H "x-login: engineer" \
  -H "x-password: engineer" \
  -F "file=@/path/to/call.wav" \
  -F 'required_phrases=["здравствуйте","до свидания"]'
```

Проверка статуса и получение результата:

```bash
curl -H "x-login: engineer" -H "x-password: engineer" "http://localhost:8000/api/v1/tasks/<task_id>"
curl -H "x-login: engineer" -H "x-password: engineer" "http://localhost:8000/api/v1/results/<task_id>"

Настройки модулей (пример для модуля `engineer`):

```bash
curl -H "x-login: engineer" -H "x-password: engineer" "http://localhost:8000/api/v1/modules/engineer/settings"
curl -X PUT "http://localhost:8000/api/v1/modules/engineer/settings" \
  -H "Content-Type: application/json" \
  -H "x-login: engineer" \
  -H "x-password: engineer" \
  -d '{"settings":{"period":"week","sortBy":"date"}}'
```
```

## Подключение через Apache (Reverse Proxy)

Цель: отдать проект через один публичный вход Apache и проксировать маршруты:

- `/api/*` -> FastAPI (`127.0.0.1:8000`)
- `/` -> Next.js (`127.0.0.1:3000`)

Готовые файлы в репозитории:

- `deploy/apache/resocall.conf`
- `deploy/systemd/resocall.service`

### 1) Поднять backend как systemd-сервис

```bash
cd server
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
sudo cp deploy/systemd/resocall.service /etc/systemd/system/resocall.service
sudo systemctl daemon-reload
sudo systemctl enable --now resocall
sudo systemctl status resocall
```

Важно:

- В `deploy/systemd/resocall.service` пользователь сейчас `www-data`.
- Если директория проекта принадлежит другому пользователю, дайте права чтения/запуска или поменяйте `User`/`Group`.

### 2) Включить reverse proxy в Apache

```bash
sudo a2enmod proxy proxy_http headers rewrite
sudo cp deploy/apache/resocall.conf /etc/apache2/sites-available/resocall.conf
sudo a2ensite resocall.conf
sudo systemctl reload apache2
```

При необходимости отключите дефолтный сайт:

```bash
sudo a2dissite 000-default.conf
sudo systemctl reload apache2
```

### 3) Проверить маршрутизацию через Apache

```bash
curl http://127.0.0.1/api/v1/health
curl http://127.0.0.1/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login":"engineer","password":"engineer"}'
```

Если эти запросы работают через порт Apache, значит reverse proxy настроен корректно.

Проверка статуса межмодульной интеграции (внешний ASR):

```bash
curl http://127.0.0.1/api/v1/health
```

Ключевые поля в ответе:

- `database_ok`: доступна ли БД и выполняется ли SQL-запрос.
- `external_asr_enabled`: включен ли режим внешнего модуля.
- `external_asr_status`: `active`, `disabled`, `unavailable`, `runtime_failed`.
- `external_asr_error`: текст последней ошибки (если есть).

## Связь модулей между собой (ASR bridge)

Сервер поддерживает 2 режима работы ASR:

- Внутренний: собственный пайплайн в `app/services/audio_pipeline.py`.
- Внешний: подключение модуля `../ASR/ASR.py` и вызов класса `CallAnalyzer`.

Настройки в `.env`:

- `RESOCALL_EXTERNAL_ASR_MODULE=true` - включить внешний ASR-модуль.
- `RESOCALL_ASR_MODULE_PATH=../ASR/ASR.py` - путь до файла внешнего модуля.

Логика отказоустойчивости:

- При недоступности/ошибке внешнего модуля сервер автоматически переключается на внутренний ASR-пайплайн.
- Это позволяет API продолжать работу даже при сбое внешней части.

## Примечания по эксплуатации

- Диаризация сейчас заглушка (`speaker=unknown`).
- Классификация и тональность реализованы эвристически; для продакшена лучше заменить на ML-модели.
- При ошибке обработки исходный файл остается в `data/uploads`, а описание ошибки пишется в `data/logs`.
