# Changelog

All notable changes to DSClinic will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

See [TODO.md](TODO.md) for planned versions.

---

## [2.15.0] - Planned — README Engineering Case Study + Architecture Diagrams
## [2.14.0] - Planned — PII Anonymization Improvements + Debug Panel
## [2.13.0] - Planned — pytest Coverage
## [2.12.0] - Planned — Chat Session View Rewrite + New Features
## [2.11.0] - In Progress — Enterprise Multi-Brand / White-Label & Subscription Config
## [2.10.0] - Completed — Local Ollama Provider (16GB VRAM Optimized)
## [2.9.0] - Completed — Groq + Together AI + HuggingFace Cloud Providers
## [2.8.0] - Completed — `src/providers/` LLMProvider Abstraction (Gemini + Claude)
## [2.7.0] - Completed — Patient Record as First-Class Entity & Session Persistence

---

## [2.11.1] - 2026-09-04

### Added
- `src/models/brand.py` — `BrandConfig(BaseModel)` with fields: `clinic_name`, `clinic_subtitle`, `clinic_address`, `logo_path`, `primary_color`, `secondary_color`, `report_header_text`, `report_footer_text`, `report_consent_text`, `subscription_tier` (`"trial"` / `"standard"` / `"enterprise"`).
  - `BrandConfig.load()` — reads `brand.json` from executable root via `get_base_dir_path()`; falls back to built-in defaults silently when file absent.
  - `BrandConfig.save()` — atomic write to `brand.json` via `.tmp` swap; used by Settings UI in v2.11.4.
  - `BrandConfig.resolved_logo_path()` — resolves relative logo paths against executable root (AD-09); returns empty string when file not found so callers skip rendering safely.
  - `BrandConfig.is_feature_allowed(feature)` — subscription tier gate; `_TIER_FEATURES` dict maps tier → allowed feature set; logs denied features at DEBUG level.
  - `BrandConfig.primary_color_rgb()` / `secondary_color_rgb()` — parse hex color strings to `(R, G, B)` tuples for FPDF.
  - `_hex_to_rgb()` — module-level helper; falls back to `(0, 51, 102)` on parse error.
  - `brand_config` singleton initialized on import.
- `brand.json` — default deployable config file at project root with `"MedAI - ViTec"` branding and `"standard"` subscription tier.
- `src/models/__init__.py` — `BrandConfig` and `brand_config` exported.

### Changed
- `pyproject.toml` — version bumped to `2.11.1`.

---

## [2.10.4] - 2026-09-03

### Changed
- `src/providers/factory.py` — replaced `NotImplementedError` stub for `OLLAMA` with lazy import of `OllamaProvider`. `NotImplementedError` catch removed from `available_providers()` (no longer needed — all six providers implemented). Module docstring updated to reflect v2.10.4 completion.

---

## [2.10.3] - 2026-09-03

### Added
- `src/providers/ollama_provider.py` — `OllamaProvider._ensure_model_loaded()`:
  - Unloads the previously active model via `keep_alive=0` before loading a new one — prevents VRAM thrashing on 16 GB budget (AD-13).
  - Checks `ollama.list()` for local model presence; calls `ollama.pull()` only when model is absent — pull runs once on first use, not at startup.
  - Logs VRAM decisions at `DEBUG` level: unload events, pull events, active model changes.
  - `_loaded_model: str` instance attribute tracks last loaded model for unload targeting.

---

## [2.10.2] - 2026-09-03

### Added
- `src/providers/ollama_provider.py` — `OllamaProvider(LLMProvider)` concrete implementation:
  - `__init__`: lazy-imports `ollama`; constructs `ollama.Client(host=app_settings.ollama_base_url)`; pings daemon via `list()` — `_available = True` only when daemon responds. Startup-guard: no exception raised when daemon is down or SDK not installed.
  - `provider_type()` → `ProviderType.OLLAMA`.
  - `is_available()` → `self._available`.
  - `analyze()`: text-only (documents ignored with warning per AD-12); builds system prompt with `_JSON_SCHEMA_SUFFIX`; seeds `_chat_history`; calls `client.chat()`; strips markdown fences; parses `MedicalReportModel`. Raises `RuntimeError` on API or parse failure.
  - `ask()`: appends question to history; streams via `client.chat(stream=True)`; yields chunks; appends accumulated response to history after generator exhaustion.
  - `_model_name()`: returns `app_settings.ollama_model_name`.
  - `_JSON_SCHEMA_SUFFIX`: mirrors `openai_compatible_provider.py` for uniform structured output contract across all providers.

