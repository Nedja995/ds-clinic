# DSClinic — Master Session Handoff & AI Entry Point

Read this before starting any work. It captures everything needed to continue development without going through previous chat history.

---

> [!IMPORTANT]
> **CRITICAL AI SYSTEM DIRECTIVES (MANDATORY):**
> Before writing, proposing, or refactoring any code for this session, you MUST read, cross-reference, and strictly adhere to **Section 3.G (AI Coding Assistant System Directives)** inside `GEMINI.md`.

---

## Key Docs — Read On Demand, Not Upfront

- `TODO.md` — roadmap and task status
- `CHANGELOG.md` — version history
- `docs/architecture.md` — AD-01 through AD-21
- `GEMINI.md` — project-wide coding guidelines
- `.dev_profile/developer_profile.md` — standing workflow and commenting rules

---

## AI Coding Assistant Directives

1. **Defensive Error Handling:** No bare `except:`. All thread failures → `TaskStatus.FAILED`. All `src/db/` and keyring calls wrapped.
2. **GDPR:** All patient data through Presidio before external transmission. Credentials via `keyring_manager.py` only.
3. **MVVM:** Zero `tkinter`/`ttk` imports in ViewModels. Complete type annotations on all new code.
4. **Commenting:** Follow `.dev_profile/developer_profile.md` §6. Explain *why*, not *what*. Module/class docstrings on all new files.
5. **Toolchain:** `uv` + `pyproject.toml` (AD-21).
6. **Multi-Brand:** All identity/commercial config via `BrandConfig` (v2.11.0 ✅).

---

## Version & Commit Discipline

```bash
git add <exact files changed>
git commit -m "vX.Y.Z: <imperative description>"
git push
```

---

## Current Status: v2.12.4 ✅ Complete — v2.12.0 Milestone Complete

| Version | Scope | Status |
|---|---|---|
| v2.12.1 | Streaming bubble fix, dual queue pollers | ✅ Done |
| v2.12.2 | ChatUser style fix, provider selector Combobox | ✅ Done |
| v2.12.3 | Reanalyze command + additional prompt input | ✅ Done |
| v2.12.4 | `include_in_report` checkboxes per bubble | ✅ Done |
| v2.13.0 | pytest coverage | Next |
| v2.14.0 | PII improvements + debug panel | Planned |
| v2.15.0 | README case study + architecture diagrams | Planned |

---

## v2.12.4 Changes (completed 2026-09-05)

### Added
- `src/models/ai.py` — `ChatMessage.include_in_report: bool = Field(default=True)`. Default `True` preserves backward-compat with pre-v2.12.4 sessions.
- `src/dsclinic_gui/report_view_models.py`:
  - `_rebuild_chat_responses()` — rebuilds `_model.chat_responses` from bot turns (odd indices in `chat_history`) with `include_in_report=True`.
  - `set_message_inclusion(bot_index, value)` — maps 0-based bot-turn index to `chat_history` via `2*bot_index+1`; calls `_rebuild_chat_responses()`. Out-of-range silently ignored.
  - `append_chat_response()` — now calls `_rebuild_chat_responses()` instead of directly appending. `chat_history` is the single source of truth.
- `src/dsclinic_gui/chat_session_view.py`:
  - `_bot_bubble_count: int` — 0-based bot bubble counter; incremented in `_on_response_finalised()` and `_add_full_bot_bubble()`.
  - `_add_bot_bubble_label(text)` — creates `MarkdownLabel` only; stores `_bubble_frame` reference on the label.
  - `_attach_inclusion_checkbutton(label, bot_index)` — adds `"Include in report"` `ttk.Checkbutton` below the `MarkdownLabel`; `BooleanVar` defaults `True`; closure captures `bot_index` by value.
  - `_add_full_bot_bubble(text)` — full bot bubble with checkbutton in one call; used for non-streaming messages (`[Reanalysis]` etc.).
  - `_on_response_finalised()` — attaches checkbutton to `_current_bot_bubble`, calls `append_chat_response()`, increments `_bot_bubble_count`.
  - `_on_reanalysis_complete()` — now calls `_add_full_bot_bubble()` so reanalysis bubbles also have checkbuttons.

