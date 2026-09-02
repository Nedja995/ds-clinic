"""
src/providers/openai_compatible_provider.py — Shared base for OpenAI-compatible providers (AD-19).

Owns: OpenAICompatibleProvider — concrete LLMProvider for any endpoint that
speaks the OpenAI /v1/chat/completions wire format. Parameterised by base_url,
credential name, and model name — subclasses supply these and nothing else.

Supported backends (all share this implementation):
  - Groq          base_url="https://api.groq.com/openai/v1"
  - Together AI   base_url="https://api.together.xyz/v1"
  - HuggingFace   base_url="https://router.huggingface.co/v1"

Does NOT own: multimodal document ingestion — these providers accept text only.
Callers must populate ProviderRequest.context with pre-extracted document text
before routing to any subclass of this provider (Split-Horizon Layer 1/2, AD-12).
If request.documents is non-empty it is silently ignored with a warning.

Does NOT own: chat session persistence — the message history is kept in
_chat_history on this instance. The instance is constructed fresh per analysis
session by ProviderFactory / DSClinic.set_active_provider(), so history is
naturally scoped to the session lifetime.
"""

import json
from typing import Iterator

from openai import OpenAI
from openai import APIConnectionError, APIStatusError, APITimeoutError

from models.patient import MedicalReportModel
from models.keyring_manager import get_credential
from providers.base import LLMProvider, ProviderRequest, ProviderType
from npy.core.logger import setup_logger

logger = setup_logger()

# System prompt suffix injected for analyze() calls to enforce JSON output.
# The leading newline is intentional — it separates it cleanly from any
# caller-supplied system instructions.
_JSON_SCHEMA_SUFFIX = """

Respond ONLY with a valid JSON object matching this exact schema — no markdown, no explanation:
{
  "patient_name": "string",
  "current_date": "string",
  "disease_diagnosis": "string",
  "diagnosis_summarized": "string",
  "diagnosis": "string",
  "expert_opinion_diagnosis_summarized": "string",
  "recommended_therapy_and_advice_summarized": "string",
  "where_is_the_problem": "string",
  "summary": "string",
  "cause_of_problem": "string",
  "cause_of_problem_detailed": "string",
  "cause_of_problem_summarized": "string",
  "problem_defined": "string",
  "critical_findings": [
    {
      "opinion_and_diagnosis": "string",
      "parameter": "string",
      "value": "string",
      "status": "string",
      "significance": "string",
      "parameter_and_value": "string",
      "diagnosis": "string",
      "where_is_the_problem": "string",
      "summary": "string",
      "cause_of_problem": "string",
      "cause_of_problem_detailed": "string",
      "cause_of_problem_summarized": "string"
    }
  ]
}"""


