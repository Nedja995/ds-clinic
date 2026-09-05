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

## [2.12.3] - 2026-09-05

### Added
- `src/dsclinic.py` — `get_initial_analysis_report()`: `additional_prompt: str = ""` parameter added. When non-empty, the cleaned additional prompt is appended to `system_instructions` in the `ProviderRequest` before the provider call. Appending rather than replacing preserves the base JSON schema, language, and formatting rules from config. Log message emitted at INFO level with prompt length.
- `src/dsclinic_gui/report_view_models.py`:
  - `var_additional_prompt: tk.StringVar` — pre-populated from `app_settings.ai_initial_task_description` so a plain reanalyze without editing produces the same result as the initial analysis.
  - `var_reanalysis_summary: tk.StringVar` — set to `model.content.patient_name` (or fallback `"Reanalysis complete"`) when a reanalysis FINISHED event arrives. The View traces this to add a `[Reanalysis]` labeled bot bubble without a separate event channel.
  - `_is_reanalysis: bool` — instance flag set `True` by `reanalyze()`, reset to `False` in all `_apply_analysis_event` terminal branches (FINISHED / CANCELED / FAILED) so a subsequent normal analysis is never misidentified.
  - `reanalyze() -> None` — guards: blocked while `var_is_analyzing` is `True`; applies same trial-tier daily limit gate as `_start_analysis()`. Sets `_is_reanalysis = True`, launches `_run_task_initial_analyzis` with `additional_prompt=var_additional_prompt.get().strip()` on `_analysis_queue`; schedules `_poll_analysis_queue`.
  - `_run_task_initial_analyzis()` — `additional_prompt: str = ""` parameter added; passed through to `dsclinicapp.get_initial_analysis_report(additional_prompt=...)`.
  - `_apply_analysis_event()` — FINISHED branch: sets `var_reanalysis_summary` and clears `_is_reanalysis` when `_is_reanalysis` is `True`; all terminal branches (FINISHED-error, CANCELED, FAILED) reset `_is_reanalysis = False`.
  - `new_session()` — resets `var_additional_prompt` to `app_settings.ai_initial_task_description` and clears `var_reanalysis_summary`.
  - Module docstring updated to document reanalysis threading model.
- `src/dsclinic_gui/chat_session_view.py`:
  - `ChatSessionView._build_reanalyze_row()` — new method: `ttk.Frame` packed `side="bottom"` above the send row, containing `ent_additional_prompt` (`ttk.Entry` bound to `var_additional_prompt`) and `btn_reanalyze` (`"↺ Reanalyze"`, `Accent.TButton`).
  - `ChatSessionView._build_send_row()` — extracted from `_build_ui()` as a named private method for structural clarity.
  - `ChatSessionView.btn_reanalyze` — disabled while `var_is_analyzing` is `True`; enabled when idle.
  - `ChatSessionView.ent_additional_prompt` — disabled while `var_is_analyzing` is `True`; enabled when idle.
  - `ChatSessionView._on_reanalyze()` — adds a right-aligned `[Reanalyze] <prompt>` user bubble (so the conversation history shows what prompt was used), then calls `view_model.reanalyze()`.
  - `ChatSessionView._on_reanalysis_complete()` — traces `var_reanalysis_summary`; adds a left-aligned `[Reanalysis] <summary>` bot bubble when the value is non-empty.
  - `ChatSessionView._bind_viewmodel()` — `var_reanalysis_summary.trace_add` wired to `_on_reanalysis_complete()`.
  - `ChatSessionView._update_input_state()` — extended to disable `btn_reanalyze` and `ent_additional_prompt` alongside existing widgets.
  - `_build_ui()` — call order: `_build_header()` → `_build_reanalyze_row()` → `_build_send_row()` → `_build_history_canvas()`.
  - Module docstring updated with Reanalyze section.

### Changed
- `src/dsclinic_gui/report_view_models.py` — `_start_analysis()` sets `_is_reanalysis = False` before launching so a normal analysis is never misidentified as a reanalysis.
- `pyproject.toml` — version bumped to `2.12.3`.

---

## [2.12.2] - 2026-09-05

### Added
- `src/dsclinic_gui/report_view_models.py`:
  - `from providers import ProviderFactory, ProviderType` import added.
  - `var_active_provider: tk.StringVar` — initialised from `dsclinicapp.active_provider.provider_type().value` at startup.
  - `available_provider_names() -> list[str]` — wraps `ProviderFactory.available_providers()`.
  - `set_provider_by_name(name: str) -> None` — calls `dsclinicapp.set_active_provider()`; emits error and restores var on failure.
- `src/dsclinic_gui/chat_session_view.py`:
  - `_build_header()` with provider Combobox.
  - `cmb_provider`, `_refresh_provider_list()`, `_on_provider_selected()`.
  - `_update_input_state()` extended to cover `cmb_provider`.
  - `<Return>` binding on `ent_message`.

### Changed
- `src/dsclinic_gui/styles.py` — `ChatUser.TFrame/TLabel` solid `ACCENT` + `WHITE` fg.
- `pyproject.toml` — version bumped to `2.12.2`.

---

## [2.12.1] - 2026-09-04

