"""Pydantic response schemas for grounded medical generation."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Claim(BaseModel):
    text: str
    citation: str


class GroundedResponse(BaseModel):
    answer: str
    claims: list[Claim] = Field(default_factory=list)
    confidence: Literal["high", "medium", "low"] = "low"
    refusal: bool = False
