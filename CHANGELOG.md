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
## [2.11.0] - Completed — Enterprise Multi-Brand / White-Label & Subscription Config
## [2.10.0] - Completed — Local Ollama Provider (16GB VRAM Optimized)
## [2.9.0] - Completed — Groq + Together AI + HuggingFace Cloud Providers
## [2.8.0] - Completed — `src/providers/` LLMProvider Abstraction (Gemini + Claude)
## [2.7.0] - Completed — Patient Record as First-Class Entity & Session Persistence

---

## [2.12.2] - 2026-09-05

### Added
- `src/dsclinic_gui/report_view_models.py`:
  - `from providers import ProviderFactory, ProviderType` import added.
  - `var_active_provider: tk.StringVar` — initialised from `dsclinicapp.active_provider.provider_type().value` at startup (empty string when no provider is configured). The chat toolbar Combobox binds to this var so the displayed selection always reflects the live active provider.
  - `available_provider_names() -> list[str]` — wraps `ProviderFactory.available_providers()`; returns `[p.value for p in ...]`. Called by the Combobox `postcommand` on every open so runtime changes (Ollama daemon start, new API key) are reflected without restart. Never raises — returns empty list on error.
  - `set_provider_by_name(name: str) -> None` — resolves `ProviderType(name)`, calls `dsclinicapp.set_active_provider()`; on `ValueError` emits `on_show_error_message` and restores `var_active_provider` to the actual current provider so the Combobox doesn't show a provider that isn't active.
- `src/dsclinic_gui/chat_session_view.py`:
  - `ChatSessionView._build_header()` — extracted from `_build_ui()` as a named private method. Builds the header strip with the "CHAT ASISTENT" title label (left) and the provider selector block (right).
  - `ChatSessionView.cmb_provider: ttk.Combobox` — `state="readonly"`, `width=14`, bound to `view_model.var_active_provider`. `postcommand` calls `_refresh_provider_list()`. `<<ComboboxSelected>>` calls `_on_provider_selected()`.
  - `ChatSessionView._refresh_provider_list()` — calls `view_model.available_provider_names()` and sets `cmb_provider.configure(values=...)`. Also called once at build time so the list is not empty before first open.
  - `ChatSessionView._on_provider_selected(event)` — reads `view_model.var_active_provider.get()` and calls `view_model.set_provider_by_name()`.
  - `ChatSessionView._update_input_state()` — extended to set `cmb_provider` to `"disabled"` while `var_is_analyzing` is `True`; `"readonly"` when idle. Prevents provider switching mid-stream.
  - `ent_message` — `<Return>` key binding added: calls `_on_send()` so the user can submit with Enter as well as the button.
  - Module docstring updated with provider selector section.

### Changed
- `src/dsclinic_gui/styles.py`:
  - `ChatUser.TFrame` — `background` changed from `ACCENT_LT` to `ACCENT`.
  - `ChatUser.TLabel` — `background` changed from `ACCENT_LT` to `ACCENT`; `foreground` changed from `TEXT` to `WHITE`. User bubbles now render as solid blue with white text to visually contrast with bot bubbles.
- `pyproject.toml` — version bumped to `2.12.2`.

---

## [2.12.1] - 2026-09-04

### Added
- `src/models/diagnostics.py` — `TaskStatus.CHUNK` enum member added. Carries a partial streaming text fragment in `ProgressEvent.message`. Multiple CHUNK events precede a single FINISHED event per follow-up turn.
- `src/dsclinic_gui/constants.py` — `CHAT_STREAM_POLL_INTERVAL_MS: int = 100`. Dedicated poll interval for the streaming chat queue, independent of the 1 s analysis queue interval.
- `src/dsclinic_gui/report_view_models.py`:
  - `_streaming_buffer: str` instance attribute — accumulates chunk text for the current turn; reset at the start of each `followup_question_submit()`.
  - `var_chunk: tk.StringVar` — set on every CHUNK event with the fully accumulated text so far. ChatSessionView traces this to call `update_text()` in place.
  - `_analysis_queue` and `_chat_queue` — two separate `queue.Queue[ProgressEvent]` instances replacing the single `_output_queue`. Analysis worker writes to `_analysis_queue`; chat worker writes to `_chat_queue`. Prevents CHUNK events from interleaving with RUNNING/PROGRESS analysis events.
  - `_poll_analysis_queue()` — dedicated slow poller (QUEUE_POLL_INTERVAL_MS) for the initial analysis worker.
  - `_poll_chat_queue()` — dedicated fast poller (CHAT_STREAM_POLL_INTERVAL_MS) for the streaming chat worker.
  - `_apply_analysis_event()` — handles RUNNING / PROGRESS / FINISHED (MedicalReport) / CANCELED / FAILED for the analysis path.
  - `_apply_chat_event()` — handles CHUNK / FINISHED (str) / FAILED for the chat streaming path.
  - `_run_task_followup_question()` — rewritten to iterate `active_provider.ask()` chunk-by-chunk, emitting one CHUNK event per fragment with the accumulated text in `message`, then a final FINISHED with the complete answer in `result`.
  - `followup_question_submit()` — resets `_streaming_buffer` and `var_chunk` before launch; schedules `_poll_chat_queue` (not `_poll_analysis_queue`).
  - `new_session()` — clears `var_chunk` alongside `var_response`.