---

## v2.13.0 — Implementation Notes (next milestone)

### v2.13.1 — pytest Infrastructure
- `uv add pytest-asyncio --group dev` (pytest and pytest-mock already present in pyproject.toml).
- Create `tests/__init__.py`, `tests/conftest.py` with shared fixtures: `tmp_path`-based `AppDatabase`, mock `MedicalReport`, mock `ProviderRequest`.
- Verify `[tool.pytest.ini_options] testpaths = ["tests"]` in `pyproject.toml` (already present).

### v2.13.2 — Key test targets
- `tests/test_anonymization.py` — PII patterns redacted; clinical values NOT redacted (regression); Serbian Cyrillic + Latin.
- `tests/test_parsers.py` — `MedicalReportModel.model_validate_json()` good/bad fixtures.
- `tests/test_providers.py` — `ProviderFactory` routing; `is_available()` with mocked keyring; `OpenAICompatibleProvider.ask()` streaming; `OllamaProvider` daemon-down guard.
- `tests/test_db.py` — `JsonCollection` save/load/delete/rebuild round-trip.
- `tests/test_settings.py` — layered config; `BrandConfig` fallback.

---

## Key Existing Code Context

- `src/models/ai.py` — `ChatMessage.include_in_report: bool = True` added v2.12.4.
- `src/dsclinic_gui/report_view_models.py` — `_rebuild_chat_responses()`, `set_message_inclusion()`, `append_chat_response()` updated v2.12.4. `reanalyze()`, `var_additional_prompt`, `var_reanalysis_summary` from v2.12.3. `var_active_provider`, `available_provider_names()`, `set_provider_by_name()` from v2.12.2.
- `src/dsclinic_gui/chat_session_view.py` — `_bot_bubble_count`, `_add_bot_bubble_label()`, `_attach_inclusion_checkbutton()`, `_add_full_bot_bubble()` added v2.12.4. `_build_reanalyze_row()`, `_on_reanalyze()`, `_on_reanalysis_complete()` from v2.12.3.
- `src/dsclinic.py` — `get_initial_analysis_report(additional_prompt="")` from v2.12.3.
- `src/dsclinic_gui/styles.py` — `ChatUser`: `ACCENT` bg + `WHITE` fg.
- `src/models/diagnostics.py` — `TaskStatus`: RUNNING, PROGRESS, CHUNK, FINISHED, CANCELED, FAILED.
- `src/dsclinic_gui/constants.py` — `QUEUE_POLL_INTERVAL_MS = 1000`, `CHAT_STREAM_POLL_INTERVAL_MS = 100`.
- `src/providers/` — all six providers fully implemented.
- `src/models/brand.py` — `BrandConfig`, `brand_config`, `is_feature_allowed()`.

---

## Previously Completed

- **v2.12.4** ✅ — `ChatMessage.include_in_report`; `_rebuild_chat_responses()`; `set_message_inclusion()`; checkbutton per bot bubble; `_bot_bubble_count`. **v2.12.0 milestone complete.**
- **v2.12.3** ✅ — Reanalyze; additional prompt; `var_reanalysis_summary`; `_is_reanalysis`; `additional_prompt` param on `get_initial_analysis_report()`.
- **v2.12.2** ✅ — ChatUser style fix; provider Combobox; `var_active_provider`; `set_provider_by_name()`.
- **v2.12.1** ✅ — Streaming bubble fix; `MarkdownLabel.update_text()`; dual queue pollers; `TaskStatus.CHUNK`.
- **v2.11.1–v2.11.5** ✅ — BrandConfig, branding, settings, tier enforcement.
- **v2.10.1–v2.10.4** ✅ — OllamaProvider, VRAM guard, config.
- **v2.9.1–v2.9.4** ✅ — Groq, Together, HuggingFace providers.
- **v2.8.1–v2.8.4** ✅ — LLMProvider abstraction, ProviderFactory.
- **v2.7.1–v2.7.4** ✅ — PatientRecord, AppDatabase, session/patient sidebars.
- **v2.6.0** ✅ — Credentials to OS keyring.
- **v2.5.0** ✅ — MVVM audit, error handling, mypy, uv migration.
