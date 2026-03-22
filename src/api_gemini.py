##
# api_gemini.py — Gemini API integration for DSClinic
# Responsibilities:
#   - Client lifecycle (gemini_client_connect)
#   - Ordered model-fallback on "model busy" / high-demand errors  (analyze_docs)
#   - Pure analysis call with no retry logic                       (analyze_lab_result_docs)
#   - analyze_docs2 kept as backward-compat shim
#
from typing import List
import json

from google import genai
from google.genai import types

import config


# ---------------------------------------------------------------------------
# Gemini runtime settings
# ---------------------------------------------------------------------------
ARG_GEMINI_THINKING_LEVEL: types.ThinkingLevel = types.ThinkingLevel[
    config.ARG_GEMINI_THINKING_LEVEL_STR]

CONST_INPUT_SUPPORTED_EXTENSIONS: list = [".jpg", ".jpeg", ".png", ".pdf"]

# Ordered fallback list — tried in sequence on "model busy" errors
MODEL_FALLBACK_ORDER: List[str] = [
    config.GEMINI_MODELS.GEMINI_3_PRO_PREVIEW,
    config.GEMINI_MODELS.GEMINI_3_FLASH_PREVIEW,
    config.GEMINI_MODELS.GEMINI_2_5_PRO,
    config.GEMINI_MODELS.GEMINI_2_5_FLASH,
]

# Substrings that indicate the model is temporarily unavailable
_BUSY_SIGNALS = ("high demand", "model is overloaded", "overloaded", "503", "resource exhausted")


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------
def gemini_client_connect() -> genai.Client:
    print("---------- |GEMINI| Client initialization begin. ----------")
    try:
        client = genai.Client(api_key=config.GOOGLE_API_KEY)
        print("---------- |GEMINI| Client initialization success. ----------")
        return client
    except Exception as e:
        print(f"---------- |GEMINI||ERROR| Client initialization failed: {e} ----------")
        raise


# ---------------------------------------------------------------------------
# Document loader
# ---------------------------------------------------------------------------
def load_document(filepath: str) -> types.Part | None:
    print(f"---- |GEMINI||DEBUG| Load Document: {filepath}")
    ext = next(
        (e for e in CONST_INPUT_SUPPORTED_EXTENSIONS if filepath.lower().endswith(e)),
        None
    )
    if ext is None:
        print(f"---- |GEMINI||WARNING| Unsupported format, skipping: {filepath}")
        return None

    with open(filepath, "rb") as fh:
        data = fh.read()

    if ext in (".jpg", ".jpeg", ".png"):
        return types.Part.from_bytes(data=data, mime_type="image/jpeg")
    if ext == ".pdf":
        return types.Part.from_bytes(data=data, mime_type="application/pdf")
    return None


# ---------------------------------------------------------------------------
# Public entry point — owns client lifecycle + model-fallback retry loop
# ---------------------------------------------------------------------------
def analyze_docs(
    ai_task_description: str = config.ARG_AI_TASK_DESCRIPTION,
    documents_filepaths: List[str] = [],
) -> dict:
    """
    Try each model in MODEL_FALLBACK_ORDER.
    On "model busy" errors advance to the next model.
    Any other exception propagates immediately.
    Returns {} if all models are exhausted.
    """
    client = gemini_client_connect()
    try:
        for model_name in MODEL_FALLBACK_ORDER:
            print(f"\n---------- |GEMINI| Attempting model: {model_name} ----------")
            try:
                result = analyze_lab_result_docs(
                    client=client,
                    model_name=model_name,
                    thinking_level=ARG_GEMINI_THINKING_LEVEL,
                    task_description=ai_task_description,
                    documents_filepaths=documents_filepaths,
                )
                print(f"---------- |GEMINI| Analysis success with model: {model_name} ----------")
                return result
            except Exception as e:
                err_lower = str(e).lower()
                if any(sig in err_lower for sig in _BUSY_SIGNALS):
                    print(f"---------- |GEMINI||WARN| Model {model_name} busy — trying next. Error: {e}")
                    continue
                # Non-busy error — do not swallow, let caller decide
                raise

        print("---------- |GEMINI||FATAL| All models are busy. Try again later. ----------")
        return {}
    finally:
        client.close()


# ---------------------------------------------------------------------------
# Pure analysis function — NO client management, NO retry, raises on error
# ---------------------------------------------------------------------------
def analyze_lab_result_docs(
    client: genai.Client,
    model_name: str = config.ARG_GEMINI_MODEL_NAME,
    thinking_level: genai.types.ThinkingLevel = ARG_GEMINI_THINKING_LEVEL,
    task_description: str = config.ARG_AI_TASK_DESCRIPTION,
    documents_filepaths: List[str] = [],
) -> dict:
    """
    Execute one Gemini request with the supplied client + model.

    Contract:
      - Does NOT create or close the client.
      - Does NOT catch "model busy" errors — raises them so the caller
        (analyze_docs) can advance to the next model in the fallback list.
      - Returns a parsed dict on success, raises on any failure.
    """
    print(f"\n---------- |GEMINI||INFO| analyze_lab_result_docs ----------")
    print(f"  thinking_level : {thinking_level}")
    print(f"  model          : {model_name}")
    print(f"  documents      : {documents_filepaths}")

    # ---- Build document parts ------------------------------------------------
    parts: List[types.Part] = []
    for filepath in documents_filepaths:
        doc = load_document(filepath)
        if doc:
            parts.append(doc)
        else:
            print(f"  |WARN| Skipping unloadable document: {filepath}")

    parts.append(types.Part.from_text(text=task_description))

    contents = [types.Content(role="user", parts=parts)]

    tools = [types.Tool(google_search=types.GoogleSearch())]

    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_level=thinking_level),
        temperature=config.ARG_GEMINI_MODEL_TEMPERATURE,
        top_p=config.ARG_GEMINI_MODEL_TOP_P,
        max_output_tokens=config.ARG_GEMINI_MODEL_MAX_OUTPUT_TOKENS,
        response_mime_type="application/json",
        safety_settings=[
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH",        threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT",   threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT",   threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT",          threshold="OFF"),
        ],
        tools=tools,
    )


    # ---- Stream response -----------------------------------------------------
    print("------- |GEMINI||INFO| Starting generate_content_stream request.")
    raw_text = ""

    # NOTE: Any exception here (including "high demand" / 503) propagates to
    # the caller (analyze_docs), which handles the model-fallback loop.
    for chunk in client.models.generate_content_stream(
        model=model_name,
        contents=contents,
        config=generate_content_config,
    ):
        # Guard: skip chunks with no usable content
        candidates = getattr(chunk, "candidates", None)
        if not candidates:
            continue
        content_obj = getattr(candidates[0], "content", None)
        if not content_obj:
            continue
        chunk_parts = getattr(content_obj, "parts", None)
        if not chunk_parts:
            continue

        # response.text raises if finish_reason is not OK — let it propagate
        try:
            raw_text += chunk.text
        except Exception as chunk_err:
            print(f"  |WARN| Skipping chunk — could not read .text: {chunk_err}")
            continue

    print("------- |GEMINI||INFO| Stream finished.")

    # ---- Parse JSON ----------------------------------------------------------
    try:
        result = json.loads(raw_text)
        print("----- |GEMINI| Response JSON parsed successfully.")
        return result
    except json.JSONDecodeError as e:
        print(f"----- |GEMINI||ERROR| JSON decode failed: {e}")
        print(f"      Raw response snippet: {raw_text[:300]!r}")
        raise ValueError(f"Gemini returned non-JSON response: {e}") from e
