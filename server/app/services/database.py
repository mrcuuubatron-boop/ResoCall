import sqlite3
from pathlib import Path

import psycopg


class Database:
    def __init__(self, db_path: Path, backend: str = "sqlite", postgres_dsn: str | None = None) -> None:
        self.db_path = db_path
        self.backend = backend.strip().lower()
        self.postgres_dsn = postgres_dsn
        if self.backend == "sqlite":
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        elif self.backend != "postgresql":
            raise ValueError("RESOCALL_DB_BACKEND must be 'sqlite' or 'postgresql'")
        self._init_schema()
        self._seed_demo_users()

    def _connect(self) -> sqlite3.Connection:
        if self.backend != "sqlite":
            raise RuntimeError("SQLite connection requested while backend is not sqlite")
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _connect_pg(self):
        if self.backend != "postgresql":
            raise RuntimeError("PostgreSQL connection requested while backend is not postgresql")
        if not self.postgres_dsn:
            raise RuntimeError("RESOCALL_POSTGRES_DSN is required for postgresql backend")
        return psycopg.connect(self.postgres_dsn)

    def _init_schema(self) -> None:
        if self.backend == "sqlite":
            with self._connect() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        login TEXT PRIMARY KEY,
                        password TEXT NOT NULL,
                        role TEXT NOT NULL
                    )
                    """
                )
                conn.commit()
            return

        with self._connect_pg() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        login TEXT PRIMARY KEY,
                        password TEXT NOT NULL,
                        role TEXT NOT NULL
                    )
                    """
                )
            conn.commit()

    def _seed_demo_users(self) -> None:
        users = [
            ("admin", "admin", "admin"),
            ("engineer", "engineer", "engineer"),
            ("user", "user", "user"),
        ]
        if self.backend == "sqlite":
            with self._connect() as conn:
                conn.executemany(
                    "INSERT OR IGNORE INTO users(login, password, role) VALUES (?, ?, ?)",
                    users,
                )
                conn.commit()
            return

        with self._connect_pg() as conn:
            with conn.cursor() as cur:
                cur.executemany(
                    "INSERT INTO users(login, password, role) VALUES (%s, %s, %s) ON CONFLICT (login) DO NOTHING",
                    users,
                )
            conn.commit()

    def verify_user(self, login: str, password: str) -> str | None:
        if self.backend == "sqlite":
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT role FROM users WHERE login = ? AND password = ?",
                    (login, password),
                ).fetchone()
            if row is None:
                return None
            return str(row["role"])

        with self._connect_pg() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT role FROM users WHERE login = %s AND password = %s",
                    (login, password),
                )
                row = cur.fetchone()
        if row is None:
            return None
        return str(row[0])

    def ping(self) -> bool:
        try:
            if self.backend == "sqlite":
                with self._connect() as conn:
                    value = conn.execute("SELECT 1 AS ok").fetchone()
                return value is not None and int(value["ok"]) == 1

            with self._connect_pg() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    value = cur.fetchone()
            return value is not None and int(value[0]) == 1
        except Exception:
            return False
