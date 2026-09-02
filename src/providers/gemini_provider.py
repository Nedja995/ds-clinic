"""
src/providers/gemini_provider.py — GeminiProvider concrete implementation (AD-19).

Owns: GeminiProvider — wraps api_gemini/client.py::MedicalAnalyzerClient behind
the LLMProvider interface. Responsible for credential resolution, client
construction, and translating ProviderRequest/ProviderResponse to/from the
Gemini SDK surface.

Does NOT own: chat session management, prompt engineering, or SDK configuration
details — those remain in api_gemini/client.py. This class is a thin delegation
adapter, not a reimplementation.
"""

from typing import Iterator

from google.genai import types as genai_types

from api_gemini import client as api_gemini_client
from models import (
    app_settings,
    get_credential,
    MedicalReportModel,
    GeminiModelConfig,
    AIServiceConfig,
)
from providers.base import LLMProvider, ProviderRequest, ProviderType
from npy.core.logger import setup_logger

logger = setup_logger()


class GeminiProvider(LLMProvider):
    """
    LLMProvider adapter for the Google Gemini backend.

    Delegates all API calls to MedicalAnalyzerClient. Does not duplicate SDK
    logic — the existing client owns prompt formatting, streaming, and JSON
    schema enforcement.

    Startup guard: if the Gemini API key is absent from the keyring, _client is
    set to None and is_available() returns False. No exception is raised at
    construction time — callers discover availability via is_available().
    """

    def __init__(self) -> None:
        logger.info("[GeminiProvider] Initializing...")
        self._client: api_gemini_client.MedicalAnalyzerClient | None = None

        _api_key = get_credential("gemini") or ""
        if not _api_key:
            logger.warning(
                "[GeminiProvider] Gemini API key absent from keyring — provider unavailable. "
                "Set key via Settings → AI → Google API Key."
            )
            return

        try:
            _config = AIServiceConfig(
                api_key=_api_key,
                model_settings=GeminiModelConfig(
                    model_name=app_settings.ai_model_name,
                    system_instruction=tuple(app_settings.ai_system_instructions),
                    thinking_level=app_settings.ai_thinking_level,
                    temperature=app_settings.ai_model_temperature,
                    top_p=app_settings.ai_model_top_p,
                    max_output_tokens=app_settings.ai_model_max_output_tokens,
                ),
            )
            self._client = api_gemini_client.MedicalAnalyzerClient(config=_config)
            logger.info("[GeminiProvider] Ready.")
        except Exception as exc:
            logger.warning(f"[GeminiProvider] Client failed to initialise: {exc}")
            self._client = None

    # ── LLMProvider interface ──────────────────────────────────────────────

    def provider_type(self) -> ProviderType:
        return ProviderType.GEMINI

    def is_available(self) -> bool:
        # Both the wrapper and the underlying SDK client must be initialised.
        return self._client is not None and self._client.client is not None

    def analyze(self, request: ProviderRequest) -> MedicalReportModel:
        if not self.is_available():
            raise RuntimeError(
                "[GeminiProvider] Provider is not available. "
                "Set your Google API Key in Settings → AI → Google API Key."
            )

        # Gemini documents are genai_types.Part instances — the caller must
        # supply them in that format. Mixing types here is undefined behaviour.
        documents: list[genai_types.Part] = request.documents  # type: ignore[assignment]

        assert self._client is not None
        result = self._client.initial_analysis_report_from_chat_stream(
            documents=documents,
            question=request.question,
        )

        if result is None:
            raise RuntimeError(
                "[GeminiProvider] Gemini returned an empty or unparseable response. "
                "Check logs for raw API output."
            )

        return result

    def ask(self, question: str) -> Iterator[str]:
        if not self.is_available():
            raise RuntimeError(
                "[GeminiProvider] Provider is not available. "
                "Set your Google API Key in Settings → AI → Google API Key."
            )

        assert self._client is not None
        # MedicalAnalyzerClient.ask_followup_question() accumulates the full
        # streamed response internally and returns a single string. We wrap it
        # in a one-shot iterator to satisfy the Iterator[str] contract while
        # keeping the existing client surface unchanged.
        result: str = self._client.ask_followup_question(question)
        return iter([result])
