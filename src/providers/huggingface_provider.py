"""
src/providers/huggingface_provider.py — HuggingFaceProvider concrete implementation (AD-19).

Thin subclass of OpenAICompatibleProvider — the HuggingFace Inference Router
exposes an OpenAI-compatible endpoint at router.huggingface.co/v1, routing
requests to the configured backend provider (Together, Fireworks, etc.).

Text-only: does not accept binary document parts. Callers must supply
pre-extracted text via ProviderRequest.context (Split-Horizon AD-12).

is_available() checks only for keyring key presence — no network ping at
startup, in line with AD-16 ("no-freeze" rule). A failed first call will
surface as a RuntimeError from the parent class.
"""

from providers.openai_compatible_provider import OpenAICompatibleProvider
from providers.base import ProviderType
from models import app_settings


class HuggingFaceProvider(OpenAICompatibleProvider):
    """LLMProvider for the HuggingFace Inference Router (OpenAI-compatible)."""

    _BASE_URL = "https://router.huggingface.co/v1"
    _CREDENTIAL_NAME = "huggingface"

    def provider_type(self) -> ProviderType:
        return ProviderType.HUGGINGFACE

    def _model_name(self) -> str:
        return app_settings.huggingface_model_name
