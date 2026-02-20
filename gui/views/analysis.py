"""Вкладка результатов анализа в GUI."""
import sys
import os
import tkinter as tk
from tkinter import ttk

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from gui.widgets import SectionLabel, ScrollableFrame


class AnalysisView(tk.Frame):
    """Вкладка анализа: отображение всех результатов."""

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg="#f8fafc", **kwargs)
        self._app = app
        self._build()

    def _build(self):
        SectionLabel(self, text="🔍 Анализ звонков", bg="#f8fafc").pack(fill="x", padx=20, pady=(16, 4))

        toolbar = tk.Frame(self, bg="#f8fafc")
        toolbar.pack(fill="x", padx=20, pady=4)
        ttk.Button(toolbar, text="↻ Обновить", command=self.refresh).pack(side="right")

        self._list_frame = ScrollableFrame(self, bg="#f8fafc")
        self._list_frame.pack(fill="both", expand=True, padx=20, pady=(4, 16))

    def refresh(self):
        results = self._app.get_analyses()
        inner = self._list_frame.inner
        for w in inner.winfo_children():
            w.destroy()

        if not results:
            tk.Label(inner, text="Результатов анализа нет", fg="#64748b",
                     font=("Segoe UI", 10), bg="#ffffff").pack(padx=12, pady=8)
            return

        sentiment_colors = {"positive": "#16a34a", "neutral": "#64748b", "negative": "#dc2626"}
        sentiment_icons = {"positive": "😊", "neutral": "😐", "negative": "😠"}

        for result in reversed(results):
            color = sentiment_colors.get(result.sentiment.value, "#64748b")
            icon = sentiment_icons.get(result.sentiment.value, "❓")
            row = tk.Frame(inner, bg="#ffffff", relief="ridge", bd=1)
            row.pack(fill="x", pady=3, padx=2)

            tk.Label(row, text=f"{icon} Звонок {result.call_id[:8]}…",
                     font=("Segoe UI", 10, "bold"), bg="#ffffff", anchor="w").pack(
                         side="left", padx=8, pady=6)

            tk.Label(row, text=f"Качество: {result.quality_score:.0f}/100",
                     fg="#4f46e5", font=("Segoe UI", 9), bg="#ffffff").pack(side="left", padx=8)

            keywords_text = ", ".join(result.keywords[:4]) or "—"
            tk.Label(row, text=f"Слова: {keywords_text}", fg="#64748b",
                     font=("Segoe UI", 9), bg="#ffffff").pack(side="left", padx=4)

            tk.Label(row, text=result.sentiment.value, fg=color,
                     font=("Segoe UI", 9, "bold"), bg="#ffffff").pack(side="right", padx=8)
