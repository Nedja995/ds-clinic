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
# Providers added in v2.9.0 and v2.10.0 are registered here as stubs so the
# priority ordering is established once and never reordered later.
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

    Future providers (GROQ, TOGETHER, HUGGINGFACE, OLLAMA) raise
    NotImplementedError from create() until their sub-versions are implemented.
    available_providers() catches and skips these gracefully so the UI is
    never broken by an unimplemented backend.
    """

    @staticmethod
    def create(provider_type: ProviderType) -> LLMProvider:
        """
        Construct and return a provider instance for the given ProviderType.

        Raises NotImplementedError for backends not yet implemented (v2.9.0+).
        Concrete provider __init__ never raises on missing credentials — check
        is_available() on the returned instance before use.
        """
        # Import inside the method to avoid circular imports and to keep SDK
        # dependencies lazy — only the requested provider's SDK is imported.
        if provider_type == ProviderType.GEMINI:
            from providers.gemini_provider import GeminiProvider
            return GeminiProvider()

        if provider_type == ProviderType.CLAUDE:
            from providers.claude_provider import ClaudeProvider
            return ClaudeProvider()

        if provider_type == ProviderType.GROQ:
            raise NotImplementedError(
                "GroqProvider is not yet implemented. Planned for v2.9.2."
            )

        if provider_type == ProviderType.TOGETHER:
            raise NotImplementedError(
                "TogetherProvider is not yet implemented. Planned for v2.9.3."
            )

        if provider_type == ProviderType.HUGGINGFACE:
            raise NotImplementedError(
                "HuggingFaceProvider is not yet implemented. Planned for v2.9.4."
            )

        if provider_type == ProviderType.OLLAMA:
            raise NotImplementedError(
                "OllamaProvider is not yet implemented. Planned for v2.10.2."
            )

        # Exhaustive match — if a new ProviderType is added without a branch,
        # this surfaces it immediately rather than silently returning None.
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
                # Expected for backends planned in future sub-versions.
                logger.debug(f"[ProviderFactory] {provider_type.value}: not yet implemented — skipping")
            except Exception as exc:
                logger.warning(f"[ProviderFactory] {provider_type.value}: unexpected error during availability check: {exc}")

        logger.info(f"[ProviderFactory] Available providers: {[p.value for p in available]}")
        return available
