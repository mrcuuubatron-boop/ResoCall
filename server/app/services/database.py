import psycopg


class Database:
    def __init__(self, postgres_dsn: str | None = None) -> None:
        self.postgres_dsn = postgres_dsn
        self._init_schema()
        self._seed_demo_users()

    def _connect_pg(self):
        if not self.postgres_dsn:
            raise RuntimeError("RESOCALL_POSTGRES_DSN is required")
        return psycopg.connect(self.postgres_dsn)

    def _init_schema(self) -> None:
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
        with self._connect_pg() as conn:
            with conn.cursor() as cur:
                cur.executemany(
                    "INSERT INTO users(login, password, role) VALUES (%s, %s, %s) ON CONFLICT (login) DO NOTHING",
                    users,
                )
            conn.commit()

    def verify_user(self, login: str, password: str) -> str | None:
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
            with self._connect_pg() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    value = cur.fetchone()
            return value is not None and int(value[0]) == 1
        except Exception:
            return False
