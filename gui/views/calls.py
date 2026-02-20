"""Вкладка управления звонками в GUI."""
import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from gui.widgets import SectionLabel, ScrollableFrame


class CallsView(tk.Frame):
    """Вкладка звонков: список + добавление + запуск анализа."""

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg="#f8fafc", **kwargs)
        self._app = app
        self._build()

    def _build(self):
        SectionLabel(self, text="📞 Звонки", bg="#f8fafc").pack(fill="x", padx=20, pady=(16, 4))

        toolbar = tk.Frame(self, bg="#f8fafc")
        toolbar.pack(fill="x", padx=20, pady=4)

        ttk.Button(toolbar, text="+ Добавить звонок", command=self._add_call).pack(side="left", padx=(0, 8))
        ttk.Button(toolbar, text="🔍 Анализировать выбранный", command=self._analyze_selected).pack(side="left")
        ttk.Button(toolbar, text="↻ Обновить", command=self.refresh).pack(side="right")

        self._list_frame = ScrollableFrame(self, bg="#f8fafc")
        self._list_frame.pack(fill="both", expand=True, padx=20, pady=(4, 16))

        self._selected_call_id = None

    def _add_call(self):
        agent_id = simpledialog.askstring("Новый звонок", "ID агента:", parent=self)
        if not agent_id:
            return
        phone = simpledialog.askstring("Новый звонок", "Телефон клиента:", parent=self)
        if not phone:
            return
        self._app.service_create_call(agent_id.strip(), phone.strip())
        self.refresh()

    def _analyze_selected(self):
        if not self._selected_call_id:
            messagebox.showinfo("Анализ", "Выберите звонок из списка.")
            return
        result = self._app.service_analyze_call(self._selected_call_id)
        if result:
            messagebox.showinfo(
                "Результат анализа",
                f"Тональность: {result.sentiment.value}\n"
                f"Оценка качества: {result.quality_score:.1f}/100\n"
                f"Ключевые слова: {', '.join(result.keywords[:5]) or '—'}",
            )
        else:
            messagebox.showerror("Ошибка", "Не удалось проанализировать звонок.")

    def refresh(self):
        calls = self._app.get_calls()
        inner = self._list_frame.inner
        for w in inner.winfo_children():
            w.destroy()
        self._selected_call_id = None

        if not calls:
            tk.Label(inner, text="Звонков нет. Добавьте первый!", fg="#64748b",
                     font=("Segoe UI", 10), bg="#ffffff").pack(padx=12, pady=8)
            return

        for call in reversed(calls):
            self._render_call_row(inner, call)

    def _render_call_row(self, parent, call):
        row = tk.Frame(parent, bg="#ffffff", relief="ridge", bd=1, cursor="hand2")
        row.pack(fill="x", pady=2, padx=2)

        tk.Label(row, text=f"📞 {call.customer_phone}", font=("Segoe UI", 10, "bold"),
                 bg="#ffffff", anchor="w").pack(side="left", padx=8, pady=6)
        tk.Label(row, text=f"Агент: {call.agent_id[:8]}…", fg="#64748b",
                 font=("Segoe UI", 9), bg="#ffffff").pack(side="left", padx=4)
        status_color = "#16a34a" if call.status.value == "completed" else "#d97706"
        tk.Label(row, text=call.status.value, fg=status_color,
                 font=("Segoe UI", 9, "bold"), bg="#ffffff").pack(side="right", padx=8)

        def select(event, cid=call.id, r=row):
            self._selected_call_id = cid
            for sibling in parent.winfo_children():
                sibling.configure(bg="#ffffff")
                for child in sibling.winfo_children():
                    child.configure(bg="#ffffff")
            r.configure(bg="#e0e7ff")
            for child in r.winfo_children():
                child.configure(bg="#e0e7ff")

        row.bind("<Button-1>", select)
        for child in row.winfo_children():
            child.bind("<Button-1>", select)
