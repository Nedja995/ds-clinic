from google import genai
from google.genai import types

import config
from npy.core.logger import setup_logger

logger = setup_logger()

def load_document_from_file(filepath: str) -> genai.types.Part:
    logger.info(f"Load Document from filepath: {filepath}.")
    doc: types.Part = None

    matches = [(doc_type, ext) for doc_type, ext in config.AI_SUPPORTED_INPUT_FILETYPES.items() if filepath.lower().endswith(ext)]
    
    if matches:
        doc_type, doc_extension = matches[0]
        doc = types.Part.from_bytes(data=open(filepath, "rb").read(), mime_type=doc_type)
    else:
        logger.warning(f"Load Document failed because: Format not supported. Skip filepath: {filepath}..")
        pass

    return doc
