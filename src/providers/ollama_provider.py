"""
src/providers/ollama_provider.py — OllamaProvider: local Ollama daemon integration (AD-13, AD-19).

Owns: OllamaProvider — LLMProvider implementation for the local Ollama daemon.
Handles model availability checking, load-on-demand pulling, VRAM sequential
guard via model unloading, and streaming chat responses.

Does NOT own: credential management — Ollama requires no API key. Connection
config (base_url, model_name) lives in app_settings as plain writable fields,
not the OS keyring. Does NOT extend OpenAICompatibleProvider — the ollama
Python SDK has a distinct API surface from openai.OpenAI.

Text-only constraint (v2.10.x): ProviderRequest.documents is ignored. Callers
must supply pre-extracted text via ProviderRequest.context. Vision multimodal
path (passing image bytes to llama3.2-vision via the ollama SDK images= param)
is a future milestone; stubs are in v2.14.3.

Split-Horizon role (AD-12): Layer 1 — privacy-preserving local extraction and
anonymization. No patient data leaves the machine when this provider is active.
"""

import json
from typing import Any, Iterator

from models.patient import MedicalReportModel
from models import app_settings
from providers.base import LLMProvider, ProviderRequest, ProviderType
from npy.core.logger import setup_logger

logger = setup_logger()

# JSON schema suffix mirroring openai_compatible_provider.py so all providers
# enforce the same structured output contract regardless of backend.
_JSON_SCHEMA_SUFFIX = """

Respond ONLY with a valid JSON object matching this exact schema — no markdown, no explanation:
{
  "patient_name": "string",
  "current_date": "string",
  "disease_diagnosis": "string",
  "diagnosis_summarized": "string",
  "diagnosis": "string",
  "expert_opinion_diagnosis_summarized": "string",
  "recommended_therapy_and_advice_summarized": "string",
  "where_is_the_problem": "string",
  "summary": "string",
  "cause_of_problem": "string",
  "cause_of_problem_detailed": "string",
  "cause_of_problem_summarized": "string",
  "problem_defined": "string",
  "critical_findings": [
    {
      "opinion_and_diagnosis": "string",
      "parameter": "string",
      "value": "string",
      "status": "string",
      "significance": "string",
      "parameter_and_value": "string",
      "diagnosis": "string",
      "where_is_the_problem": "string",
      "summary": "string",
      "cause_of_problem": "string",
      "cause_of_problem_detailed": "string",
      "cause_of_problem_summarized": "string"
    }
  ]
}"""


