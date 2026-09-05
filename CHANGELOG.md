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

## [2.12.4] - 2026-09-05

### Added
- `src/models/ai.py` — `ChatMessage.include_in_report: bool = Field(default=True)`. Controls whether the bot response is included in the PDF export. Default `True` preserves backward-compatibility with sessions persisted before this version. Module and class docstrings added explaining the flag's scope (bot turns only; user messages are never exported).
- `src/dsclinic_gui/report_view_models.py`:
  - `_rebuild_chat_responses() -> None` — rebuilds `_model.chat_responses` from `_session.chat_history` by filtering to bot turns (odd indices) with `include_in_report=True`. Called after any mutation to `chat_history` or `include_in_report` flags. Logs count of bot messages and included count at DEBUG level.
  - `set_message_inclusion(bot_index: int, value: bool) -> None` — public delegate called by the View's Checkbutton trace. Maps `bot_index` (0-based bot-turn counter) to `chat_history` index via `2 * bot_index + 1`. Out-of-range indices are silently ignored. Calls `_rebuild_chat_responses()` after updating the flag.
  - `append_chat_response()` — behaviour changed: instead of directly appending to `_model.chat_responses`, now calls `_rebuild_chat_responses()`. The text argument is ignored; `chat_history` is the single source of truth. This ensures any previously toggled `include_in_report` flags are respected on every rebuild.
  - Module docstring updated with "Chat response → PDF filtering (v2.12.4)" section.
- `src/dsclinic_gui/chat_session_view.py`:
  - `ChatSessionView._bot_bubble_count: int` — 0-based counter of bot bubbles created in the current session view. Incremented in `_on_response_finalised()` and `_add_full_bot_bubble()` after the checkbutton is attached.
  - `ChatSessionView._add_bot_bubble_label(text) -> MarkdownLabel` — creates the bot bubble MarkdownLabel only (no checkbutton). Stores `_bubble_frame` reference on the label so `_attach_inclusion_checkbutton()` can add the checkbutton to the same parent. Replaces the previous `_add_bot_bubble()`.
  - `ChatSessionView._attach_inclusion_checkbutton(label, bot_index) -> None` — adds a `"Include in report"` `ttk.Checkbutton` below the MarkdownLabel in `label._bubble_frame`. `BooleanVar` starts `True`. The `_on_toggle` closure captures `bot_index` by value and calls `view_model.set_message_inclusion(bot_index, var.get())`.
  - `ChatSessionView._add_full_bot_bubble(text) -> None` — convenience method for non-streaming bot messages (e.g. `[Reanalysis]` bubbles): calls `_add_bot_bubble_label()` → `_attach_inclusion_checkbutton()` → `append_chat_response()` → increments counter.
  - `ChatSessionView._on_response_finalised()` — extended: after `var_response` fires, attaches the checkbutton to `_current_bot_bubble` (when not None), calls `append_chat_response()`, and increments `_bot_bubble_count`.
  - `ChatSessionView._on_reanalysis_complete()` — now calls `_add_full_bot_bubble()` instead of `_add_bot_bubble()` so reanalysis result bubbles also get checkbuttons.
  - `ChatSessionView.add_message()` legacy shim — updated to call `_add_full_bot_bubble()` for bot messages.
  - Module docstring updated with "Report inclusion checkboxes (v2.12.4)" section.

### Changed
- `pyproject.toml` — version bumped to `2.12.4`.

---

## [2.12.3] - 2026-09-05

### Added
- `src/dsclinic.py` — `get_initial_analysis_report(additional_prompt: str = "")`.
- `src/dsclinic_gui/report_view_models.py` — `var_additional_prompt`, `var_reanalysis_summary`, `_is_reanalysis`, `reanalyze()`, `additional_prompt` param on worker.
- `src/dsclinic_gui/chat_session_view.py` — `_build_reanalyze_row()`, `_on_reanalyze()`, `_on_reanalysis_complete()`.

### Changed
- `pyproject.toml` — version bumped to `2.12.3`.