---

## [2.10.1] - 2026-09-03

### Added
- `config.json` — `ollama_initial_model_config` (`llama3.2-vision:q4_0`, `base_url`) and `ollama_supported_models` (5 quantized models: `llama3.2-vision:q4_0`, `llama3.2-vision:q8_0`, `medgemma:q4_0`, `llama3.1:8b-q4_0`, `mistral:7b-q4_0`).
- `src/models/settings.py` — `ollama_model_name: str` and `ollama_base_url: str` writable fields; `ollama_supported_models: Dict[str, str]` static field. `load_unified()` reads all three from `ollama_initial_model_config` / `ollama_supported_models` in `config.json`. `save_unified()` excludes `ollama_supported_models` (static) but persists `ollama_model_name` and `ollama_base_url` (user prefs).
- `src/dsclinic_gui/settings/settings_view_model.py` — `var_ollama_base_url`, `var_ollama_model_name` `tk.StringVar` vars; `ollama_supported_models` list. `update_from_config()` refreshes both from `app_settings`. `save_to_config()` writes both to `app_settings` before `save_unified()`.
- `src/dsclinic_gui/settings/settings_view.py` — new `_build_local_ai_section()` method renders "LOCAL AI (OLLAMA)" card: plain (unmasked) base URL entry with hint label; model combobox populated from `ollama_supported_models`; quantization hint label referencing AD-13. `_setup_ui()` calls `_build_local_ai_section()` between AI and General sections. `_HEIGHT` bumped from 1020 to 1160.

### Changed
- `pyproject.toml` — version bumped to `2.10.1`; `local` optional extra comment updated to reference AD-13 and v2.10.x.

---

## [2.9.4] - 2026-09-02

### Changed
- `src/providers/factory.py` — replaced `NotImplementedError` stubs for `GROQ`, `TOGETHER`, `HUGGINGFACE` with lazy imports of their concrete provider classes. `OLLAMA` stub retained (planned v2.10.2). Updated module docstring.
- `src/providers/__init__.py` — no change to exports; re-written for consistency.

---

## [2.9.3] - 2026-09-02

### Added
- `src/providers/groq_provider.py` — `GroqProvider(OpenAICompatibleProvider)`: `_BASE_URL="https://api.groq.com/openai/v1"`, `_CREDENTIAL_NAME="groq"`, `_model_name()` returns `app_settings.groq_model_name`.
- `src/providers/together_provider.py` — `TogetherProvider(OpenAICompatibleProvider)`: `_BASE_URL="https://api.together.xyz/v1"`, `_CREDENTIAL_NAME="together"`, `_model_name()` returns `app_settings.together_model_name`.
- `src/providers/huggingface_provider.py` — `HuggingFaceProvider(OpenAICompatibleProvider)`: `_BASE_URL="https://router.huggingface.co/v1"`, `_CREDENTIAL_NAME="huggingface"`, `_model_name()` returns `app_settings.huggingface_model_name`. `is_available()` key-only check per AD-16 (no startup network ping).

---

## [2.9.2] - 2026-09-02

### Added
- `src/providers/openai_compatible_provider.py` — `OpenAICompatibleProvider(LLMProvider)`: shared concrete base for all OpenAI-compatible `/v1/chat/completions` backends.
  - Parameterised via `_BASE_URL` and `_CREDENTIAL_NAME` class attributes — subclasses supply these and nothing else.
  - `__init__`: resolves key from keyring via `_CREDENTIAL_NAME`; constructs `openai.OpenAI(base_url=_BASE_URL, api_key=...)`. Startup-guard: `_client = None` when key absent, no exception raised.
  - `analyze(request)`: text-only — `request.documents` ignored with warning (Split-Horizon constraint, AD-12). Builds system prompt from `request.system_instructions` + `_JSON_SCHEMA_SUFFIX`. Builds user message from `request.context` + `request.question`. Seeds `_chat_history`. Calls `client.chat.completions.create()`. Strips markdown fences from response. Parses into `MedicalReportModel` via `model_validate_json()`. Raises `RuntimeError` on API or parse failure.
  - `ask(question)`: appends question to `_chat_history`, streams via `stream=True`, yields chunks, appends accumulated response to history after generator exhausted.
  - `_stream_and_record()`: inner generator that yields chunks and records history atomically on exhaustion.
  - Catches `APIConnectionError`, `APIStatusError`, `APITimeoutError` and wraps as `RuntimeError`.

---

