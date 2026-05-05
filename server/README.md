# ResoCall Server

Бэкенд `ResoCall` — это FastAPI-сервис для:

- аутентификации пользователей;
- загрузки и обработки аудиофайлов;
- управления задачами анализа;
- хранения и выдачи результатов;
- мониторинга состояния сервера и операций с файлами.

## Что внутри сервера

Основные блоки:

- `app/main.py`: создание FastAPI-приложения, подключение middleware и роутеров.
- `app/dependencies.py`: сборка контекста приложения (`settings`, `storage`, `db`, `tasks`, pipeline).
- `app/services/database.py`: работа с PostgreSQL (пользователи, метаданные загрузок).
- `app/services/storage.py`: файловое хранилище (`uploads`, `results`, `logs`) и JSON-настройки.
- `app/services/task_manager.py`: очередь и статусы задач (`queued/processing/done/failed`).
- `app/services/audio_pipeline.py`: ASR/анализ, формирование результата.
- `app/routers/*.py`: API-эндпоинты (`auth`, `analysis`, `module_settings`, `monitor`, `storage_admin`).

## Как сервер работает (поток данных)

1. Клиент проходит вход (`/api/v1/auth/login`).
2. Клиент загружает аудио на анализ (`/api/v1/analysis/upload-and-analyze`) или напрямую в storage (`/api/v1/storage/upload`).
3. Файл сохраняется в `data/uploads` или `data/results`.
4. Для upload-операций метаданные пишутся в PostgreSQL (`uploads`).
5. Аналитическая задача попадает в очередь (`TaskManager`) и обрабатывается worker'ами.
6. Результат анализа сохраняется в `data/results/<task_id>.json`.
7. Монитор (`/docs`) показывает состояние задач, процесса, запросов и storage.

## Быстрый запуск (локально)

```bash
cd server
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Сервис будет доступен по адресу:

- `http://127.0.0.1:8000`
- монитор: `http://127.0.0.1:8000/docs`

## Основные команды для работы

### 1) Проверка состояния сервера

```bash
curl http://127.0.0.1:8000/api/v1/health
```

### 2) Логин

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"login":"engineer","password":"engineer"}'
```

Демо-пользователи:

- `admin/admin`
- `engineer/engineer`
- `user/user`

### 3) Запуск анализа аудио

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/analysis/upload-and-analyze" \
  -H "x-login: engineer" \
  -H "x-password: engineer" \
  -F "file=@/path/to/call.wav" \
  -F 'required_phrases=["здравствуйте","до свидания"]'
```

### 4) Проверка задач и результатов

```bash
curl -H "x-login: engineer" -H "x-password: engineer" "http://127.0.0.1:8000/api/v1/tasks"
curl -H "x-login: engineer" -H "x-password: engineer" "http://127.0.0.1:8000/api/v1/tasks/<task_id>"
curl -H "x-login: engineer" -H "x-password: engineer" "http://127.0.0.1:8000/api/v1/results/<task_id>"
```

## Storage/Admin API (загрузка, просмотр, удаление)

Эти эндпоинты защищены (роль `admin` или `engineer`).

Поддерживаемые способы аутентификации:

- заголовки `x-login` + `x-password`;
- или Basic Auth (`-u login:password` в `curl`).

### Список файлов

```bash
curl -u engineer:engineer "http://localhost:8000/api/v1/storage/files?which=uploads"
```

`which`:

- `uploads`
- `results`
- `logs`

### Загрузка файла

```bash
curl -u engineer:engineer \
  -F file=@/path/to/call.wav \
  -F area=uploads \
  "http://localhost:8000/api/v1/storage/upload"
```

### Скачивание файла

```bash
curl -u engineer:engineer -OJ "http://localhost:8000/api/v1/storage/download?which=uploads&name=call.wav"
```

### Удаление физического файла (A)

```bash
curl -X DELETE -u engineer:engineer \
  "http://localhost:8000/api/v1/storage/file?which=uploads&name=call.wav"
```

### Метаданные загрузок (B)

```bash
curl -u engineer:engineer \
  "http://localhost:8000/api/v1/storage/uploads?include_deleted=true&limit=50&offset=0"
```

Фильтры:

- `area=uploads|results|logs`
- `uploader=<login>`
- `include_deleted=true|false`
- `limit`, `offset`

### Soft-delete по записи upload (B)

```bash
curl -X POST -u engineer:engineer \
  "http://localhost:8000/api/v1/storage/uploads/123/soft-delete"
```

Soft-delete + удаление физического файла:

```bash
curl -X POST -u engineer:engineer \
  "http://localhost:8000/api/v1/storage/uploads/123/soft-delete?purge_file=true"
```

## База данных (PostgreSQL)

Сервер использует PostgreSQL для аутентификации и метаданных storage.

Переменная окружения:

```bash
RESOCALL_POSTGRES_DSN=postgresql://resocall:resocall@127.0.0.1:5432/resocall
```

Таблицы:

- `users(login, password, role)`
- `uploads(id, name, area, size, uploader, uploaded_at, deleted_at, deleted_by)`

Проверка метаданных в БД:

```bash
psql "$RESOCALL_POSTGRES_DSN" \
  -c "SELECT id,name,area,size,uploader,uploaded_at,deleted_at,deleted_by FROM uploads ORDER BY uploaded_at DESC LIMIT 50;"
```

## Как сохраняются данные и почему они не теряются после рестарта

Постоянные данные:

- Файлы: `data/uploads`, `data/results`, `data/logs`.
- Метаданные загрузок: PostgreSQL, таблица `uploads`.
- Пользователи/роли: PostgreSQL, таблица `users`.

На старте приложения вызывается `db.init()`:

- таблицы создаются, если отсутствуют;
- демо-пользователи добавляются только если их еще нет.

Итог: после перезапуска сервера файлы и записи в БД остаются доступными.

## Подготовка PostgreSQL через Docker

```bash
cd server/deploy/postgres
docker compose up -d
```

SQL-инициализация находится в:

- `deploy/postgres/init.sql`

## Преимущества сервера

- Простая архитектура: легко развернуть и поддерживать.
- Прозрачный мониторинг: `/docs` показывает задачи, запросы, загрузки и состояние процесса.
- Надежное хранение: файлы на диске + метаданные в PostgreSQL.
- Безопасность для admin/storage операций: role-based доступ (`admin`/`engineer`).
- Гибкий API: можно автоматизировать загрузку, аналитику, выгрузку и аудит.
- Отказоустойчивость ASR: возможен fallback между внешним и внутренним пайплайном.

## Полезные файлы деплоя

- `deploy/apache/resocall.conf` — reverse proxy для Apache.
- `deploy/systemd/resocall.service` — systemd unit для backend.
- `deploy/postgres/docker-compose.yml` — локальный PostgreSQL.

## Краткий чек-лист перед эксплуатацией

1. Запустить PostgreSQL и проверить `RESOCALL_POSTGRES_DSN`.
2. Запустить backend и проверить `/api/v1/health`.
3. Проверить логин и роль.
4. Проверить upload/download/delete в storage.
5. Открыть `/docs` и убедиться, что монитор показывает актуальные данные.
