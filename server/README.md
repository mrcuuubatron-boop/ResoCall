# ResoCall Voice Server

Separate backend segment for call audio processing.

## What is implemented

- FastAPI service for audio upload and async processing.
- ASR pipeline (Whisper), simple sentiment, script compliance check.
- Category and priority estimation for call tickets.
- Task lifecycle API: queued -> processing -> done/failed.
- Minimal verification like current site demo users.

## API

- `POST /api/v1/auth/login` - verify login/password and return role.
- `POST /api/v1/analysis/upload-and-analyze` - upload `.wav` or `.mp3`, start processing.
- `GET /api/v1/tasks` - list tasks.
- `GET /api/v1/tasks/{task_id}` - task status.
- `GET /api/v1/results/{task_id}` - analysis result payload.
- `GET /api/v1/health` - service health.

Swagger UI is available at `/docs`.

## Run

```bash
cd server
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Example request

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"login":"engineer","password":"engineer"}'
```

Demo credentials are the same as in site UI:

- `admin/admin`
- `engineer/engineer`
- `user/user`

Protected endpoints require headers:

- `x-login`
- `x-password`

```bash
curl -X POST "http://localhost:8000/api/v1/analysis/upload-and-analyze" \
  -H "x-login: engineer" \
  -H "x-password: engineer" \
  -F "file=@/path/to/call.wav" \
  -F 'required_phrases=["здравствуйте","до свидания"]'
```

Then poll:

```bash
curl -H "x-login: engineer" -H "x-password: engineer" "http://localhost:8000/api/v1/tasks/<task_id>"
curl -H "x-login: engineer" -H "x-password: engineer" "http://localhost:8000/api/v1/results/<task_id>"
```

## Notes

- Current diarization is a placeholder (`speaker=unknown`).
- Sentiment and ticket classification are lightweight heuristics; replace with production ML models.
- In case of processing error, source file is kept in `data/uploads`, and an error log is written to `data/logs`.
