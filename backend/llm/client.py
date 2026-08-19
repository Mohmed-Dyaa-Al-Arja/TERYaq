"""Groq/OpenAI-compatible client for Teryaq's grounded Qwen model."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from langchain_openai import ChatOpenAI

from .config import (
    GROQ_API_KEY,
    MODEL_NAME,
    TEMPERATURE,
    MAX_TOKENS,
    REASONING_EFFORT,
    TIMEOUT,
    RETRIES,
)

from .exceptions import (
    InvalidLLMResponseError,
    LLMConfigurationError,
    LLMGenerationError,
)

from .prompts import SYSTEM_PROMPT
from .schemas import GroundedResponse
from .image_utils import image_file_to_data_url


# ============================================================
# LLM Client
# ============================================================

@lru_cache(maxsize=1)
def get_grounded_llm() -> ChatOpenAI:
    """Create one shared grounded LLM instance."""

    if not GROQ_API_KEY:
        raise LLMConfigurationError(
            "GROQ_API_KEY is missing from the environment."
        )

    return ChatOpenAI(
        model=MODEL_NAME,
        base_url="https://api.groq.com/openai/v1",
        api_key=GROQ_API_KEY,

        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,

        timeout=TIMEOUT,
        max_retries=RETRIES,

        # ----------------------------------------------------
        # IMPORTANT:
        # reasoning_effort is passed explicitly.
        # This avoids the LangChain warning.
        # ----------------------------------------------------
        reasoning_effort=REASONING_EFFORT,

        # ----------------------------------------------------
        # Groq/OpenAI-compatible JSON output.
        # ----------------------------------------------------
        model_kwargs={
            "response_format": {
                "type": "json_object"
            }
        },
    )


# ============================================================
# JSON Extraction
# ============================================================

def _extract_json(raw_output: str) -> dict[str, Any]:
    """Parse a JSON object from a model response."""

    text = raw_output.strip()

    # --------------------------------------------------------
    # Remove Qwen/Groq thinking blocks if present.
    # --------------------------------------------------------

    text = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=re.DOTALL,
    ).strip()

    # --------------------------------------------------------
    # Remove Markdown JSON fences.
    # --------------------------------------------------------

    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"```$",
        "",
        text,
    ).strip()

    # --------------------------------------------------------
    # Try direct JSON parsing first.
    # --------------------------------------------------------

    try:
        return json.loads(text)

    except json.JSONDecodeError:

        # ----------------------------------------------------
        # Fallback:
        # Find the first { and last }.
        # ----------------------------------------------------

        start = text.find("{")
        end = text.rfind("}")

        if start < 0 or end <= start:
            raise InvalidLLMResponseError(
                "No valid JSON object was returned by the model."
            )

        try:

            return json.loads(
                text[start:end + 1]
            )

        except json.JSONDecodeError as exc:

            raise InvalidLLMResponseError(
                f"Invalid JSON returned by the model: {exc}"
            ) from exc


# ============================================================
# Grounded Generation
# ============================================================

def generate_grounded_response(
    *,
    question: str,
    accepted_evidence: list[dict],
    image_path: str | Path | None = None,
) -> dict[str, Any]:
    """
    Generate a structured answer using accepted evidence only.

    Optional image_path allows the same LLM client to receive
    the original visual evidence when multimodal processing
    is required.
    """

    if not accepted_evidence:
        raise ValueError(
            "Grounded generation requires accepted evidence."
        )

    from .prompts import build_grounded_prompt

    # --------------------------------------------------------
    # Build grounded prompt
    # --------------------------------------------------------

    prompt = build_grounded_prompt(
        question=question,
        accepted_evidence=accepted_evidence,
    )

    llm = get_grounded_llm()

    # ========================================================
    # Text-only generation
    # ========================================================

    if image_path is None:

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]

    # ========================================================
    # Multimodal generation
    # ========================================================

    else:

        image_url = image_file_to_data_url(
            image_path
        )

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ],
            },
        ]

    # ========================================================
    # Generate response
    # ========================================================

    try:

        response = llm.invoke(
            messages
        )

    except Exception as exc:

        raise LLMGenerationError(
            f"Grounded LLM generation failed: {exc}"
        ) from exc

    # ========================================================
    # Extract raw model output
    # ========================================================

    raw_output = getattr(
        response,
        "content",
        str(response),
    )

    # ========================================================
    # Parse JSON
    # ========================================================

    data = _extract_json(
        raw_output
    )

    # ========================================================
    # Validate response schema
    # ========================================================

    try:

        validated = GroundedResponse.model_validate(
            data
        )

    except Exception as exc:

        raise InvalidLLMResponseError(
            "Model JSON does not match "
            f"GroundedResponse: {exc}"
        ) from exc

    return validated.model_dump()