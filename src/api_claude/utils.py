import base64
from models import app_settings
from npy.core.logger import setup_logger

logger = setup_logger()


def load_document_from_file(filepath: str) -> dict | None:
    """
    Load a document from filepath and return an Anthropic API content block dict.
    
    Returns Anthropic content block format:
      - PDF  -> {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": ...}}
      - Image -> {"type": "image",    "source": {"type": "base64", "media_type": "image/jpeg",     "data": ...}}
    
    Mirrors api_gemini/utils.py::load_document_from_file() but returns dict instead of genai_types.Part.
    """
    logger.info(f"[api_claude] Load Document from filepath: {filepath}.")
    content_block: dict | None = None

    matches = [(ext, doc_type) for ext, doc_type in app_settings.ai_supported_input_filetypes.items()
               if filepath.lower().endswith(ext)]

    if not matches:
        logger.warning(f"[api_claude] Load Document failed: Format not supported. Skip filepath: {filepath}.")
        return None

    _doc_extension, doc_type = matches[0]

    try:
        with open(filepath, "rb") as f:
            raw_bytes = f.read()
        encoded_data = base64.standard_b64encode(raw_bytes).decode("utf-8")
    except (OSError, IOError) as e:
        logger.error(f"[api_claude] Failed to read file '{filepath}': {e}", exc_info=True)
        return None

    # Map MIME type to Anthropic content block type
    # Claude supports: "document" (pdf, txt, csv, html, xml, json, md) and "image" (jpeg, png, webp, gif)
    image_mime_types = {"image/jpeg", "image/png", "image/webp", "image/gif", "image/bmp"}
    # Claude "document" block supports these MIME types natively
    document_mime_types = {
        "application/pdf", "text/plain", "text/html", "text/xml",
        "text/csv", "text/rtf", "application/json"
    }

    if doc_type in image_mime_types:
        content_block = {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": doc_type,
                "data": encoded_data,
            },
        }
    elif doc_type in document_mime_types:
        content_block = {
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": doc_type,
                "data": encoded_data,
            },
        }
    else:
        logger.warning(f"[api_claude] MIME type '{doc_type}' has no Anthropic content block mapping. Skip: {filepath}.")
        return None

    logger.debug(f"[api_claude] Loaded document as '{content_block['type']}' block (mime={doc_type})")
    return content_block
