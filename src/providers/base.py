"""
src/providers/base.py — Abstract LLMProvider interface and shared data contracts (AD-19).

Owns: ProviderType, ProviderRequest, ProviderResponse, LLMProvider (ABC).

The abstraction boundary sits here: everything above this layer (DSClinic,
ViewModels) speaks only in these types. Everything below (gemini_provider.py,
claude_provider.py, ...) translates to SDK-specific wire formats.

Does NOT own: any SDK import, credential resolution, or config loading.
Those responsibilities belong exclusively to concrete provider classes.
"""

from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any, Iterator

from pydantic import BaseModel, Field

from models.patient import MedicalReportModel


class ProviderType(StrEnum):
    """
    Canonical identifiers for all supported inference backends.

    Priority order for ProviderFactory.available_providers():
    GEMINI → CLAUDE → GROQ → TOGETHER → HUGGINGFACE → OLLAMA
    (v2.9.0 and v2.10.0 add the remaining entries.)
    """

    GEMINI = "gemini"
    CLAUDE = "claude"
    GROQ = "groq"
    TOGETHER = "together"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"


class ProviderRequest(BaseModel):
    """
    Provider-agnostic analysis request.

    `documents` is intentionally typed as list[Any] — Gemini providers receive
    list[genai_types.Part]; Claude providers receive list[dict[str, Any]].
    Each concrete provider casts internally. Mixing types in one request is
    undefined behaviour — callers must ensure homogeneity.
    """

    documents: list[Any] = Field(default_factory=list)
    question: str = Field(default="")
    system_instructions: list[str] = Field(default_factory=list)
    temperature: float = Field(default=1.0)
    max_tokens: int = Field(default=65535)


class ProviderResponse(BaseModel):
    """Normalised response envelope returned from every provider's ask() call."""

    text: str = Field(default="")
    provider: ProviderType = Field(default=ProviderType.GEMINI)
    model_name: str = Field(default="")
    # None when the provider does not expose token-count metadata (e.g. streaming).
    tokens_used: int | None = Field(default=None)


class LLMProvider(ABC):
    """
    Abstract base for all inference provider implementations (AD-19).

    Contract:
    - `analyze()` performs the initial structured document analysis and returns
      a parsed MedicalReportModel. Raises RuntimeError on API or parse failure.
    - `ask()` streams follow-up question chunks as an Iterator[str]. The caller
      is responsible for accumulating chunks if a full string is needed.
    - `is_available()` MUST return False when the required credential is absent
      from the keyring OR when the underlying SDK client failed to initialise.
      ProviderFactory calls this before exposing a provider to the UI.
    - `provider_type()` returns the ProviderType enum value for this instance.

    Concrete subclasses must NOT raise in __init__ when a key is absent —
    they set self._available = False and return early (mirrors the startup-guard
    pattern in api_gemini/client.py and api_claude/client.py).
    """

    @abstractmethod
    def analyze(self, request: ProviderRequest) -> MedicalReportModel:
        """
        Run initial structured document analysis.

        Raises RuntimeError when the client is unavailable or the API returns
        an unparseable response. Never returns None.
        """
        ...

    @abstractmethod
    def ask(self, question: str) -> Iterator[str]:
        """
        Stream a follow-up question response as text chunks.

        The active chat context (history, session) is managed internally by
        each concrete provider. Raises RuntimeError when the client is unavailable.
        """
        ...

    @abstractmethod
    def provider_type(self) -> ProviderType:
        """Return the ProviderType enum value identifying this provider."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """
        Return True only when:
          1. The required API key is present in the OS keyring, AND
          2. The underlying SDK client initialised without error.

        Never raises — returns False on any failure.
        """
        ...