class OpenAICompatibleProvider(LLMProvider):
    """
    LLMProvider for any OpenAI-compatible /v1/chat/completions endpoint.

    Subclasses must implement provider_type() and supply _BASE_URL and
    _CREDENTIAL_NAME class attributes. Everything else is handled here.

    Text-only constraint: request.documents is ignored. Callers must pass
    pre-extracted text in request.context (Split-Horizon Layer 1/2 pattern).

    Chat history: _chat_history accumulates messages across ask() calls within
    the same provider instance, mirroring the session-scoped pattern used by
    GeminiProvider and ClaudeProvider.
    """

    # Subclasses override these two class attributes.
    _BASE_URL: str = ""
    _CREDENTIAL_NAME: str = ""

    def __init__(self) -> None:
        logger.info(f"[{self.__class__.__name__}] Initializing...")
        self._client: OpenAI | None = None
        self._chat_history: list[dict[str, str]] = []

        _api_key = get_credential(self._CREDENTIAL_NAME) or ""
        if not _api_key:
            logger.warning(
                f"[{self.__class__.__name__}] API key absent from keyring "
                f"(credential: '{self._CREDENTIAL_NAME}') — provider unavailable. "
                "Set key via Settings → AI."
            )
            return

        try:
            self._client = OpenAI(base_url=self._BASE_URL, api_key=_api_key)
            logger.info(f"[{self.__class__.__name__}] Ready — base_url={self._BASE_URL}")
        except Exception as exc:
            logger.warning(f"[{self.__class__.__name__}] Client failed to initialise: {exc}")
            self._client = None

    # ── LLMProvider interface ──────────────────────────────────────────────

    def is_available(self) -> bool:
        return self._client is not None

    def analyze(self, request: ProviderRequest) -> MedicalReportModel:
        if not self.is_available():
            raise RuntimeError(
                f"[{self.__class__.__name__}] Provider is not available. "
                "Set the required API key in Settings → AI."
            )

        # Text-only providers cannot consume binary document Parts.
        # Log a warning so the developer sees the misconfiguration immediately.
        if request.documents:
            logger.warning(
                f"[{self.__class__.__name__}] request.documents is non-empty but this provider "
                "is text-only — documents are ignored. Populate request.context with "
                "pre-extracted text instead (Split-Horizon Layer 1/2, AD-12)."
            )

        _system = " ".join(request.system_instructions) + _JSON_SCHEMA_SUFFIX
        _user_parts: list[str] = []
        if request.context:
            _user_parts.append(f"Document content:\n{request.context}")
        if request.question:
            _user_parts.append(request.question)
        _user_content = "\n\n".join(_user_parts) if _user_parts else "Analyze the provided medical data."

        # Seed history for the session so ask() continuations have context.
        self._chat_history = [
            {"role": "system", "content": _system},
            {"role": "user",   "content": _user_content},
        ]

        assert self._client is not None
        try:
            response = self._client.chat.completions.create(
                model=self._model_name(),
                messages=self._chat_history,  # type: ignore[arg-type]
                temperature=request.temperature,
                max_tokens=min(request.max_tokens, 8192),
            )
        except (APIConnectionError, APIStatusError, APITimeoutError) as exc:
            raise RuntimeError(
                f"[{self.__class__.__name__}] API call failed: {exc}"
            ) from exc

        _raw = response.choices[0].message.content or ""
        self._chat_history.append({"role": "assistant", "content": _raw})

        # Strip markdown fences that some providers wrap around JSON output.
        _clean = _raw.strip()
        if _clean.startswith("```"):
            _clean = _clean.split("\n", 1)[-1]
            _clean = _clean.rsplit("```", 1)[0].strip()

        try:
            return MedicalReportModel.model_validate_json(_clean)
        except Exception as exc:
            logger.error(
                f"[{self.__class__.__name__}] Failed to parse response as MedicalReportModel: {exc}\n"
                f"Raw response (first 500 chars): {_raw[:500]}"
            )
            raise RuntimeError(
                f"[{self.__class__.__name__}] Response could not be parsed into a medical report. "
                "Check logs for raw API output."
            ) from exc

    def ask(self, question: str) -> Iterator[str]:
        if not self.is_available():
            raise RuntimeError(
                f"[{self.__class__.__name__}] Provider is not available. "
                "Set the required API key in Settings → AI."
            )

        self._chat_history.append({"role": "user", "content": question})

        assert self._client is not None
        try:
            stream = self._client.chat.completions.create(
                model=self._model_name(),
                messages=self._chat_history,  # type: ignore[arg-type]
                stream=True,
            )
        except (APIConnectionError, APIStatusError, APITimeoutError) as exc:
            raise RuntimeError(
                f"[{self.__class__.__name__}] Streaming API call failed: {exc}"
            ) from exc

        # Accumulate the full response so we can append it to history after
        # streaming — the iterator yields chunks to the caller in real time.
        _accumulated: list[str] = []

        def _stream_and_record() -> Iterator[str]:
            for chunk in stream:
                _delta = chunk.choices[0].delta.content or ""
                if _delta:
                    _accumulated.append(_delta)
                    yield _delta
            # History update happens after the generator is exhausted.
            self._chat_history.append(
                {"role": "assistant", "content": "".join(_accumulated)}
            )

        return _stream_and_record()

    def _model_name(self) -> str:
        """Return the configured model name for this provider. Overridden by subclasses."""
        raise NotImplementedError
