"""
src/providers/claude_provider.py — ClaudeProvider concrete implementation (AD-19).

Owns: ClaudeProvider — wraps api_claude/client.py::ClaudeAnalyzerClient behind
the LLMProvider interface. Responsible for credential resolution, client
construction, and translating ProviderRequest/ProviderResponse to/from the
Anthropic SDK surface.

Does NOT own: chat history management, system prompt construction, or JSON
schema enforcement — those remain in api_claude/client.py. This class is a
thin delegation adapter, not a reimplementation.
"""

from typing import Any, Iterator

from api_claude import client as api_claude_client
from models import (
    app_settings,
    get_credential,
    MedicalReportModel,
    ClaudeModelConfig,
    ClaudeAIServiceConfig,
)
from providers.base import LLMProvider, ProviderRequest, ProviderType
from npy.core.logger import setup_logger

logger = setup_logger()


class ClaudeProvider(LLMProvider):
    """
    LLMProvider adapter for the Anthropic Claude backend.

    Delegates all API calls to ClaudeAnalyzerClient. Does not duplicate SDK
    logic — the existing client owns chat history, system prompt with embedded
    JSON schema, and streaming.

    Startup guard: if the Anthropic API key is absent from the keyring, _client
    is set to None and is_available() returns False. No exception is raised at
    construction time.
    """

    def __init__(self) -> None:
        logger.info("[ClaudeProvider] Initializing...")
        self._client: api_claude_client.ClaudeAnalyzerClient | None = None

        _api_key = get_credential("anthropic") or ""
        if not _api_key:
            logger.warning(
                "[ClaudeProvider] Anthropic API key absent from keyring — provider unavailable. "
                "Set key via Settings → AI → Anthropic API Key."
            )
            return

        try:
            _config = ClaudeAIServiceConfig(
                api_key=_api_key,
                model_settings=ClaudeModelConfig(
                    model_name=app_settings.claude_model_name,
                    temperature=app_settings.ai_model_temperature,
                    top_p=app_settings.ai_model_top_p,
                    max_output_tokens=app_settings.ai_model_max_output_tokens,
                ),
            )
            self._client = api_claude_client.ClaudeAnalyzerClient(config=_config)
            logger.info("[ClaudeProvider] Ready.")
        except Exception as exc:
            logger.warning(f"[ClaudeProvider] Client failed to initialise: {exc}")
            self._client = None

    # ── LLMProvider interface ──────────────────────────────────────────────

    def provider_type(self) -> ProviderType:
        return ProviderType.CLAUDE

    def is_available(self) -> bool:
        # Both the wrapper and the underlying Anthropic SDK client must be initialised.
        return self._client is not None and self._client.client is not None

    def analyze(self, request: ProviderRequest) -> MedicalReportModel:
        if not self.is_available():
            raise RuntimeError(
                "[ClaudeProvider] Provider is not available. "
                "Set your Anthropic API Key in Settings → AI → Anthropic API Key."
            )

        # Claude documents are list[dict[str, Any]] content blocks — the caller
        # must supply them in that format. Mixing with genai_types.Part is
        # undefined behaviour.
        documents: list[dict[str, Any]] = request.documents  # type: ignore[assignment]

        assert self._client is not None
        result = self._client.initial_analysis_report_from_chat_stream(
            documents=documents,
            question=request.question,
        )

        if result is None:
            raise RuntimeError(
                "[ClaudeProvider] Claude returned an empty or unparseable response. "
                "Check logs for raw API output."
            )

        return result

    def ask(self, question: str) -> Iterator[str]:
        if not self.is_available():
            raise RuntimeError(
                "[ClaudeProvider] Provider is not available. "
                "Set your Anthropic API Key in Settings → AI → Anthropic API Key."
            )

        assert self._client is not None
        # ClaudeAnalyzerClient.ask_followup_stream() already yields chunks
        # directly — no accumulation wrapper needed here.
        return self._client.ask_followup_stream(question)
