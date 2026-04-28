#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_DIR="$ROOT_DIR/server"
SITE_DIR="$ROOT_DIR/site"

if [[ ! -d "$SERVER_DIR" ]]; then
  echo "[error] server directory not found: $SERVER_DIR" >&2
  exit 1
fi

if [[ ! -d "$SITE_DIR" ]]; then
  echo "[error] site directory not found: $SITE_DIR" >&2
  exit 1
fi

pick_python_with_uvicorn() {
  local candidate="$1"
  if [[ -x "$candidate" ]] && "$candidate" -c "import uvicorn" >/dev/null 2>&1; then
    echo "$candidate"
    return 0
  fi
  return 1
}

if BACKEND_PYTHON="$(pick_python_with_uvicorn "$SERVER_DIR/.venv/bin/python")"; then
  :
elif BACKEND_PYTHON="$(pick_python_with_uvicorn "$ROOT_DIR/.venv/bin/python")"; then
  :
elif command -v python3 >/dev/null 2>&1 && python3 -c "import uvicorn" >/dev/null 2>&1; then
  BACKEND_PYTHON="python3"
else
  echo "[error] uvicorn is not installed in server/.venv, .venv, or system python3" >&2
  echo "[hint] Install backend deps: cd server && python -m pip install -r requirements.txt" >&2
  exit 1
fi

if command -v pnpm >/dev/null 2>&1; then
  FRONT_CMD=(pnpm dev)
else
  FRONT_CMD=(npm run dev)
fi

BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
  echo
  echo "[stop] Stopping services..."

  if [[ -n "$BACKEND_PID" ]] && kill -0 "$BACKEND_PID" >/dev/null 2>&1; then
    kill "$BACKEND_PID" >/dev/null 2>&1 || true
  fi

  if [[ -n "$FRONTEND_PID" ]] && kill -0 "$FRONTEND_PID" >/dev/null 2>&1; then
    kill "$FRONTEND_PID" >/dev/null 2>&1 || true
  fi

  wait || true
  echo "[done] Services stopped"
}

trap cleanup INT TERM EXIT

echo "[start] Backend: http://127.0.0.1:8000"
(
  cd "$SERVER_DIR"
  exec "$BACKEND_PYTHON" -m uvicorn app.main:app --host 0.0.0.0 --port 8000
) &
BACKEND_PID=$!

echo "[start] Frontend: http://127.0.0.1:3000"
(
  cd "$SITE_DIR"
  exec "${FRONT_CMD[@]}"
) &
FRONTEND_PID=$!

echo "[info] Press Ctrl+C to stop both services"

wait -n "$BACKEND_PID" "$FRONTEND_PID"
echo "[warn] One of services exited, stopping the other..."
