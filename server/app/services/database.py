import psycopg


class Database:
    def __init__(self, postgres_dsn: str | None = None) -> None:
        self.postgres_dsn = postgres_dsn
        # demo users: map login -> (password, role)
        self._demo_users: dict[str, tuple[str, str]] = {
            "admin": ("admin", "admin"),
            "engineer": ("engineer", "engineer"),
            "user": ("user", "user"),
        }

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
                # uploads metadata table
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS uploads (
                        id SERIAL PRIMARY KEY,
                        name TEXT NOT NULL,
                        area TEXT NOT NULL,
                        size BIGINT NOT NULL,
                        uploader TEXT,
                        uploaded_at TIMESTAMPTZ DEFAULT now(),
                        deleted_at TIMESTAMPTZ,
                        deleted_by TEXT
                    )
                    """
                )
                # Backward-compatible schema upgrades for existing deployments.
                cur.execute("ALTER TABLE uploads ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ")
                cur.execute("ALTER TABLE uploads ADD COLUMN IF NOT EXISTS deleted_by TEXT")
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
        # Check demo users first (fast, in-memory)
        demo = self._demo_users.get(login)
        if demo is not None:
            if demo[0] == password:
                return demo[1]
            return None

        # Fallback to DB lookup (best-effort). Returns role if valid.
        try:
            with self._connect_pg() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT role FROM users WHERE login = %s AND password = %s", (login, password))
                    row = cur.fetchone()
                    if row:
                        return row[0]
        except Exception:
            # if DB unavailable, be conservative and deny auth
            return None
        return None

    def ping(self) -> bool:
        return True

    def init(self) -> None:
        """Initialize schema and seed demo users if possible. Best-effort.

        Called at application startup so that the DB contains expected tables.
        Exceptions are swallowed to keep the app resilient when the DB is down.
        """
        try:
            self._init_schema()
            self._seed_demo_users()
        except Exception:
            # don't crash startup if DB isn't reachable
            return

    def list_users(self) -> list[dict[str, str]]:
        """Return a list of users from the `users` table.

        This is a thin wrapper around a simple SELECT; if the DB is
        unavailable an empty list is returned.
        """
        try:
            with self._connect_pg() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT login, role FROM users")
                    rows = cur.fetchall()
        except Exception:
            return []
        return [{"login": r[0], "role": r[1]} for r in rows]

    def record_upload(self, name: str, area: str, size: int, uploader: str | None = None) -> None:
        try:
            with self._connect_pg() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO uploads (name, area, size, uploader) VALUES (%s, %s, %s, %s)",
                        (name, area, size, uploader),
                    )
                conn.commit()
        except Exception:
            # best-effort: don't fail uploads if DB can't record metadata
            return

    def list_uploads(
        self,
        area: str | None = None,
        limit: int = 200,
        offset: int = 0,
        include_deleted: bool = False,
        uploader: str | None = None,
    ) -> list[dict[str, object]]:
        try:
            with self._connect_pg() as conn:
                with conn.cursor() as cur:
                    # Keep SQL strings literal for psycopg static typing checks.
                    if area and uploader and not include_deleted:
                        cur.execute(
                            "SELECT id, name, area, size, uploader, uploaded_at, deleted_at, deleted_by FROM uploads WHERE area = %s AND uploader = %s AND deleted_at IS NULL ORDER BY uploaded_at DESC LIMIT %s OFFSET %s",
                            (area, uploader, limit, offset),
                        )
                    elif area and uploader and include_deleted:
                        cur.execute(
                            "SELECT id, name, area, size, uploader, uploaded_at, deleted_at, deleted_by FROM uploads WHERE area = %s AND uploader = %s ORDER BY uploaded_at DESC LIMIT %s OFFSET %s",
                            (area, uploader, limit, offset),
                        )
                    elif area and not include_deleted:
                        cur.execute(
                            "SELECT id, name, area, size, uploader, uploaded_at, deleted_at, deleted_by FROM uploads WHERE area = %s AND deleted_at IS NULL ORDER BY uploaded_at DESC LIMIT %s OFFSET %s",
                            (area, limit, offset),
                        )
                    elif area and include_deleted:
                        cur.execute(
                            "SELECT id, name, area, size, uploader, uploaded_at, deleted_at, deleted_by FROM uploads WHERE area = %s ORDER BY uploaded_at DESC LIMIT %s OFFSET %s",
                            (area, limit, offset),
                        )
                    elif uploader and not include_deleted:
                        cur.execute(
                            "SELECT id, name, area, size, uploader, uploaded_at, deleted_at, deleted_by FROM uploads WHERE uploader = %s AND deleted_at IS NULL ORDER BY uploaded_at DESC LIMIT %s OFFSET %s",
                            (uploader, limit, offset),
                        )
                    elif uploader and include_deleted:
                        cur.execute(
                            "SELECT id, name, area, size, uploader, uploaded_at, deleted_at, deleted_by FROM uploads WHERE uploader = %s ORDER BY uploaded_at DESC LIMIT %s OFFSET %s",
                            (uploader, limit, offset),
                        )
                    elif include_deleted:
                        cur.execute(
                            "SELECT id, name, area, size, uploader, uploaded_at, deleted_at, deleted_by FROM uploads ORDER BY uploaded_at DESC LIMIT %s OFFSET %s",
                            (limit, offset),
                        )
                    else:
                        cur.execute(
                            "SELECT id, name, area, size, uploader, uploaded_at, deleted_at, deleted_by FROM uploads WHERE deleted_at IS NULL ORDER BY uploaded_at DESC LIMIT %s OFFSET %s",
                            (limit, offset),
                        )
                    rows = cur.fetchall()
        except Exception:
            return []
        return [
            {
                "id": r[0],
                "name": r[1],
                "area": r[2],
                "size": r[3],
                "uploader": r[4],
                "uploaded_at": r[5].isoformat() if r[5] is not None else None,
                "deleted_at": r[6].isoformat() if r[6] is not None else None,
                "deleted_by": r[7],
            }
            for r in rows
        ]

    def soft_delete_upload(self, upload_id: int, deleted_by: str | None) -> bool:
        try:
            with self._connect_pg() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE uploads SET deleted_at = now(), deleted_by = %s WHERE id = %s AND deleted_at IS NULL",
                        (deleted_by, upload_id),
                    )
                    updated = cur.rowcount
                conn.commit()
            return updated > 0
        except Exception:
            return False

    def soft_delete_upload_by_name(self, name: str, area: str, deleted_by: str | None) -> int:
        try:
            with self._connect_pg() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE uploads SET deleted_at = now(), deleted_by = %s WHERE name = %s AND area = %s AND deleted_at IS NULL",
                        (deleted_by, name, area),
                    )
                    updated = cur.rowcount
                conn.commit()
            return updated
        except Exception:
            return 0

    def get_upload(self, upload_id: int) -> dict[str, object] | None:
        try:
            with self._connect_pg() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT id, name, area, size, uploader, uploaded_at, deleted_at, deleted_by FROM uploads WHERE id = %s",
                        (upload_id,),
                    )
                    row = cur.fetchone()
        except Exception:
            return None
        if row is None:
            return None
        return {
            "id": row[0],
            "name": row[1],
            "area": row[2],
            "size": row[3],
            "uploader": row[4],
            "uploaded_at": row[5].isoformat() if row[5] is not None else None,
            "deleted_at": row[6].isoformat() if row[6] is not None else None,
            "deleted_by": row[7],
        }
