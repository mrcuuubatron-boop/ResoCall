"""
gui/main.py — точка входа десктопного GUI-приложения ResoCall.

Запуск:
    python gui/main.py
    (из корня проекта)
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import tkinter as tk
from tkinter import ttk

from core.models import Agent, CallRecord, AnalysisResult
from core.analysis import analyze_call
from backend.app.services import (
    create_agent, list_agents,
    create_call, list_calls,
    run_analysis, list_analyses,
)
from gui.views.dashboard import DashboardView
from gui.views.calls import CallsView
from gui.views.agents import AgentsView
from gui.views.analysis import AnalysisView


class ResoCallApp(tk.Tk):
    """Главное окно приложения ResoCall."""

    def __init__(self):
        super().__init__()
        self.title("ResoCall — Анализ Колл-Центра")
        self.geometry("960x640")
        self.minsize(800, 540)
        self.configure(bg="#f8fafc")

        self._build_ui()

    # ── Service layer delegates ──────────────────────────────────────────────

    def get_calls(self):
        return list_calls()

    def get_agents(self):
        return list_agents()

    def get_analyses(self):
        return list_analyses()

    def service_create_agent(self, name: str, department: str = "", email: str = "") -> Agent:
        agent = create_agent(name=name, department=department, email=email)
        return agent

    def service_create_call(self, agent_id: str, customer_phone: str) -> CallRecord:
        return create_call(agent_id=agent_id, customer_phone=customer_phone)

    def service_analyze_call(self, call_id: str):
        return run_analysis(call_id)

    # ── UI construction ──────────────────────────────────────────────────────

    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg="#4f46e5", height=52)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="📞 ResoCall", font=("Segoe UI", 15, "bold"),
                 fg="white", bg="#4f46e5").pack(side="left", padx=20)

        # Notebook (tabs)
        style = ttk.Style(self)
        style.configure("TNotebook", background="#f8fafc", borderwidth=0)
        style.configure("TNotebook.Tab", font=("Segoe UI", 10), padding=(14, 6))

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=0, pady=0)

        self._dashboard_view = DashboardView(notebook, app=self)
        self._calls_view     = CallsView(notebook, app=self)
        self._agents_view    = AgentsView(notebook, app=self)
        self._analysis_view  = AnalysisView(notebook, app=self)

        notebook.add(self._dashboard_view, text="  Дашборд  ")
        notebook.add(self._calls_view,     text="  Звонки  ")
        notebook.add(self._agents_view,    text="  Агенты  ")
        notebook.add(self._analysis_view,  text="  Анализ  ")

        def on_tab_change(event):
            tab = notebook.index(notebook.select())
            views = [
                self._dashboard_view,
                self._calls_view,
                self._agents_view,
                self._analysis_view,
            ]
            view = views[tab]
            if tab == 0:
                view.refresh(self.get_calls(), self.get_analyses())
            elif hasattr(view, "refresh"):
                view.refresh()

        notebook.bind("<<NotebookTabChanged>>", on_tab_change)

        # Load initial dashboard data
        self._dashboard_view.refresh(self.get_calls(), self.get_analyses())


if __name__ == "__main__":
    app = ResoCallApp()
    app.mainloop()
