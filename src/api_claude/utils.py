from __future__ import annotations

import base64
from typing import Any, Optional

from models import app_settings
from npy.core.logger import setup_logger

logger = setup_logger()

_IMAGE_MIME_TYPES: frozenset[str] = frozenset({
    "image/jpeg", "image/png", "image/webp", "image/gif", "image/bmp"
})
_DOCUMENT_MIME_TYPES: frozenset[str] = frozenset({
    "application/pdf", "text/plain", "text/html", "text/xml",
    "text/csv", "text/rtf", "application/json",
})


def load_document_from_file(filepath: str) -> Optional[dict[str, Any]]:
    """
    Load a document from filepath and return an Anthropic API content block dict.

    Returns Anthropic content block format:
      - PDF/doc -> {"type": "document", "source": {"type": "base64", ...}}
      - Image   -> {"type": "image",    "source": {"type": "base64", ...}}

    Mirrors api_gemini/utils.py::load_document_from_file() but returns dict instead
    of genai_types.Part.
    """
    logger.info(f"[api_claude] Load Document from filepath: {filepath}.")

    matches = [
        (ext, doc_type)
        for ext, doc_type in app_settings.ai_supported_input_filetypes.items()
        if filepath.lower().endswith(ext)
    ]

    if not matches:
        logger.warning(
            f"[api_claude] Load Document failed: Format not supported. Skip filepath: {filepath}."
        )
        return None

    _doc_extension, doc_type = matches[0]

    try:
        with open(filepath, "rb") as f:
            raw_bytes = f.read()
        encoded_data = base64.standard_b64encode(raw_bytes).decode("utf-8")
    except OSError as e:
        logger.error(f"[api_claude] Failed to read file '{filepath}': {e}", exc_info=True)
        return None

    content_block: dict[str, Any]

    if doc_type in _IMAGE_MIME_TYPES:
        content_block = {
            "type": "image",
            "source": {"type": "base64", "media_type": doc_type, "data": encoded_data},
        }
    elif doc_type in _DOCUMENT_MIME_TYPES:
        content_block = {
            "type": "document",
            "source": {"type": "base64", "media_type": doc_type, "data": encoded_data},
        }
    else:
        logger.warning(
            f"[api_claude] MIME type '{doc_type}' has no Anthropic content block mapping. "
            f"Skip: {filepath}."
        )
        return None

    logger.debug(
        f"[api_claude] Loaded document as '{content_block['type']}' block (mime={doc_type})"
    )
    return content_block
