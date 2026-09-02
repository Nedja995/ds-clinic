"""
src/providers/factory.py — ProviderFactory: provider construction and discovery (AD-19).

Owns: ProviderFactory — static factory for constructing LLMProvider instances
and querying runtime availability across all registered backends.

Does NOT own: credential resolution (that belongs to each concrete provider),
provider-specific config (each provider reads app_settings directly), or UI
state (the provider selector in the chat toolbar reads available_providers()
and calls DSClinic.set_active_provider() — see v2.12.2).
"""

from providers.base import LLMProvider, ProviderType
from npy.core.logger import setup_logger

logger = setup_logger()

# Priority order enforced by available_providers(). Lower index = higher priority.
_PROVIDER_PRIORITY: list[ProviderType] = [
    ProviderType.GEMINI,
    ProviderType.CLAUDE,
    ProviderType.GROQ,
    ProviderType.TOGETHER,
    ProviderType.HUGGINGFACE,
    ProviderType.OLLAMA,
]


class ProviderFactory:
    """
    Static factory for LLMProvider construction and availability discovery.

    Two responsibilities:
    - `create()` — construct a provider instance by ProviderType.
    - `available_providers()` — return the ordered list of providers whose
      is_available() returns True at the current moment (keys in keyring,
      daemons running, etc.).

    OLLAMA raises NotImplementedError until v2.10.x is implemented.
    available_providers() catches and skips it gracefully.
    """

    @staticmethod
    def create(provider_type: ProviderType) -> LLMProvider:
        """
        Construct and return a provider instance for the given ProviderType.

        Imports are lazy (inside the method) to keep SDK dependencies deferred —
        only the requested provider's SDK is imported when that provider is first used.
        Concrete provider __init__ never raises on missing credentials — check
        is_available() on the returned instance before use.
        """
        if provider_type == ProviderType.GEMINI:
            from providers.gemini_provider import GeminiProvider
            return GeminiProvider()

        if provider_type == ProviderType.CLAUDE:
            from providers.claude_provider import ClaudeProvider
            return ClaudeProvider()

        if provider_type == ProviderType.GROQ:
            from providers.groq_provider import GroqProvider
            return GroqProvider()

        if provider_type == ProviderType.TOGETHER:
            from providers.together_provider import TogetherProvider
            return TogetherProvider()

        if provider_type == ProviderType.HUGGINGFACE:
            from providers.huggingface_provider import HuggingFaceProvider
            return HuggingFaceProvider()

        if provider_type == ProviderType.OLLAMA:
            raise NotImplementedError(
                "OllamaProvider is not yet implemented. Planned for v2.10.2."
            )

        # Exhaustive match — surfaces any new ProviderType added without a branch.
        raise ValueError(f"Unknown ProviderType: {provider_type!r}")

    @staticmethod
    def available_providers() -> list[ProviderType]:
        """
        Return the ordered list of ProviderType values whose providers are
        currently available (key in keyring, client initialised, daemon running).

        Priority follows _PROVIDER_PRIORITY. The first entry is the recommended
        default for DSClinic.set_active_provider() on startup.

        Never raises — NotImplementedError (unimplemented backends) and any
        unexpected exception are caught and logged, then skipped.
        """
        available: list[ProviderType] = []

        for provider_type in _PROVIDER_PRIORITY:
            try:
                provider = ProviderFactory.create(provider_type)
                if provider.is_available():
                    available.append(provider_type)
                    logger.debug(f"[ProviderFactory] {provider_type.value}: available")
                else:
                    logger.debug(f"[ProviderFactory] {provider_type.value}: not available (key absent or init failed)")
            except NotImplementedError:
                # Expected for OLLAMA until v2.10.x.
                logger.debug(f"[ProviderFactory] {provider_type.value}: not yet implemented — skipping")
            except Exception as exc:
                logger.warning(f"[ProviderFactory] {provider_type.value}: unexpected error during availability check: {exc}")

        logger.info(f"[ProviderFactory] Available providers: {[p.value for p in available]}")
        return available
