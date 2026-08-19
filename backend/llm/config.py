"""LLM configuration derived from the final notebook setup."""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

PROVIDER = "groq"

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

# Same model used in the notebook.
MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "qwen/qwen3.6-27b",
).strip()

# Same grounded-generation settings used in the notebook.
TEMPERATURE = float(
    os.getenv("TEMPERATURE", "0.1")
)

MAX_TOKENS = int(
    os.getenv("MAX_TOKENS", "700")
)

# The notebook did not set top_p for the final grounded model.
# Keep it configurable, but do not pass it unless explicitly enabled.
TOP_P = float(
    os.getenv("TOP_P", "1.0")
)

REASONING_EFFORT = os.getenv(
    "REASONING_EFFORT",
    "none",
).strip()

TIMEOUT = int(
    os.getenv("LLM_TIMEOUT", "120")
)

RETRIES = int(
    os.getenv("LLM_RETRIES", "3")
)

STREAM = os.getenv(
    "LLM_STREAM",
    "false",
).lower() == "true"
