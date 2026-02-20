"""Вкладка управления агентами в GUI."""
import sys
import os
import tkinter as tk
from tkinter import ttk, simpledialog

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from gui.widgets import SectionLabel, ScrollableFrame


class AgentsView(tk.Frame):
    """Вкладка агентов: список + добавление."""

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg="#f8fafc", **kwargs)
        self._app = app
        self._build()

    def _build(self):
        SectionLabel(self, text="👤 Агенты", bg="#f8fafc").pack(fill="x", padx=20, pady=(16, 4))

        toolbar = tk.Frame(self, bg="#f8fafc")
        toolbar.pack(fill="x", padx=20, pady=4)
        ttk.Button(toolbar, text="+ Добавить агента", command=self._add_agent).pack(side="left", padx=(0, 8))
        ttk.Button(toolbar, text="↻ Обновить", command=self.refresh).pack(side="right")

        self._list_frame = ScrollableFrame(self, bg="#f8fafc")
        self._list_frame.pack(fill="both", expand=True, padx=20, pady=(4, 16))

    def _add_agent(self):
        name = simpledialog.askstring("Новый агент", "Имя агента:", parent=self)
        if not name:
            return
        department = simpledialog.askstring("Новый агент", "Отдел (необязательно):", parent=self) or ""
        email = simpledialog.askstring("Новый агент", "Email (необязательно):", parent=self) or ""
        self._app.service_create_agent(name.strip(), department.strip(), email.strip())
        self.refresh()

    def refresh(self):
        agents = self._app.get_agents()
        inner = self._list_frame.inner
        for w in inner.winfo_children():
            w.destroy()

        if not agents:
            tk.Label(inner, text="Агентов нет. Добавьте первого!", fg="#64748b",
                     font=("Segoe UI", 10), bg="#ffffff").pack(padx=12, pady=8)
            return

        for agent in agents:
            row = tk.Frame(inner, bg="#ffffff", relief="ridge", bd=1)
            row.pack(fill="x", pady=2, padx=2)
            tk.Label(row, text=f"👤 {agent.name}", font=("Segoe UI", 10, "bold"),
                     bg="#ffffff", anchor="w").pack(side="left", padx=8, pady=6)
            sub = f"{agent.department or '—'} · {agent.email or '—'}"
            tk.Label(row, text=sub, fg="#64748b",
                     font=("Segoe UI", 9), bg="#ffffff").pack(side="left", padx=4)
