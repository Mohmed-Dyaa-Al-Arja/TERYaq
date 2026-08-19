from __future__ import annotations

from pydantic import BaseModel, Field


class Source(BaseModel):
    document_id: str | None = None
    page: int | str | None = None
    section: str | None = None
    chunk_id: str | None = None
    content_type: str | None = None
    citation: str | None = None


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    confidence: str
    evidence_sufficient: bool
    refusal: bool
    sources: list[Source] = Field(default_factory=list)
    memory: list[dict] = Field(default_factory=list)
