# PostgreSQL Preparation Report

Date: 2026-03-29
Owner: Dudenkov S.

## Implemented
1. Added PostgreSQL deployment files:
- `server/deploy/postgres/docker-compose.yml`
- `server/deploy/postgres/init.sql`

2. Added backend DB backend switch:
- `RESOCALL_DB_BACKEND=sqlite|postgresql`
- `RESOCALL_POSTGRES_DSN=...`

3. Extended DB service to support PostgreSQL and SQLite:
- `server/app/services/database.py`

4. Wired backend settings to DB service:
- `server/app/dependencies.py`

5. Added diagnostics in health endpoint:
- `db_backend`
- `database_ok`

## Verification checklist
- [x] SQL schema for users prepared in PostgreSQL init script
- [x] App can run in SQLite mode
- [x] App has PostgreSQL mode configuration
- [x] Health endpoint exposes active DB backend and ping status

## Run guide
```bash
cd server/deploy/postgres
docker compose up -d
```
Set in `.env`:
```bash
RESOCALL_DB_BACKEND=postgresql
RESOCALL_POSTGRES_DSN=postgresql://resocall:resocall@127.0.0.1:5432/resocall
```
