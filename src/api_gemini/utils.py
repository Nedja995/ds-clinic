from google import genai
from google.genai import types

import config
from logger import setup_logger

logger = setup_logger()

def load_document_from_file(filepath: str) -> genai.types.Part:
    logger.info(f"Load Document from filepath: {filepath}.")
    doc: types.Part = None
    # Ensure extensions have a dot prefix for endswith() to work correctly
    supported_exts = tuple(f".{ext.lstrip('.')}" for ext in config.SUPPORTED_EXTENSIONS)
    doc_extension = [ext for ext in supported_exts if filepath.lower().endswith(ext)]

    if doc_extension and len(doc_extension) > 0:
        # print(f"\n---- |GEMINI||DEBUG| Document format supported: {doc_extension[0]}.")
        if doc_extension[0] in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tif", ".tiff", ".svg"]:
            # Document is Image file
            doc = types.Part.from_bytes(data=open(filepath, "rb").read(), mime_type="image/jpeg")
        elif doc_extension[0] == ".pdf":
            # Document is PDF file
            doc = types.Part.from_bytes(data=open(filepath, "rb").read(), mime_type="application/pdf")
    else:
        logger.warning(f"Load Document failed because: Format not supported. Skip filepath: {filepath}..")
        pass

    return doc
