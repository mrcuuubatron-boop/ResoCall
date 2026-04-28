import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import Settings


class Storage:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        self.settings.data_dir.mkdir(parents=True, exist_ok=True)
        self.settings.upload_dir.mkdir(parents=True, exist_ok=True)
        self.settings.result_dir.mkdir(parents=True, exist_ok=True)
        self.settings.log_dir.mkdir(parents=True, exist_ok=True)

    def upload_path(self, task_id: str, file_name: str) -> Path:
        suffix = Path(file_name).suffix.lower()
        return self.settings.upload_dir / f"{task_id}{suffix}"

    def result_path(self, task_id: str) -> Path:
        return self.settings.result_dir / f"{task_id}.json"

    def error_log_path(self, task_id: str) -> Path:
        return self.settings.log_dir / f"{task_id}.error.log"

    def write_json(self, path: Path, data: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False, indent=2)

    def read_json(self, path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as fp:
            return json.load(fp)

    def write_error(self, task_id: str, message: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        payload = f"[{now}] {message}\n"
        self.error_log_path(task_id).write_text(payload, encoding="utf-8")

    def default_script_path(self) -> Path:
        return self.settings.data_dir / "scripts" / "default.json"

    def read_default_script(self) -> list[str]:
        path = self.default_script_path()
        if not path.exists():
            return []
        payload = self.read_json(path)
        phrases = payload.get("required_phrases", [])
        return [p for p in phrases if isinstance(p, str)]

    def write_default_script(self, required_phrases: list[str]) -> None:
        path = self.default_script_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        self.write_json(path, {"required_phrases": required_phrases})

    def _sanitize_part(self, value: str) -> str:
        safe = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in value.strip().lower())
        return safe or "unknown"

    def module_settings_path(self, login: str, module_key: str) -> Path:
        safe_login = self._sanitize_part(login)
        safe_module = self._sanitize_part(module_key)
        return self.settings.data_dir / "module_settings" / safe_login / f"{safe_module}.json"

    def read_module_settings(self, login: str, module_key: str) -> tuple[dict[str, Any], str | None]:
        path = self.module_settings_path(login, module_key)
        if not path.exists():
            return {}, None

        payload = self.read_json(path)
        settings = payload.get("settings") if isinstance(payload, dict) else None
        updated_at = payload.get("updated_at") if isinstance(payload, dict) else None

        if not isinstance(settings, dict):
            settings = {}
        if updated_at is not None and not isinstance(updated_at, str):
            updated_at = None
        return settings, updated_at

    def write_module_settings(self, login: str, module_key: str, settings: dict[str, Any]) -> str:
        now = datetime.now(timezone.utc).isoformat()
        path = self.module_settings_path(login, module_key)
        self.write_json(path, {"settings": settings, "updated_at": now})
        return now
