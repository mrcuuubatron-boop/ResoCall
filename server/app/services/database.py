import sqlite3
from pathlib import Path


class Database:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()
        self._seed_demo_users()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
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

    def _seed_demo_users(self) -> None:
        users = [
            ("admin", "admin", "admin"),
            ("engineer", "engineer", "engineer"),
            ("user", "user", "user"),
        ]
        with self._connect() as conn:
            conn.executemany(
                "INSERT OR IGNORE INTO users(login, password, role) VALUES (?, ?, ?)",
                users,
            )
            conn.commit()

    def verify_user(self, login: str, password: str) -> str | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT role FROM users WHERE login = ? AND password = ?",
                (login, password),
            ).fetchone()
        if row is None:
            return None
        return str(row["role"])

    def ping(self) -> bool:
        try:
            with self._connect() as conn:
                value = conn.execute("SELECT 1 AS ok").fetchone()
            return value is not None and int(value["ok"]) == 1
        except Exception:
            return False
