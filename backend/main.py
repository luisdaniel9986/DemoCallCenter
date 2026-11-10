"""
main.py — FastAPI application entry point
==========================================
Start the server:
    cd ErpCallCenter
    uvicorn backend.main:app --reload --port 8000

Interactive docs:
    http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database.connection import Base, engine
import backend.models  # registers all ORM models before create_all()
from backend.routes import (
    customers_router,
    calls_router,
    followups_router,
    predictions_router,
    dashboard_router,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title       = "Call Center CRM API",
    description = "REST API for the Call Center system with real-time ML predictions",
    version     = "1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["http://localhost:5173", "http://localhost:3000"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

app.include_router(customers_router)
app.include_router(calls_router)
app.include_router(followups_router)
app.include_router(predictions_router)
app.include_router(dashboard_router)


@app.get("/", tags=["Root"])
def root():
    return {"system": "Call Center CRM", "version": "1.0.0", "status": "online", "docs": "/docs"}


@app.get("/health", tags=["Root"])
def health():
    return {"status": "ok"}
