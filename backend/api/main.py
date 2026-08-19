from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes.chat import router as chat_router
from backend.api.routes.history import router as history_router
from backend.api.routes.sessions import router as sessions_router

app = FastAPI(
    title="Teryaq API",
    description="Teryaq Medical RAG API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(history_router)
app.include_router(sessions_router)


@app.get("/")
def root():
    return {"name": "Teryaq", "status": "online", "version": "1.0.0"}


@app.get("/health")
def health():
    from backend.database.mongodb import ping_database
    return {"status": "healthy", "database": ping_database()}