- `src/dsclinic_gui/chat_session_view.py`:
  - `MarkdownLabel.update_text(new_text: str)` — enables widget, clears content, re-inserts markdown, disables, recalculates height. In-place streaming update without spawning a new widget.
  - `MarkdownLabel._insert_markdown()` — extracted from `__init__` as a named private method so `update_text()` can reuse it.
  - `MarkdownLabel._recalculate_height()` — extracted from `__init__` as a named private method.
  - `ChatSessionView._current_bot_bubble: Optional[MarkdownLabel]` — reference to the bot bubble currently receiving stream chunks. `None` between turns.
  - `ChatSessionView._bind_viewmodel()` — wires all three traces in one place: `var_chunk` to `_on_chunk()`; `var_response` to `_on_response_finalised()`; `var_is_analyzing` to `_on_analyzing_changed()`.
  - `ChatSessionView._on_chunk()` — creates the bot bubble on the first chunk of a turn via `_add_bot_bubble()`; calls `update_text()` on subsequent chunks. Auto-scrolls to bottom.
  - `ChatSessionView._on_response_finalised()` — traces `var_response` (FINISHED signal) to call `append_chat_response()` for model persistence only. Does not create a new bubble.
  - `ChatSessionView._on_analyzing_changed()` — clears `_current_bot_bubble` reference when `var_is_analyzing` transitions to `False`; calls `_update_input_state()`.
  - `ChatSessionView._add_bot_bubble(text)` — creates and returns a `MarkdownLabel` bubble aligned left; separated from the user-bubble path.
  - `ChatSessionView.add_user_bubble(text)` — public method for user-side plain `ttk.Label` bubbles.
  - `ChatSessionView._on_send()` — guard added: returns early on empty input. Calls `add_user_bubble()` directly instead of the old `add_message()` shim.
  - Module docstring added explaining the streaming architecture.

### Changed
- `src/dsclinic_gui/report_view_models.py` — `_reset_task_state()` now resets `_analysis_queue` (not the removed `_output_queue`).
- `src/dsclinic_gui/chat_session_view.py` — `var_response.trace_add` no longer drives bubble creation; moved to `_on_response_finalised()` for persistence only.
- `pyproject.toml` — version bumped to `2.12.1`.

---

## [2.11.5] - 2026-09-04

### Added
- `src/dsclinic_gui/report_view_models.py`:
  - `from models.brand import brand_config` import added.
  - `_TRIAL_DAILY_LIMIT: int = 3` module-level constant — maximum analyses per day on the trial tier.
  - `_start_analysis()`: trial-tier session limit gate added before any worker thread is launched. Calls `brand_config.is_feature_allowed("unlimited_sessions")`; when `False`, counts today's sessions from `_db.sessions.list_index()` filtered by ISO date prefix. If count ≥ `_TRIAL_DAILY_LIMIT`, emits `on_show_error_message` with upgrade prompt and returns without launching analysis. Standard and enterprise tiers skip the check entirely (zero overhead). `OSError` on index read caught and logged; count defaults to 0 so a DB failure never silently blocks analysis.
- `src/providers/factory.py` — `available_providers()`: enterprise stub block added at top of method. Lazy-imports `brand_config` inside try/except; calls `is_feature_allowed("custom_models")` and logs a `DEBUG` message when the enterprise tier is active. `except Exception: pass` ensures no provider discovery is ever blocked by a brand config import failure.

### Changed
- `pyproject.toml` — version bumped to `2.11.5`.

---

## [2.11.4] - 2026-09-04

### Added
- `src/dsclinic_gui/settings/settings_view.py` — `_build_clinic_profile_section()`: new "CLINIC PROFILE" card placed first in the settings scroll area.

### Changed
- `src/dsclinic_gui/settings/settings_view_model.py` — clinic profile vars, `brand_config.save()` on save.
- `pyproject.toml` — version bumped to `2.11.4`.

---

## [2.11.3] - 2026-09-04

### Changed
- `src/dsclinic_gui/dsclinic_gui_app.py` — window title from `brand_config.clinic_name`.
- `src/dsclinic_gui/report_view.py` — toolbar branding: clinic name + subtitle + 22×22 logo.
- `pyproject.toml` — version bumped to `2.11.3`.

---

## [2.11.2] - 2026-09-04

### Changed
- `src/pdf_maker.py` — fully branded via `brand_config`; trial watermark; `LOGO_PATH` removed.
- `pyproject.toml` — version bumped to `2.11.2`.

---

## [2.11.1] - 2026-09-04