---

## [2.12.2] - 2026-09-05

### Added
- `var_active_provider`, `available_provider_names()`, `set_provider_by_name()` in ViewModel.
- Provider Combobox in chat header; `<Return>` binding on message entry.

### Changed
- `ChatUser.TFrame/TLabel` — solid `ACCENT` + `WHITE` fg.
- `pyproject.toml` — version bumped to `2.12.2`.

---

## [2.12.1] - 2026-09-04

### Added
- `TaskStatus.CHUNK`; `CHAT_STREAM_POLL_INTERVAL_MS`; dual queue pollers; `MarkdownLabel.update_text()`; `_current_bot_bubble` streaming.

### Changed
- `pyproject.toml` — version bumped to `2.12.1`.

---

## [2.11.5] - 2026-09-04

### Added
- Trial session gate; enterprise stub in ProviderFactory.

### Changed
- `pyproject.toml` — version bumped to `2.11.5`.

---

## [2.11.4] - 2026-09-04 — Clinic Profile settings card. `pyproject.toml` bumped.

## [2.11.3] - 2026-09-04 — Window title + toolbar branding. `pyproject.toml` bumped.

## [2.11.2] - 2026-09-04 — `pdf_maker.py` fully branded; trial watermark. `pyproject.toml` bumped.

## [2.11.1] - 2026-09-04 — `BrandConfig`, `brand_config` singleton, `brand.json`. `pyproject.toml` bumped.

## [2.10.4] - 2026-09-03 — `OllamaProvider` stub replaced with lazy import.

## [2.10.3] - 2026-09-03 — `_ensure_model_loaded()` VRAM guard added.

## [2.10.2] - 2026-09-03 — `OllamaProvider(LLMProvider)` fully implemented.

## [2.10.1] - 2026-09-03 — Ollama config infra. `pyproject.toml` bumped.

## [2.9.4] - 2026-09-02 — Groq/Together/HuggingFace stubs replaced.

## [2.9.3] - 2026-09-02 — `GroqProvider`, `TogetherProvider`, `HuggingFaceProvider` added.

## [2.9.2] - 2026-09-02 — `OpenAICompatibleProvider` base class added.

## [2.9.1] - 2026-09-02 — `ProviderRequest.context`; credential infra. `pyproject.toml` bumped.

## [2.8.4] - 2026-09-02 — `dsclinic.py` refactored to route through `ProviderFactory`.

## [2.8.3] - 2026-09-02 — `ProviderFactory` with `create()` and `available_providers()`.

## [2.8.2] - 2026-09-02 — `GeminiProvider`, `ClaudeProvider` added.

## [2.8.1] - 2026-09-02 — `src/providers/` package; `ProviderType`, `ProviderRequest`, `LLMProvider(ABC)`.

## [2.7.4] - 2026-09-01 — Two-tab Notebook sidebar; patient management methods.

## [2.7.3] - 2026-09-01 — `SessionHistoryView`; `load_session()`; `new_session()`; three-pane layout.

## [2.7.2] - 2026-09-01 — `AppDatabase` wired; `_persist_report()`; `_persist_session()`.

## [2.7.1] - 2026-09-01 — `PatientRecord`; `patients` collection in `AppDatabase`.

## [2.5.4] - 2026-09-01 — `pyproject.toml` full migration; `README.md` rewrite.

## [2.5.3] - 2026-09-01 — `mypy --strict` 0 errors across 26 files.

## [2.5.2] - 2026-08-31 — Defensive error handling audit.

## [2.5.1] - 2026-08-31 — MVVM boundary audit; `append_chat_response()` delegate.

## [2.6.7] - 2026-08-30 — `settings.ini` deleted; keys rotated.

## [2.6.0] - 2026-08-30 — Credentials to OS keyring; `keyring_manager.py`.

## [2.3.0] - 2026-08-29 — `src/models/` package; `AppSettings` Pydantic model.

## [2.1.10] - 2026-08-28 — Settings "SUPPORT" card; nested-tuple serialization fix.