## [2.9.1] - 2026-09-02

### Added
- `src/providers/base.py` — `ProviderRequest.context: str` field added. Carries pre-extracted document text for text-only providers (Groq, Together, HuggingFace, Ollama). Multimodal providers (Gemini, Claude) use `documents`; text-only providers use `context`. Split-Horizon boundary made explicit in data model (AD-12).
- `config.json` — three new provider config sections:
  - `groq_initial_model_config` (`llama-3.3-70b-versatile`), `groq_supported_models` (4 models).
  - `together_initial_model_config` (`meta-llama/Llama-3.3-70B-Instruct-Turbo`), `together_supported_models` (4 models).
  - `huggingface_initial_model_config` (`meta-llama/Llama-3.3-70B-Instruct`), `huggingface_supported_models` (4 models).

### Changed
- `src/models/keyring_manager.py` — added `"groq"` → `"groq_api_key"`, `"together"` → `"together_api_key"`, `"huggingface"` → `"huggingface_api_key"` to `_CREDENTIAL_KEYS`. Module docstring updated.
- `src/models/settings.py` — added `groq_supported_models`, `together_supported_models`, `huggingface_supported_models` dict fields; `groq_model_name`, `together_model_name`, `huggingface_model_name` string fields. `load_unified()` reads all six from `config.json`. `save_unified()` excludes the three supported-model dicts from written JSON.
- `src/dsclinic_gui/settings/settings_view_model.py` — added `var_groq_api_key`, `var_together_api_key`, `var_huggingface_api_key` `tk.StringVar` vars; `update_from_config()` refreshes all three from keyring; `save_to_config()` writes all three via `set_credential()`.
- `src/dsclinic_gui/settings/settings_view.py` — added three `_credential_field()` calls for Groq, Together AI, and HuggingFace below the existing cloud provider fields. `_HEIGHT` bumped from 860 to 1020.
- `pyproject.toml` — version bumped to `2.9.1`; `providers` optional extra comment updated to explain single `openai` SDK covers all three new backends.

---

## [2.8.4] - 2026-09-02

### Changed
- `src/dsclinic.py` — full refactor to route through `ProviderFactory` / `LLMProvider` (AD-19):
  - All direct SDK client imports (`api_gemini_client`, `api_claude_client`, model config types) removed. Only `api_gemini.utils` retained for document loading (Gemini Part format).
  - `DSClinic.__init__` — drops direct `MedicalAnalyzerClient` / `ClaudeAnalyzerClient` construction. Calls `ProviderFactory.available_providers()` and constructs the first available via `ProviderFactory.create()`. `active_provider: LLMProvider | None` attribute introduced; `None` only when no key is configured at startup.
  - `DSClinic.set_active_provider(provider_type: ProviderType) -> None` — new method; constructs provider via factory, validates `is_available()`, raises `ValueError` if unavailable.
  - `DSClinic.get_initial_analysis_report()` — document loading loop unchanged; builds `ProviderRequest` from loaded parts + `app_settings`; delegates to `self.active_provider.analyze(request)`.
  - `DSClinic.ask_followup_question()` — delegates to `self.active_provider.ask(question)`; accumulates `Iterator[str]` chunks into full string for ViewModel compatibility.
  - Module docstring added; inline comments explain the document-format coupling and whitespace-normalisation rationale.

---

## [2.8.3] - 2026-09-02

### Added
- `src/providers/factory.py` — `ProviderFactory` with two static methods:
  - `create(provider_type: ProviderType) -> LLMProvider` — constructs the concrete provider for the given type; raises `NotImplementedError` for `GROQ`, `TOGETHER`, `HUGGINGFACE`, `OLLAMA` (planned in v2.9.x / v2.10.x). Imports are lazy (inside the method) to keep SDK dependencies deferred.
  - `available_providers() -> list[ProviderType]` — iterates `_PROVIDER_PRIORITY` (`GEMINI → CLAUDE → GROQ → TOGETHER → HUGGINGFACE → OLLAMA`), constructs each, calls `is_available()`, returns those that are `True`. `NotImplementedError` and unexpected exceptions are caught and skipped — UI is never broken by an unimplemented backend.

### Changed
- `src/providers/__init__.py` — added `ProviderFactory` to exports and `__all__`.

---

## [2.8.2] - 2026-09-02

