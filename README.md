# ResoCall

ResoCall — проект по ТППО, направленный на анализ Call-центра с помощью ИИ.

## Структура проекта

```
ResoCall/
├── core/           # Ядро: бизнес-логика, модели данных, аудио-обработка, анализ
├── backend/        # REST API сервер (FastAPI)
├── frontend/       # Веб-интерфейс (HTML/CSS/JS)
└── gui/            # Десктопный GUI (Tkinter)
```

## Модули

### `core/`
Общее ядро приложения:
- `models/`   — Pydantic-модели данных (звонки, агенты, аналитика)
- `audio/`    — Обработка аудио (транскрибация, VAD)
- `analysis/` — Анализ звонков (тональность, ключевые слова, метрики)

### `backend/`
FastAPI-сервер с REST API:
- `app/api/`      — Эндпоинты (звонки, агенты, отчёты)
- `app/models/`   — Схемы запросов/ответов
- `app/services/` — Сервисный слой (интеграция с `core`)

### `frontend/`
Веб-дашборд для просмотра аналитики звонков в браузере:
- `public/`       — Статика (index.html)
- `src/components/` — UI-компоненты
- `src/pages/`    — Страницы дашборда

### `gui/`
Десктопное GUI-приложение (Tkinter):
- `views/`   — Окна приложения
- `widgets/` — Переиспользуемые виджеты

## Быстрый старт

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### GUI
```bash
cd gui
python main.py
```

### Frontend
Откройте `frontend/public/index.html` в браузере или запустите через любой статический сервер.
