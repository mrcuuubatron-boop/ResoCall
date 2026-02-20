"""Переиспользуемые виджеты."""
import tkinter as tk
from tkinter import ttk


class StatCard(tk.Frame):
    """Карточка статистики (иконка + значение + подпись)."""

    def __init__(self, parent, icon: str, label: str, **kwargs):
        super().__init__(parent, relief="raised", bd=1, padx=16, pady=12, bg="#ffffff", **kwargs)
        tk.Label(self, text=icon, font=("Segoe UI", 24), bg="#ffffff").pack()
        self._value_var = tk.StringVar(value="—")
        tk.Label(self, textvariable=self._value_var, font=("Segoe UI", 20, "bold"),
                 fg="#4f46e5", bg="#ffffff").pack()
        tk.Label(self, text=label, font=("Segoe UI", 9), fg="#64748b", bg="#ffffff").pack()

    def set_value(self, value):
        self._value_var.set(str(value))


class SectionLabel(tk.Label):
    """Заголовок секции."""

    def __init__(self, parent, text: str, **kwargs):
        super().__init__(parent, text=text, font=("Segoe UI", 13, "bold"),
                         anchor="w", **kwargs)


class ScrollableFrame(tk.Frame):
    """Фрейм с вертикальной прокруткой."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.inner = tk.Frame(canvas)

        self.inner.bind("<Configure>",
                        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
