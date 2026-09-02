"""
src/providers — LLMProvider abstraction package (AD-19).

Exports the public interface for the pluggable inference pipeline.
All application code (DSClinic, ViewModels) interacts exclusively with
these symbols — never with SDK-specific client classes directly.
"""

from providers.base import LLMProvider, ProviderType, ProviderRequest, ProviderResponse
from providers.factory import ProviderFactory

__all__ = [
    "LLMProvider",
    "ProviderType",
    "ProviderRequest",
    "ProviderResponse",
    "ProviderFactory",
]
