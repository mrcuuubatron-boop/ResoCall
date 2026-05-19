from __future__ import annotations

import json
import shutil
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from threading import Lock
from typing import Any

from app.config import Settings


def _parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _format_duration(seconds: int) -> str:
    minutes = seconds // 60
    remainder = seconds % 60
    return f"{minutes}:{remainder:02d}"


class CallStore:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._lock = Lock()
        self._state_dir = self.settings.data_dir / "state"
        self._calls_root = self._state_dir / "calls"
        self._active_calls_dir = self._calls_root / "active"
        self._deleted_calls_dir = self._calls_root / "deleted"
        self._employees_path = self._calls_root / "employees.json"
        self._clients_path = self._calls_root / "clients.json"
        self._audio_dir = self._calls_root / "audio"
        self._state_dir.mkdir(parents=True, exist_ok=True)
        self._active_calls_dir.mkdir(parents=True, exist_ok=True)
        self._deleted_calls_dir.mkdir(parents=True, exist_ok=True)
        self._audio_dir.mkdir(parents=True, exist_ok=True)
        self._seed_if_needed()

    def _default_state(self) -> dict[str, Any]:
        employees = [
            {"id": "emp1", "name": "Иванова Анна Сергеевна", "position": "Старший оператор", "hireDate": "2024-01-15"},
            {"id": "emp2", "name": "Петров Дмитрий Александрович", "position": "Оператор", "hireDate": "2024-03-20"},
            {"id": "emp3", "name": "Сидорова Мария Ивановна", "position": "Оператор", "hireDate": "2024-02-10"},
            {"id": "emp4", "name": "Козлов Алексей Николаевич", "position": "Оператор", "hireDate": "2024-05-05"},
        ]

        clients = [
            {"id": "cl1", "name": "Кузнецов Иван Петрович", "phone": "+7 (900) 123-45-67"},
            {"id": "cl2", "name": "Смирнова Ольга Александровна", "phone": "+7 (901) 234-56-78"},
            {"id": "cl3", "name": "Федоров Андрей Михайлович", "phone": "+7 (902) 345-67-89"},
            {"id": "cl4", "name": "Волкова Наталья Сергеевна", "phone": "+7 (903) 456-78-90"},
        ]

        def transcript(*rows: tuple[str, str, str]) -> list[dict[str, str]]:
            return [{"speaker": speaker, "text": text, "timestamp": timestamp} for speaker, text, timestamp in rows]

        calls = [
            {
                "id": "call-1",
                "employeeId": "emp1",
                "clientId": "cl1",
                "date": "2026-05-01T09:10:00+00:00",
                "duration": 420,
                "sentiment": "positive",
                "scriptCompliance": 94,
                "category": "Оплата",
                "isProcessed": True,
                "errorReason": None,
                "audioUrl": "/audio/call-1.mp3",
                "transcript": transcript(
                    ("operator", "Добрый день! Компания 'РесоКалл', Анна. Чем могу помочь?", "00:00"),
                    ("client", "Здравствуйте, у меня вопрос по оплате.", "00:05"),
                    ("operator", "Сейчас проверю ваш договор.", "00:12"),
                    ("client", "Спасибо.", "00:18"),
                ),
                "deleted_at": None,
                "deleted_by": None,
            },
            {
                "id": "call-2",
                "employeeId": "emp2",
                "clientId": "cl2",
                "date": "2026-05-01T11:40:00+00:00",
                "duration": 360,
                "sentiment": "neutral",
                "scriptCompliance": 81,
                "category": "Тарифы",
                "isProcessed": True,
                "errorReason": None,
                "audioUrl": "/audio/call-2.mp3",
                "transcript": transcript(
                    ("operator", "Здравствуйте! Подскажите, какой тариф вам нужен?", "00:00"),
                    ("client", "Хотела бы узнать про расширенный.", "00:06"),
                    ("operator", "Расскажу по условиям и оформлю заявку.", "00:12"),
                    ("client", "Хорошо, спасибо.", "00:20"),
                ),
                "deleted_at": None,
                "deleted_by": None,
            },
            {
                "id": "call-3",
                "employeeId": "emp3",
                "clientId": "cl3",
                "date": "2026-05-02T13:20:00+00:00",
                "duration": 510,
                "sentiment": "negative",
                "scriptCompliance": 68,
                "category": "Техническая поддержка",
                "isProcessed": True,
                "errorReason": None,
                "audioUrl": "/audio/call-3.mp3",
                "transcript": transcript(
                    ("operator", "Здравствуйте, компания 'РесоКалл'.", "00:00"),
                    ("client", "Интернет не работает уже второй день!", "00:04"),
                    ("operator", "Проверяю заявку.", "00:12"),
                    ("client", "Жду решения.", "00:18"),
                ),
                "deleted_at": None,
                "deleted_by": None,
            },
            {
                "id": "call-4",
                "employeeId": "emp4",
                "clientId": "cl4",
                "date": "2026-05-03T10:05:00+00:00",
                "duration": 300,
                "sentiment": "positive",
                "scriptCompliance": 89,
                "category": "Консультация",
                "isProcessed": True,
                "errorReason": None,
                "audioUrl": "/audio/call-4.mp3",
                "transcript": transcript(
                    ("operator", "Добрый день! Чем помочь?", "00:00"),
                    ("client", "Хочу узнать баланс.", "00:05"),
                    ("operator", "Конечно, проверяю.", "00:10"),
                    ("client", "Спасибо.", "00:18"),
                ),
                "deleted_at": None,
                "deleted_by": None,
            },
            {
                "id": "call-5",
                "employeeId": "emp1",
                "clientId": "cl2",
                "date": "2026-05-03T15:30:00+00:00",
                "duration": 240,
                "sentiment": "neutral",
                "scriptCompliance": 0,
                "category": "Жалоба",
                "isProcessed": False,
                "errorReason": "Низкое качество аудио",
                "audioUrl": "/audio/call-5.mp3",
                "transcript": transcript(
                    ("client", "Алло? Меня плохо слышно?", "00:00"),
                    ("operator", "Да, связь нестабильная.", "00:03"),
                ),
                "deleted_at": None,
                "deleted_by": None,
            },
            {
                "id": "call-6",
                "employeeId": "emp2",
                "clientId": "cl1",
                "date": "2026-05-04T12:00:00+00:00",
                "duration": 480,
                "sentiment": "positive",
                "scriptCompliance": 97,
                "category": "Подключение услуг",
                "isProcessed": True,
                "errorReason": None,
                "audioUrl": "/audio/call-6.mp3",
                "transcript": transcript(
                    ("operator", "Здравствуйте! Компания 'РесоКалл'.", "00:00"),
                    ("client", "Хочу подключить дополнительную услугу.", "00:05"),
                    ("operator", "С удовольствием оформлю.", "00:10"),
                    ("client", "Отлично.", "00:20"),
                ),
                "deleted_at": None,
                "deleted_by": None,
            },
        ]

        return {"employees": employees, "clients": clients, "calls": calls}

    def _read_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return deepcopy(default)
        with path.open("r", encoding="utf-8") as fp:
            return json.load(fp)

    def _write_json(self, path: Path, payload: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as fp:
            json.dump(payload, fp, ensure_ascii=False, indent=2)

    def _call_dir(self, call_id: str, deleted: bool = False) -> Path:
        return (self._deleted_calls_dir if deleted else self._active_calls_dir) / call_id

    def _audio_path(self, file_name: str) -> Path:
        return self._audio_dir / file_name

    def _seed_if_needed(self) -> None:
        default_state = self._default_state()
        if not self._employees_path.exists():
            self._write_json(self._employees_path, default_state["employees"])
        if not self._clients_path.exists():
            self._write_json(self._clients_path, default_state["clients"])

        for call in default_state["calls"]:
            self._seed_call(call)

        # Keep audio stubs available even for already-seeded calls.
        for call_dir in self._active_calls_dir.iterdir():
            if not call_dir.is_dir():
                continue
            meta = self._read_json(call_dir / "meta.json", {})
            if not isinstance(meta, dict):
                continue
            call_id = str(meta.get("id") or call_dir.name)
            self._ensure_audio_stub(call_id)

    def _seed_call(self, call: dict[str, Any]) -> None:
        call_dir = self._call_dir(str(call["id"]), deleted=False)
        if call_dir.exists() or self._call_dir(str(call["id"]), deleted=True).exists():
            return

        call_dir.mkdir(parents=True, exist_ok=True)
        meta = deepcopy(call)
        meta["audioUrl"] = f"/api/calls/audio/{call['id']}.mp3"
        transcript = meta.pop("transcript", [])
        self._write_json(call_dir / "meta.json", meta)
        self._write_json(call_dir / "transcript.json", transcript)
        self._ensure_audio_stub(str(call["id"]))

    def _ensure_audio_stub(self, call_id: str) -> None:
        # Temporary media stub so frontend links always resolve.
        audio_path = self._audio_path(f"{call_id}.mp3")
        if audio_path.exists():
            return
        audio_path.parent.mkdir(parents=True, exist_ok=True)
        audio_path.write_bytes(b"ID3\x04\x00\x00\x00\x00\x00\x00")

    def _client_name_by_id(self, client_id: str) -> str:
        for client in self.list_clients():
            if client["id"] == client_id:
                return client["name"]
        return client_id

    def _employee_name_by_id(self, employee_id: str) -> str:
        for employee in self.list_employees():
            if employee["id"] == employee_id:
                return employee["name"]
        return employee_id

    def _enrich_call(self, call: dict[str, Any]) -> dict[str, Any]:
        payload = deepcopy(call)
        payload["clientName"] = self._client_name_by_id(str(call["clientId"]))
        payload["employeeName"] = self._employee_name_by_id(str(call["employeeId"]))
        payload["durationText"] = _format_duration(int(call["duration"]))
        # Normalize legacy /audio/* links to the current backend audio endpoint.
        audio_url = str(payload.get("audioUrl") or "")
        if not audio_url.startswith("/api/calls/audio/"):
            payload["audioUrl"] = f"/api/calls/audio/{payload['id']}.mp3"
        self._ensure_audio_stub(str(payload["id"]))
        return payload

    def _read_call_from_dir(self, call_dir: Path) -> dict[str, Any] | None:
        meta_path = call_dir / "meta.json"
        transcript_path = call_dir / "transcript.json"
        if not meta_path.exists():
            return None

        with meta_path.open("r", encoding="utf-8") as fp:
            meta = json.load(fp)

        transcript: list[dict[str, Any]] = []
        if transcript_path.exists():
            with transcript_path.open("r", encoding="utf-8") as fp:
                transcript = json.load(fp)

        meta["transcript"] = transcript
        meta["deleted"] = call_dir.parent.name == "deleted"
        return self._enrich_call(meta)

    def _list_call_dirs(self, include_deleted: bool = False) -> list[Path]:
        call_dirs = [path for path in self._active_calls_dir.iterdir() if path.is_dir()]
        if include_deleted:
            call_dirs.extend(path for path in self._deleted_calls_dir.iterdir() if path.is_dir())
        return call_dirs

    def list_employees(self) -> list[dict[str, Any]]:
        return deepcopy(self._read_json(self._employees_path, []))

    def list_clients(self) -> list[dict[str, Any]]:
        return deepcopy(self._read_json(self._clients_path, []))

    def create_employee(self, name: str, position: str, hire_date: str | None = None) -> dict[str, Any]:
        name = name.strip()
        position = position.strip()
        if not name or not position:
            raise ValueError("employee name and position are required")
        employees = self.list_employees()
        employee = {
            "id": f"emp-{uuid4().hex[:8]}",
            "name": name,
            "position": position,
            "hireDate": hire_date.strip() if hire_date else datetime.now(timezone.utc).date().isoformat(),
        }
        employees.append(employee)
        self._write_json(self._employees_path, employees)
        return deepcopy(employee)

    def delete_employee(self, employee_id: str) -> bool:
        employees = self.list_employees()
        filtered = [employee for employee in employees if str(employee.get("id")) != employee_id]
        if len(filtered) == len(employees):
            return False
        self._write_json(self._employees_path, filtered)
        return True

    def create_client(self, name: str, phone: str | None = None) -> dict[str, Any]:
        name = name.strip()
        if not name:
            raise ValueError("client name is required")
        clients = self.list_clients()
        client = {
            "id": f"cl-{uuid4().hex[:8]}",
            "name": name,
            "phone": phone.strip() if phone else "",
        }
        clients.append(client)
        self._write_json(self._clients_path, clients)
        return deepcopy(client)

    def delete_client(self, client_id: str) -> bool:
        clients = self.list_clients()
        filtered = [client for client in clients if str(client.get("id")) != client_id]
        if len(filtered) == len(clients):
            return False
        self._write_json(self._clients_path, filtered)
        return True

    def create_call(self, call: dict[str, Any]) -> dict[str, Any]:
        call_id = str(call.get("call_id") or call.get("id") or f"call-{uuid4().hex[:8]}")
        call_dir = self._call_dir(call_id, deleted=False)
        if call_dir.exists() or self._call_dir(call_id, deleted=True).exists():
            raise ValueError(f"call already exists: {call_id}")

        employee_id = str(call.get("employee_id") or call.get("employeeId") or "").strip()
        client_id = str(call.get("client_id") or call.get("clientId") or "").strip()
        if not employee_id or not client_id:
            raise ValueError("employee_id and client_id are required")

        transcript = call.get("transcript") or []
        if not isinstance(transcript, list):
            raise ValueError("transcript must be a list")

        meta = {
            "id": call_id,
            "employeeId": employee_id,
            "clientId": client_id,
            "date": str(call.get("date") or datetime.now(timezone.utc).isoformat()),
            "duration": int(call.get("duration") or 0),
            "sentiment": str(call.get("sentiment") or "neutral"),
            "scriptCompliance": int(call.get("script_compliance") or call.get("scriptCompliance") or 0),
            "category": str(call.get("category") or "Не определено"),
            "isProcessed": bool(call.get("is_processed") if "is_processed" in call else call.get("isProcessed", False)),
            "errorReason": call.get("error_reason") if "error_reason" in call else call.get("errorReason"),
            "audioUrl": str(call.get("audio_url") or call.get("audioUrl") or f"/api/calls/audio/{call_id}.mp3"),
            "deleted_at": None,
            "deleted_by": None,
        }

        call_dir.mkdir(parents=True, exist_ok=False)
        self._write_json(call_dir / "meta.json", meta)
        self._write_json(call_dir / "transcript.json", transcript)
        self._ensure_audio_stub(call_id)
        return self.get_call(call_id, include_deleted=False) or meta

    def list_calls(
        self,
        from_dt: datetime | None = None,
        to_dt: datetime | None = None,
        include_deleted: bool = False,
    ) -> list[dict[str, Any]]:
        calls = []
        for call_dir in self._list_call_dirs(include_deleted=include_deleted):
            call = self._read_call_from_dir(call_dir)
            if call is None:
                continue
            if not include_deleted and call.get("deleted_at"):
                continue
            call_dt = _parse_iso(str(call["date"]))
            if from_dt and call_dt < from_dt:
                continue
            if to_dt and call_dt > to_dt:
                continue
            calls.append(call)

        return sorted(calls, key=lambda item: item["date"], reverse=True)

    def list_unprocessed_calls(self) -> list[dict[str, Any]]:
        return [call for call in self.list_calls() if not call.get("isProcessed")]

    def list_deleted_calls(self) -> list[dict[str, Any]]:
        return [call for call in self.list_calls(include_deleted=True) if call.get("deleted_at")]

    def get_call(self, call_id: str, include_deleted: bool = True) -> dict[str, Any] | None:
        active_dir = self._call_dir(call_id, deleted=False)
        deleted_dir = self._call_dir(call_id, deleted=True)

        if active_dir.exists():
            return self._read_call_from_dir(active_dir)
        if include_deleted and deleted_dir.exists():
            return self._read_call_from_dir(deleted_dir)
        return None

    def soft_delete_call(self, call_id: str, deleted_by: str | None = None) -> bool:
        with self._lock:
            source_dir = self._call_dir(call_id, deleted=False)
            target_dir = self._call_dir(call_id, deleted=True)
            if not source_dir.exists() or target_dir.exists():
                return False

            meta_path = source_dir / "meta.json"
            if not meta_path.exists():
                return False

            with meta_path.open("r", encoding="utf-8") as fp:
                meta = json.load(fp)

            meta["deleted_at"] = datetime.now(timezone.utc).isoformat()
            meta["deleted_by"] = deleted_by
            self._write_json(meta_path, meta)
            target_dir.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source_dir), str(target_dir))
            return True

    def restore_call(self, call_id: str) -> bool:
        with self._lock:
            source_dir = self._call_dir(call_id, deleted=True)
            target_dir = self._call_dir(call_id, deleted=False)
            if not source_dir.exists() or target_dir.exists():
                return False

            meta_path = source_dir / "meta.json"
            if not meta_path.exists():
                return False

            with meta_path.open("r", encoding="utf-8") as fp:
                meta = json.load(fp)

            meta["deleted_at"] = None
            meta["deleted_by"] = None
            self._write_json(meta_path, meta)
            target_dir.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source_dir), str(target_dir))
            return True