### Added
- `src/providers/gemini_provider.py` — `GeminiProvider(LLMProvider)`: delegates to `MedicalAnalyzerClient`; resolves key from keyring; `is_available()` checks both wrapper and SDK client; `ask()` wraps accumulated string in `iter([result])` to satisfy `Iterator[str]` contract.
- `src/providers/claude_provider.py` — `ClaudeProvider(LLMProvider)`: delegates to `ClaudeAnalyzerClient`; resolves key from keyring; `ask()` delegates directly to `ask_followup_stream()` (already an `Iterator[str]`).
- Both providers follow the startup-guard contract: no exception raised in `__init__` when key is absent — `_client` set to `None`, `is_available()` returns `False`.

---

## [2.8.1] - 2026-09-02

### Added
- `src/providers/` — new package directory created.
- `src/providers/__init__.py` — package init; exports `LLMProvider`, `ProviderType`, `ProviderRequest`, `ProviderResponse`.
- `src/providers/base.py` — abstract LLMProvider interface and shared data contracts (AD-19):
  - `ProviderType(StrEnum)` — `GEMINI`, `CLAUDE`, `GROQ`, `TOGETHER`, `HUGGINGFACE`, `OLLAMA`.
  - `ProviderRequest(BaseModel)` — `documents: list[Any]`, `question: str`, `system_instructions: list[str]`, `temperature: float`, `max_tokens: int`.
  - `ProviderResponse(BaseModel)` — `text: str`, `provider: ProviderType`, `model_name: str`, `tokens_used: int | None`.
  - `LLMProvider(ABC)` — abstract methods: `analyze()`, `ask()`, `provider_type()`, `is_available()`.

---

## [2.7.4] - 2026-09-01

### Added
- `src/dsclinic_gui/session_history_view.py` — rewritten as two-tab `ttk.Notebook` sidebar:
  - **Sessions tab:** `+ New Session` button, optional patient filter indicator label, scrollable `tk.Listbox`. Clicking a row calls `view_model.load_session()`. Filter applied when a patient is selected from the Patients tab.
  - **Patients tab:** scrollable `tk.Listbox` listing all patients. Clicking a patient sets the session filter and switches to the Sessions tab (toggle-click clears filter). Inline "New Patient" form at the bottom: full name + date of birth fields + "Save Patient" button. Calls `view_model.save_new_patient()` on submit; clears fields on success. Empty-state labels on both lists.
  - `_filter_patient_id` / `_filter_session_ids` View-local state drives the session filter — no ViewModel involvement required for filter state.
  - `_load_patient_session_ids()` loads `PatientRecord.session_ids` from DB via `view_model._db` for filter construction.
- `src/dsclinic_gui/report_view_models.py` — `var_patients_index`, `on_patients_changed` EventEmitter, `_active_patient_id: str`, `_refresh_patients_index()`, `save_new_patient()`, `set_active_patient()`.
- `src/dsclinic_gui/report_view_models.py` — `_link_session_to_patient()`: idempotently appends `session_id` to `PatientRecord.session_ids` and re-saves whenever `_active_patient_id` is set during `_persist_session()`.
- `src/dsclinic_gui/styles.py` — `SidebarFormLabel.TLabel` style for the "New Patient" section heading.

### Changed
- `src/dsclinic_gui/report_view_models.py` — `_persist_session()` now calls `_link_session_to_patient()` when `_active_patient_id` is set, then `_refresh_sessions_index()`.
- `src/dsclinic_gui/report_view_models.py` — `PatientRecord` imported from `models`.

---

## [2.7.3] - 2026-09-01

### Added
- `src/dsclinic_gui/session_history_view.py` — new `SessionHistoryView(ttk.Frame)` sidebar widget. Subscribes to `on_sessions_changed`; rebuilds `tk.Listbox` from `var_sessions_index` on every update. Clicking a row calls `view_model.load_session(session_id)`. "New Session" button calls `view_model.new_session()`. Empty-state label shown when no sessions exist yet.
- `src/dsclinic_gui/report_view_models.py` — `var_sessions_index: list[dict]` attribute, populated from `_db.sessions.list_index()` on init and refreshed after every `_persist_session()` call.
- `src/dsclinic_gui/report_view_models.py` — `on_sessions_changed: EventEmitter` — fired whenever `var_sessions_index` is refreshed.
- `src/dsclinic_gui/report_view_models.py` — `_refresh_sessions_index()`: reloads index from disk and emits `on_sessions_changed`.
- `src/dsclinic_gui/report_view_models.py` — `load_session(session_id: str)`: loads `ChatSessionModel` from DB, replaces `_model` and `_session`, emits `on_vm_data_changed`.
- `src/dsclinic_gui/report_view_models.py` — `new_session()`: resets all model/session/observable state to defaults, emits `on_vm_data_changed`.
- `src/dsclinic_gui/styles.py` — `SIDEBAR_BG`, `SIDEBAR_STRIP` palette constants; `SidebarPanel.TFrame`, `SidebarStrip.TFrame`, `SidebarTitle.TLabel`, `SidebarEmpty.TLabel` style definitions.

