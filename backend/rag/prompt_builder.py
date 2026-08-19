"""Compatibility wrapper around the grounded LLM prompt builder."""

from backend.llm.prompts import (
    SYSTEM_PROMPT,
    build_grounded_prompt,
)

__all__ = [
    "SYSTEM_PROMPT",
    "build_grounded_prompt",
]
