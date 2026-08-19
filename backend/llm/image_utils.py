"""Utilities for sending rendered PDF pages to the multimodal LLM."""

from __future__ import annotations

import base64
import mimetypes
from pathlib import Path


SUPPORTED_IMAGE_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
}


def image_file_to_data_url(path: str | Path) -> str:
    """Convert a local image into a data URL."""
    image_path = Path(path)

    if not image_path.exists():
        raise FileNotFoundError(image_path)

    if image_path.suffix.lower() not in SUPPORTED_IMAGE_SUFFIXES:
        raise ValueError(
            f"Unsupported image format: {image_path.suffix}"
        )

    mime_type = (
        mimetypes.guess_type(image_path.name)[0]
        or "image/png"
    )

    encoded = base64.b64encode(
        image_path.read_bytes()
    ).decode("utf-8")

    return f"data:{mime_type};base64,{encoded}"