### Added
- `src/models/brand.py` — `BrandConfig`, `brand_config` singleton, `brand.json`.
- `src/models/__init__.py` — `BrandConfig` and `brand_config` exported.

### Changed
- `pyproject.toml` — version bumped to `2.11.1`.

---

## [2.10.4] - 2026-09-03

### Changed
- `src/providers/factory.py` — `OllamaProvider` stub replaced with full lazy import.

---

## [2.10.3] - 2026-09-03

### Added
- `src/providers/ollama_provider.py` — `OllamaProvider._ensure_model_loaded()`: unloads previous model before loading new, pulls on first use only.

---

## [2.10.2] - 2026-09-03

### Added
- `src/providers/ollama_provider.py` — `OllamaProvider(LLMProvider)` full implementation.

---

## [2.10.1] - 2026-09-03

### Added
- Ollama config infra: `config.json`, `AppSettings`, `SettingsViewModel`, `settings_view.py` "LOCAL AI" card.

### Changed
- `pyproject.toml` — version bumped to `2.10.1`.

---

## [2.9.4] - 2026-09-02

### Changed
- `src/providers/factory.py` — Groq, Together, HuggingFace stubs replaced with lazy imports.

---

## [2.9.3] - 2026-09-02

### Added
- `src/providers/groq_provider.py`, `together_provider.py`, `huggingface_provider.py`.

---

## [2.9.2] - 2026-09-02

### Added
- `src/providers/openai_compatible_provider.py` — `OpenAICompatibleProvider(LLMProvider)` shared base.

---

## [2.9.1] - 2026-09-02

### Added
- `ProviderRequest.context: str` field (Split-Horizon text-only path, AD-12).
- Groq, Together, HuggingFace credential and config infra.

### Changed
- `pyproject.toml` — version bumped to `2.9.1`.

---

## [2.8.4] - 2026-09-02

### Changed
- `src/dsclinic.py` — full refactor to route through `ProviderFactory` / `LLMProvider` (AD-19).

---

## [2.8.3] - 2026-09-02

### Added
- `src/providers/factory.py` — `ProviderFactory` with `create()` and `available_providers()`.

### Changed
- `src/providers/__init__.py` — `ProviderFactory` exported.

---

## [2.8.2] - 2026-09-02

### Added
- `src/providers/gemini_provider.py` — `GeminiProvider(LLMProvider)`.
- `src/providers/claude_provider.py` — `ClaudeProvider(LLMProvider)`.

---

## [2.8.1] - 2026-09-02

### Added
- `src/providers/` package, `base.py` — `ProviderType`, `ProviderRequest`, `ProviderResponse`, `LLMProvider(ABC)`.

---

## [2.7.4] - 2026-09-01

### Added
- `src/dsclinic_gui/session_history_view.py` — two-tab Notebook sidebar (Sessions + Patients).
- `src/dsclinic_gui/report_view_models.py` — patient management methods.

---

## [2.7.3] - 2026-09-01

### Added
- `src/dsclinic_gui/session_history_view.py` — `SessionHistoryView(ttk.Frame)` initial version.
- Session index, `on_sessions_changed`, `load_session()`, `new_session()` in ViewModel.

### Changed
- `src/dsclinic_gui/main_container.py` — three-pane layout.

---

## [2.7.2] - 2026-09-01

### Added
- `AppDatabase` wired into `DSClinicViewModel`; `_persist_report()`, `_persist_session()`.

---

## [2.7.1] - 2026-09-01

### Added
- `src/models/patient.py` — `PatientRecord(BaseModel)`.
- `src/db/app_database.py` — `patients` collection.

---

## [2.5.4] - 2026-09-01

### Added
- `pyproject.toml` full migration: metadata, deps, extras, dev group, tool sections.
- `README.md` full rewrite.

### Removed
- `mypy.ini` — config moved into `pyproject.toml`.

---

## [2.5.3] - 2026-09-01

### Fixed
- `mypy --strict src/` — 0 errors across 26 checked files.

---

## [2.5.2] - 2026-08-31

### Fixed
- Defensive error handling audit across `src/db/`, keyring, worker threads.

---

## [2.5.1] - 2026-08-31

### Fixed
- MVVM boundary audit; `append_chat_response()` delegate; `execute_export()` error handling.

---

## [2.6.7] - 2026-08-30

### Security
- `settings.ini` permanently deleted. Both API keys regenerated and written to OS keyring.

---

## [2.6.0] - 2026-08-30 — Secure Credential Management & `settings.ini` Elimination ✅

### Security
- All API keys moved to OS keyring via `keyring_manager.py`. `settings.ini` deleted.

---

## [2.3.0] - 2026-08-29

### Added
- Unified `src/models/` package. `AppSettings` Pydantic model.

---

## [2.1.10] - 2026-08-28

### Added
- "SUPPORT" card section in Settings. Token-optimization filters.

### Fixed
- Nested-tuple serialization bug on multiple settings saves.