class OllamaProvider(LLMProvider):
    """
    LLMProvider for the local Ollama inference daemon.

    Availability contract: is_available() pings the daemon via ollama.list()
    rather than checking the keyring — no API key required. Returns False when
    the daemon is not running or unreachable.

    Load-on-demand: models are pulled via ollama.pull() only when first needed,
    not at startup, to avoid blocking the UI. Previous model is unloaded before
    the new one loads to prevent VRAM thrashing on a 16 GB budget (AD-13).

    Chat history: maintained in _chat_history across ask() calls within the
    same provider instance, matching the session-scoped pattern of all other
    providers.
    """

    def __init__(self) -> None:
        logger.info("[OllamaProvider] Initializing...")
        self._available: bool = False
        self._client: Any = None  # ollama.Client — typed as Any to defer import
        self._chat_history: list[dict[str, str]] = []
        # Track the last loaded model name so we can unload it before switching.
        self._loaded_model: str = ""

        try:
            import ollama  # lazy import — only loaded when Ollama provider is requested
            _base_url = app_settings.ollama_base_url or "http://localhost:11434"
            self._client = ollama.Client(host=_base_url)
            # Ping the daemon — list() raises if it's not running.
            self._client.list()
            self._available = True
            logger.info(f"[OllamaProvider] Daemon reachable at {_base_url}")
        except ImportError:
            logger.warning(
                "[OllamaProvider] 'ollama' package not installed. "
                "Install with: uv sync --extra local"
            )
        except Exception as exc:
            # Daemon not running or unreachable — not an error worth surfacing at startup.
            logger.info(f"[OllamaProvider] Daemon not available: {exc}")

    # ── LLMProvider interface ──────────────────────────────────────────────

    def provider_type(self) -> ProviderType:
        return ProviderType.OLLAMA

    def is_available(self) -> bool:
        return self._available

    def analyze(self, request: ProviderRequest) -> MedicalReportModel:
        if not self.is_available():
            raise RuntimeError(
                "[OllamaProvider] Daemon is not reachable. "
                "Start Ollama (ollama serve) and verify the base URL in Settings → Local AI."
            )

        # Text-only in v2.10.x — vision multimodal path planned for v2.14.3.
        if request.documents:
            logger.warning(
                "[OllamaProvider] request.documents is non-empty but this provider "
                "is text-only in v2.10.x — documents are ignored. "
                "Populate request.context with pre-extracted text (Split-Horizon AD-12)."
            )

        _model = self._model_name()
        self._ensure_model_loaded(_model)

        _system = " ".join(request.system_instructions) + _JSON_SCHEMA_SUFFIX
        _user_parts: list[str] = []
        if request.context:
            _user_parts.append(f"Document content:\n{request.context}")
        if request.question:
            _user_parts.append(request.question)
        _user_content = "\n\n".join(_user_parts) if _user_parts else "Analyze the provided medical data."

        # Seed history for the session so subsequent ask() calls have context.
        self._chat_history = [
            {"role": "system", "content": _system},
            {"role": "user",   "content": _user_content},
        ]

        assert self._client is not None
        try:
            response = self._client.chat(
                model=_model,
                messages=self._chat_history,
                options={
                    "temperature": request.temperature,
                    "num_predict": min(request.max_tokens, 8192),
                },
            )
        except Exception as exc:
            raise RuntimeError(f"[OllamaProvider] chat() call failed: {exc}") from exc

        _raw: str = response["message"]["content"] if isinstance(response, dict) else response.message.content
        self._chat_history.append({"role": "assistant", "content": _raw})

        # Strip markdown fences — some models wrap JSON output regardless of the system prompt.
        _clean = _raw.strip()
        if _clean.startswith("```"):
            _clean = _clean.split("\n", 1)[-1]
            _clean = _clean.rsplit("```", 1)[0].strip()

        try:
            return MedicalReportModel.model_validate_json(_clean)
        except Exception as exc:
            logger.error(
                f"[OllamaProvider] Failed to parse response as MedicalReportModel: {exc}\n"
                f"Raw response (first 500 chars): {_raw[:500]}"
            )
            raise RuntimeError(
                "[OllamaProvider] Response could not be parsed into a medical report. "
                "Check logs for raw model output. Consider a larger/more capable model."
            ) from exc

    def ask(self, question: str) -> Iterator[str]:
        if not self.is_available():
            raise RuntimeError(
                "[OllamaProvider] Daemon is not reachable. "
                "Start Ollama and verify the base URL in Settings → Local AI."
            )

        _model = self._model_name()
        self._ensure_model_loaded(_model)

        self._chat_history.append({"role": "user", "content": question})

        assert self._client is not None
        try:
            stream = self._client.chat(
                model=_model,
                messages=self._chat_history,
                stream=True,
            )
        except Exception as exc:
            raise RuntimeError(f"[OllamaProvider] Streaming chat() failed: {exc}") from exc

        _accumulated: list[str] = []

        def _stream_and_record() -> Iterator[str]:
            for chunk in stream:
                # Ollama streaming chunks are dicts or response objects.
                _delta: str
                if isinstance(chunk, dict):
                    _delta = chunk.get("message", {}).get("content", "")
                else:
                    _delta = chunk.message.content or ""
                if _delta:
                    _accumulated.append(_delta)
                    yield _delta
            # Append full response to history after generator is exhausted,
            # so the next ask() call has the complete context.
            self._chat_history.append(
                {"role": "assistant", "content": "".join(_accumulated)}
            )

        return _stream_and_record()

    # ── Internal helpers ───────────────────────────────────────────────────

    def _model_name(self) -> str:
        return app_settings.ollama_model_name

    def _ensure_model_loaded(self, model_name: str) -> None:
        """
        Pull the model if not already present, then unload the previous model
        to free VRAM before loading the new one (load-on-demand, AD-13).

        Ollama handles quantization automatically via the model tag suffix
        (e.g. :q4_0, :q8_0) — no explicit quantization API call is needed.
        """
        assert self._client is not None

        # Unload previous model from VRAM before loading the new one.
        # keep_alive=0 tells Ollama to evict the model immediately.
        if self._loaded_model and self._loaded_model != model_name:
            try:
                logger.debug(
                    # load-on-demand: only one model in VRAM at a time — see AD-13
                    f"[OllamaProvider] Unloading '{self._loaded_model}' to free VRAM before loading '{model_name}'"
                )
                self._client.chat(
                    model=self._loaded_model,
                    messages=[{"role": "user", "content": ""}],
                    options={"keep_alive": 0},
                )
            except Exception as exc:
                # Non-fatal — previous model may have already been evicted by Ollama.
                logger.debug(f"[OllamaProvider] Unload attempt for '{self._loaded_model}' returned: {exc}")

        # Pull model if not locally available — runs only the first time.
        try:
            _local_models = self._client.list()
            _local_names: list[str] = []
            if isinstance(_local_models, dict):
                _local_names = [m.get("name", "") for m in _local_models.get("models", [])]
            else:
                _local_names = [m.model for m in _local_models.models]

            if model_name not in _local_names:
                logger.info(
                    f"[OllamaProvider] Model '{model_name}' not found locally — pulling. "
                    "This may take several minutes on first use."
                )
                self._client.pull(model_name)
                logger.info(f"[OllamaProvider] Pull complete: '{model_name}'")
        except Exception as exc:
            # Pull failure is non-fatal here — chat() will surface a clear error
            # if the model is genuinely missing after the pull attempt.
            logger.warning(f"[OllamaProvider] Model check/pull failed for '{model_name}': {exc}")

        self._loaded_model = model_name
        logger.debug(f"[OllamaProvider] Active model: '{model_name}'")