### Changed
- `src/dsclinic_gui/main_container.py` — three-pane layout: `SessionHistoryView` (weight=2) added as leftmost pane; `MedicalReportView` weight reduced from 8 to 6 to preserve proportional feel. Module and class docstrings added.
- `src/dsclinic_gui/report_view_models.py` — `_persist_session()` now calls `_refresh_sessions_index()` after every save so the sidebar stays current.
- `src/dsclinic_gui/report_view_models.py` — `PatientRecord` imported from `models`.

---

## [2.7.2] - 2026-09-01

### Added
- `dsclinic_gui/report_view_models.py` — `self._db: AppDatabase` instantiated once in `DSClinicViewModel.__init__`.
- `dsclinic_gui/report_view_models.py` — `self._session: ChatSessionModel` tracks the active session wrapping the current report and chat history.
- `dsclinic_gui/report_view_models.py` — `self._pending_question: str` stashes the submitted question text so the `FINISHED` handler can build the `ChatMessage` pair without re-reading the (already-cleared) `StringVar`.
- `dsclinic_gui/report_view_models.py` — `_persist_report()`: saves `MedicalReport` to `_db.reports` on analysis completion. Failures logged and swallowed — never propagate to UI.
- `dsclinic_gui/report_view_models.py` — `_persist_session()`: re-saves `ChatSessionModel` to `_db.sessions` after analysis completion and after each Q&A exchange. Syncs `session.report` to current model state before writing.
- `dsclinic_gui/report_view_models.py` — `_apply_progress_event` `FINISHED/MedicalReport` branch: calls `_persist_report` + creates fresh `ChatSessionModel` + calls `_persist_session` immediately after analysis.
- `dsclinic_gui/report_view_models.py` — `_apply_progress_event` `FINISHED/str` branch: appends question + answer `ChatMessage` pair to `_session.chat_history`, clears `_pending_question`, calls `_persist_session`.

### Changed
- `dsclinic_gui/report_view_models.py` — `followup_question_submit()`: stashes question into `self._pending_question` before clearing `var_initial_question`.

---

## [2.7.1] - 2026-09-01

### Added
- `src/models/patient.py` — `PatientRecord(BaseModel)` with fields: `patient_id` (uuid4 hex), `full_name`, `date_of_birth`, `created_at`, `session_ids: list[str]`. First-class persistent entity per AD-18.
- `src/db/app_database.py` — `patients: JsonCollection[PatientRecord]` collection at `app_data/patients/`. Index fields: `patient_id`, `full_name`, `created_at`.
- `src/models/__init__.py` — `PatientRecord` exported from the models package.

### Changed
- `src/models/patient.py` — added module-level docstring explaining ownership boundary and AD-18 join key contract.
- `src/db/app_database.py` — updated module docstring to include `patients/` in directory layout and usage examples.

---

## [2.5.4] - 2026-09-01

### Added
- `pyproject.toml` — migrated all tool configuration into `pyproject.toml` as single source of truth: `[tool.mypy]` (replaces `mypy.ini`), `[tool.pytest.ini_options]`, `[tool.autopep8]`.
- `pyproject.toml` — added `requires-python = ">=3.12,<3.13"`, `authors`, `readme`, `license` fields (mirrors GASSI `pyproject.toml` convention, see AD-21).
- `pyproject.toml` — added `[project.optional-dependencies]`: `claude`, `local`, `providers` extras for opt-in backends.
- `pyproject.toml` — added `[dependency-groups] dev` with `mypy`, `pytest`, `pytest-mock`, `pyinstaller` (install with `uv sync --group dev`).
- `pyproject.toml` — added full runtime dependency set with version pins: `fpdf2`, `presidio-analyzer`, `presidio-anonymizer`, `spacy`, `easyocr`, `Pillow`, `pdf2image`.
- `README.md` — full rewrite: `uv`-based setup (`uv sync`, extras, spaCy model download), keyring credential setup, run commands, mypy, pytest, PyInstaller release builds, project structure, architecture overview.

