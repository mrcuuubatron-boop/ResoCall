"""Точка входа FastAPI приложения ResoCall."""
import sys
import os

# Добавляем корень проекта в sys.path, чтобы импорты core/ работали
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.agents import router as agents_router
from backend.app.api.calls import router as calls_router
from backend.app.api.analysis import router as analysis_router

app = FastAPI(
    title="ResoCall API",
    description="REST API для анализа звонков колл-центра с помощью ИИ",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agents_router, prefix="/api/v1")
app.include_router(calls_router, prefix="/api/v1")
app.include_router(analysis_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
def health():
    return {"status": "ok", "service": "ResoCall API"}
