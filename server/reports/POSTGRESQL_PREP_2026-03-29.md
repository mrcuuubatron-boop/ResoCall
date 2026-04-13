# PostgreSQL Preparation Report

Date: 2026-03-29
Owner: Dudenkov S.

## Implemented
1. Added PostgreSQL deployment files:
- `server/deploy/postgres/docker-compose.yml`
- `server/deploy/postgres/init.sql`

2. Added backend PostgreSQL connection settings:
- `RESOCALL_POSTGRES_DSN=...`

3. Implemented PostgreSQL-only DB service:
- `server/app/services/database.py`

4. Wired backend settings to DB service:
- `server/app/dependencies.py`

4. Added diagnostics in health endpoint:
- `db_backend=postgresql`
- `database_ok`

## Verification checklist
- [x] SQL schema for users prepared in PostgreSQL init script
- [x] App runs with PostgreSQL only
- [x] Health endpoint exposes active DB backend and ping status

## Run guide
```bash
cd server/deploy/postgres
docker compose up -d
```
Set in `.env`:
```bash
RESOCALL_POSTGRES_DSN=postgresql://resocall:resocall@127.0.0.1:5432/resocall
```