### Added
- `src/models/diagnostics.py` — `TaskStatus.CHUNK`.
- `src/dsclinic_gui/constants.py` — `CHAT_STREAM_POLL_INTERVAL_MS = 100`.
- `src/dsclinic_gui/report_view_models.py` — `_streaming_buffer`, `var_chunk`, `_analysis_queue`, `_chat_queue`, dual pollers and handlers, `_run_task_followup_question` rewritten for chunk streaming.
- `src/dsclinic_gui/chat_session_view.py` — `MarkdownLabel.update_text()`, `_current_bot_bubble`, `_on_chunk()`, `_on_response_finalised()`, `_on_analyzing_changed()`, `_add_bot_bubble()`, `add_user_bubble()`.

### Changed
- `src/dsclinic_gui/report_view_models.py` — `_reset_task_state()` resets `_analysis_queue`.
- `pyproject.toml` — version bumped to `2.12.1`.

---

## [2.11.5] - 2026-09-04

### Added
- Trial session gate in `_start_analysis()`; enterprise stub in `ProviderFactory.available_providers()`.

### Changed
- `pyproject.toml` — version bumped to `2.11.5`.

---

## [2.11.4] - 2026-09-04

### Added
- Clinic Profile settings card.

### Changed
- `pyproject.toml` — version bumped to `2.11.4`.

---

## [2.11.3] - 2026-09-04

### Changed
- Window title + toolbar branding from `brand_config`.
- `pyproject.toml` — version bumped to `2.11.3`.

---

## [2.11.2] - 2026-09-04

### Changed
- `pdf_maker.py` fully branded; trial watermark; `LOGO_PATH` removed.
- `pyproject.toml` — version bumped to `2.11.2`.

---

## [2.11.1] - 2026-09-04

### Added
- `src/models/brand.py` — `BrandConfig`, `brand_config` singleton, `brand.json`.

### Changed
- `pyproject.toml` — version bumped to `2.11.1`.

---

## [2.10.4] - 2026-09-03

### Changed
- `ProviderFactory` — `OllamaProvider` stub replaced with lazy import.

---

## [2.10.3] - 2026-09-03

### Added
- `OllamaProvider._ensure_model_loaded()` — unload previous model before loading new; pull on first use only.

---

## [2.10.2] - 2026-09-03

### Added
- `OllamaProvider(LLMProvider)` full implementation.

---

## [2.10.1] - 2026-09-03

### Added
- Ollama config infra: `config.json`, `AppSettings`, `SettingsViewModel`, Settings UI "LOCAL AI" card.

### Changed
- `pyproject.toml` — version bumped to `2.10.1`.

---

## [2.9.4] - 2026-09-02

### Changed
- `ProviderFactory` — Groq, Together, HuggingFace stubs replaced.

---

## [2.9.3] - 2026-09-02

### Added
- `GroqProvider`, `TogetherProvider`, `HuggingFaceProvider`.

---

## [2.9.2] - 2026-09-02

### Added
- `OpenAICompatibleProvider(LLMProvider)` shared base.

---

## [2.9.1] - 2026-09-02

### Added
- `ProviderRequest.context: str`; Groq/Together/HuggingFace credential and config infra.

### Changed
- `pyproject.toml` — version bumped to `2.9.1`.

---

## [2.8.4] - 2026-09-02

### Changed
- `dsclinic.py` full refactor to `ProviderFactory` / `LLMProvider` (AD-19).

---

## [2.8.3] - 2026-09-02

### Added
- `ProviderFactory` with `create()` and `available_providers()`.

---

## [2.8.2] - 2026-09-02

### Added
- `GeminiProvider`, `ClaudeProvider`.

---

## [2.8.1] - 2026-09-02

### Added
- `src/providers/` package; `ProviderType`, `ProviderRequest`, `ProviderResponse`, `LLMProvider(ABC)`.

---

## [2.7.4] - 2026-09-01

### Added
- Two-tab Notebook sidebar (Sessions + Patients); patient management ViewModel methods.

---

## [2.7.3] - 2026-09-01

### Added
- `SessionHistoryView`; session index; `load_session()`; `new_session()`.

### Changed
- `main_container.py` — three-pane layout.

---

## [2.7.2] - 2026-09-01

### Added
- `AppDatabase` wired; `_persist_report()`, `_persist_session()`.

---

## [2.7.1] - 2026-09-01

### Added
- `PatientRecord`; `patients` collection in `AppDatabase`.

---

## [2.5.4] - 2026-09-01

### Added
- `pyproject.toml` full migration; `README.md` rewrite.

---

## [2.5.3] - 2026-09-01

### Fixed
- `mypy --strict src/` — 0 errors across 26 checked files.

---

## [2.5.2] - 2026-08-31

### Fixed
- Defensive error handling audit.

---

## [2.5.1] - 2026-08-31

### Fixed
- MVVM boundary audit; `append_chat_response()` delegate.

---

## [2.6.7] - 2026-08-30

### Security
- `settings.ini` permanently deleted. API keys regenerated and written to OS keyring.

---

## [2.6.0] - 2026-08-30 — Secure Credential Management & `settings.ini` Elimination ✅

### Security
- All API keys moved to OS keyring via `keyring_manager.py`.

---

## [2.3.0] - 2026-08-29

### Added
- Unified `src/models/` package; `AppSettings` Pydantic model.

---

## [2.1.10] - 2026-08-28

### Added
- "SUPPORT" card in Settings. Token-optimization filters.

### Fixed
- Nested-tuple serialization bug.