### Removed
- `mypy.ini` — deleted; all mypy configuration now lives in `[tool.mypy]` inside `pyproject.toml`.
- `README.md` — removed outdated `pip` / `requirements.txt` / Poetry workflow references.

### Changed
- `pyproject.toml` — `[autopep8]` section key renamed to `[tool.autopep8]` (correct TOML tool namespace).

---

## [2.5.3] - 2026-09-01

### Fixed — `mypy --strict src/` now passes with 0 errors across 26 checked files
- `db/json_collection.py` — all bare `dict` replaced with `dict[str, Any]`; `_load_raw_index` return type explicit; `_build_index_entry` node traversal typed correctly.
- `models/ai.py` — `tuple` → `tuple[str, ...]` on both `system_instruction` fields.
- `models/diagnostics.py` — `UserList[T]` parameterised; `ObservableList` fully annotated (`__init__`, `extend`, `__setitem__`, `__delitem__`, `__iter__`).
- `api_gemini/client.py` — `chat_session: Optional[Any]` (SDK has no stable public chat session type); `-> None` added to all methods; `SafetySetting` uses enum members; `system_instruction` passed as `str`.
- `api_gemini/utils.py` — return type `Optional[types.Part]`; `None` initialiser removed.
- `api_claude/client.py` — unused `MessageParam` import removed (type doesn't exist in SDK); `user_content: Any` cast eliminates TypedDict mismatch; all bare `dict` type-args filled; `# type: ignore` codes corrected.
- `api_claude/utils.py` — `dict[str, Any]` throughout; `frozenset[str]` constants typed.
- `dsclinic.py` — `__init__` annotated `-> None`; `ask_followup_question` uses explicit `result: str` assignment to suppress `no-any-return`.
- `dsclinic_gui/report_view_models.py` — `callable` → `Callable[..., Any]`; `mp_input_queue`/`mp_output_queue` annotated as `multiprocessing.Queue[Any]`; `_` calls suppressed with `# type: ignore[name-defined]`.
- `dsclinic_gui/chat_session_view.py` — full annotations on `MarkdownLabel`; `_wheel` parameter typed as `Any`; `anchor` typed as `Literal["e", "w"]`; unused `Optional` import removed; unused `# type: ignore` comments removed.

### Added
- `mypy.ini` — created with `[mypy]` strict config and exclude list for View-layer files deferred to rewrite milestones.

### Removed
- `src/test_guis/` — removed from git tracking via `git rm -r src/test_guis/`.

---

## [2.5.2] - 2026-08-31

### Fixed
- `db/json_collection.py` — all four unguarded I/O sites wrapped in `try/except OSError` / `ValidationError`.
- `models/keyring_manager.py` — `get_credential()` and `set_credential()` wrapped in `keyring.errors.KeyringError`; `delete_credential()` gets additional `KeyringError` branch.
- `dsclinic.py` — `get_initial_analysis_report()`: `None` check on `report_content` before constructing `MedicalReport`; raises `RuntimeError` with user-readable message.

---

## [2.5.1] - 2026-08-31

### Fixed
- `report_view_models.py` — added `append_chat_response(text: str) -> None`; View must never mutate `_model` directly.
- `chat_session_view.py` — replaced direct `_model` mutation with `view_model.append_chat_response(text)`.
- `report_view_models.py` — `execute_export()` wraps PDF generation in `try/except`; emits `on_show_error_message` on failure.

### Changed
- Added `-> None` return type annotations to all previously unannotated ViewModel methods.

---

## [2.6.7] - 2026-08-30

### Security
- `settings.ini` permanently deleted. Both API keys regenerated and written to OS keyring.

---

## [2.6.0] - 2026-08-30 — Secure Credential Management & `settings.ini` Elimination ✅

### Security
- All API keys moved to OS keyring via `keyring_manager.py`. `settings.ini` deleted.

### Changed
- `app_name`/`app_version` sourced from `pyproject.toml` via `importlib.metadata`.
- `GOOGLE_PROJECT_LOCATION` moved to `config.json`.

---

## [2.3.0] - 2026-08-29

### Added
- Unified `src/models/` package. `AppSettings` Pydantic model. Layered `load_unified` / `save_unified`.

### Removed
- Legacy `src/models.py`, `src/models_new/`, `src/config.py`, `src/npy/core/settings_manager.py`.

---

## [2.1.10] - 2026-08-28

### Added
- "SUPPORT" card section in Settings window. Token-optimization filters in `dsclinic.py`.

### Fixed
- Nested-tuple serialization bug on multiple settings saves in `config.json`.
