from __future__ import annotations

from typing import Optional

from google import genai
from google.genai import types

from models import app_settings
from npy.core.logger import setup_logger

logger = setup_logger()


def load_document_from_file(filepath: str) -> Optional[types.Part]:
    logger.info(f"Load Document from filepath: {filepath}.")
    doc: Optional[types.Part] = None

    matches = [
        (ext, doc_type)
        for ext, doc_type in app_settings.ai_supported_input_filetypes.items()
        if filepath.lower().endswith(ext)
    ]

    if matches:
        _doc_extension, doc_type = matches[0]
        doc = types.Part.from_bytes(
            data=open(filepath, "rb").read(),  # noqa: WPS515
            mime_type=doc_type,
        )
    else:
        logger.warning(
            f"Load Document failed because: Format not supported. Skip filepath: {filepath}.."
        )

    return doc
