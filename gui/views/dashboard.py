"""Дашборд — главная вкладка GUI."""
import sys
import os
import tkinter as tk
from tkinter import ttk

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from gui.widgets import StatCard, SectionLabel, ScrollableFrame


class DashboardView(tk.Frame):
    """Вкладка с общей статистикой и последними звонками."""

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg="#f8fafc", **kwargs)
        self._app = app
        self._build()

    def _build(self):
        SectionLabel(self, text="📊 Дашборд", bg="#f8fafc").pack(fill="x", padx=20, pady=(16, 8))

        # Stat cards row
        cards_row = tk.Frame(self, bg="#f8fafc")
        cards_row.pack(fill="x", padx=20, pady=4)

        self._card_calls   = StatCard(cards_row, "📞", "Всего звонков")
        self._card_analyzed = StatCard(cards_row, "✅", "Проанализировано")
        self._card_quality  = StatCard(cards_row, "⭐", "Ср. качество")
        self._card_positive = StatCard(cards_row, "😊", "Позитивных")

        for card in (self._card_calls, self._card_analyzed, self._card_quality, self._card_positive):
            card.pack(side="left", padx=6, pady=4)

        SectionLabel(self, text="Последние звонки", bg="#f8fafc").pack(
            fill="x", padx=20, pady=(12, 4))

        self._list_frame = ScrollableFrame(self, bg="#f8fafc")
        self._list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))

    def refresh(self, calls, analyses):
        """Обновить данные дашборда."""
        self._card_calls.set_value(len(calls))
        self._card_analyzed.set_value(len(analyses))

        positive = sum(1 for a in analyses if a.sentiment.value == "positive")
        self._card_positive.set_value(positive)

        if analyses:
            avg_q = sum(a.quality_score for a in analyses) / len(analyses)
            self._card_quality.set_value(f"{avg_q:.1f}")
        else:
            self._card_quality.set_value("—")

        inner = self._list_frame.inner
        for w in inner.winfo_children():
            w.destroy()

        if not calls:
            tk.Label(inner, text="Звонков пока нет", fg="#64748b",
                     font=("Segoe UI", 10), bg="#ffffff").pack(padx=12, pady=8)
            return

        for call in reversed(calls[-10:]):
            row = tk.Frame(inner, bg="#ffffff", relief="ridge", bd=1)
            row.pack(fill="x", pady=2, padx=2)
            tk.Label(row, text=f"📞 {call.customer_phone}", font=("Segoe UI", 10, "bold"),
                     bg="#ffffff", anchor="w").pack(side="left", padx=8, pady=6)
            tk.Label(row, text=call.status.value, fg="#4f46e5",
                     font=("Segoe UI", 9), bg="#ffffff").pack(side="right", padx=8)
