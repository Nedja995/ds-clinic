"""
src/providers/groq_provider.py — GroqProvider concrete implementation (AD-19).

Thin subclass of OpenAICompatibleProvider — Groq exposes a fully
OpenAI-compatible /v1/chat/completions endpoint at api.groq.com.

Text-only: does not accept binary document parts. Callers must supply
pre-extracted text via ProviderRequest.context (Split-Horizon AD-12).
"""

from providers.openai_compatible_provider import OpenAICompatibleProvider
from providers.base import ProviderType
from models import app_settings


class GroqProvider(OpenAICompatibleProvider):
    """LLMProvider for the Groq LPU inference API."""

    _BASE_URL = "https://api.groq.com/openai/v1"
    _CREDENTIAL_NAME = "groq"

    def provider_type(self) -> ProviderType:
        return ProviderType.GROQ

    def _model_name(self) -> str:
        return app_settings.groq_model_name
