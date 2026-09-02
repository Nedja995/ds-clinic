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

    `documents` carries binary file parts for multimodal providers (Gemini,
    Claude). Text-only providers (Groq, Together, HuggingFace, Ollama) cannot
    consume binary parts — callers must pre-extract document text and supply it
    via `context`. Passing non-empty `documents` to a text-only provider is a
    no-op: the provider logs a warning and falls back to `context`.

    Split-Horizon usage (AD-12):
      - Layer 1 (extraction / text-only providers): populate `context` with
        OCR-extracted or scrubbed text; leave `documents` empty.
      - Layer 2 (cloud reasoning, multimodal providers): populate `documents`
        with file Parts; leave `context` empty or use it for structured JSON
        produced by Layer 1.
    """

    documents: list[Any] = Field(default_factory=list)
    # Pre-extracted text for text-only providers, or structured JSON from
    # Layer 1 passed to Layer 2 as additional context. Empty string means
    # the provider should rely solely on `documents` (multimodal path).
    context: str = Field(default="")
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
