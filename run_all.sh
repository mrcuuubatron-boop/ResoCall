#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_DIR="$ROOT_DIR/server"
SITE_DIR="$ROOT_DIR/site"
SERVER_VENV_DIR="$SERVER_DIR/.venv"
SERVER_PYTHON="$SERVER_VENV_DIR/bin/python"
LOCK_FILE="$SITE_DIR/.next/dev/lock"
POSTGRES_COMPOSE_DIR="$SERVER_DIR/deploy/postgres"

if [[ ! -d "$SERVER_DIR" ]]; then
  echo "[error] server directory not found: $SERVER_DIR" >&2
  exit 1
fi

if [[ ! -d "$SITE_DIR" ]]; then
  echo "[error] site directory not found: $SITE_DIR" >&2
  exit 1
fi

ensure_backend_env() {
  if [[ ! -f "$SERVER_DIR/requirements.txt" ]]; then
    echo "[error] backend requirements not found: $SERVER_DIR/requirements.txt" >&2
    exit 1
  fi

  local needs_install=0
  if [[ ! -x "$SERVER_PYTHON" ]] || ! "$SERVER_PYTHON" -c "import uvicorn" >/dev/null 2>&1; then
    needs_install=1
  elif ! "$SERVER_PYTHON" -m pip check >/dev/null 2>&1; then
    needs_install=1
  fi

  if [[ "$needs_install" -eq 1 ]]; then
    if ! command -v python3 >/dev/null 2>&1; then
      echo "[error] python3 is required to create the backend virtualenv" >&2
      exit 1
    fi

    echo "[setup] Preparing backend virtualenv"
    python3 -m venv "$SERVER_VENV_DIR"
    "$SERVER_PYTHON" -m pip install --upgrade pip >/dev/null
    "$SERVER_PYTHON" -m pip install -r "$SERVER_DIR/requirements.txt"
  fi
}

ensure_frontend_deps() {
  if [[ ! -f "$SITE_DIR/package.json" ]]; then
    echo "[error] frontend package.json not found: $SITE_DIR/package.json" >&2
    exit 1
  fi

  if [[ ! -d "$SITE_DIR/node_modules" ]]; then
    echo "[setup] Installing frontend dependencies"
    if command -v pnpm >/dev/null 2>&1; then
      (cd "$SITE_DIR" && pnpm install --frozen-lockfile)
    elif command -v npm >/dev/null 2>&1; then
      (cd "$SITE_DIR" && npm install)
    else
      echo "[error] pnpm or npm is required to install frontend dependencies" >&2
      exit 1
    fi
  fi
}

ensure_postgres() {
  if ss -ltn 2>/dev/null | grep -q ':5432 '; then
    return 0
  fi

  if [[ -f "$POSTGRES_COMPOSE_DIR/docker-compose.yml" ]]; then
    if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
      echo "[setup] Starting PostgreSQL via Docker Compose"
      (cd "$POSTGRES_COMPOSE_DIR" && docker compose up -d)
    elif command -v docker-compose >/dev/null 2>&1; then
      echo "[setup] Starting PostgreSQL via docker-compose"
      (cd "$POSTGRES_COMPOSE_DIR" && docker-compose up -d)
    else
      echo "[error] PostgreSQL is not running on 127.0.0.1:5432 and Docker Compose is not available" >&2
      echo "[hint] Install Docker or start PostgreSQL manually using server/deploy/postgres/docker-compose.yml" >&2
      exit 1
    fi

    for _ in $(seq 1 30); do
      if ss -ltn 2>/dev/null | grep -q ':5432 '; then
        return 0
      fi
      sleep 1
    done

    echo "[error] PostgreSQL did not become ready on 127.0.0.1:5432" >&2
    exit 1
  fi

  echo "[error] PostgreSQL is not running on 127.0.0.1:5432 and docker compose file is missing" >&2
  exit 1
}

ensure_postgres
ensure_backend_env
ensure_frontend_deps

BACKEND_PYTHON="$SERVER_PYTHON"

if command -v pnpm >/dev/null 2>&1; then
  # Turbopack can panic on some Linux setups/paths; force stable webpack dev server.
  FRONT_CMD=(pnpm exec next dev --webpack)
else
  # Same fallback for npm to avoid Turbopack runtime crashes.
  FRONT_CMD=(npx next dev --webpack)
fi

rm -f "$LOCK_FILE"

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
