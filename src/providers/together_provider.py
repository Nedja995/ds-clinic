"""
src/providers/together_provider.py — TogetherProvider concrete implementation (AD-19).

Thin subclass of OpenAICompatibleProvider — Together AI exposes a fully
OpenAI-compatible /v1/chat/completions endpoint at api.together.xyz.

Text-only: does not accept binary document parts. Callers must supply
pre-extracted text via ProviderRequest.context (Split-Horizon AD-12).
"""

from providers.openai_compatible_provider import OpenAICompatibleProvider
from providers.base import ProviderType
from models import app_settings


class TogetherProvider(OpenAICompatibleProvider):
    """LLMProvider for the Together AI hosted open-weights inference API."""

    _BASE_URL = "https://api.together.xyz/v1"
    _CREDENTIAL_NAME = "together"

    def provider_type(self) -> ProviderType:
        return ProviderType.TOGETHER

    def _model_name(self) -> str:
        return app_settings.together_model_name
