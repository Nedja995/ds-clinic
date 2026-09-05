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

1. **Defensive Error Handling:** No bare `except:`. All thread failures → `TaskStatus.FAILED` queue. All `src/db/` and keyring calls wrapped.
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

## Current Status: v2.12.3 ✅ Complete — Next: v2.12.4

| Version | Scope | Status |
|---|---|---|
| v2.11.1 – v2.11.5 | BrandConfig, branding, settings, tier enforcement | ✅ Done |
| v2.12.1 | Streaming bubble fix, dual queue pollers | ✅ Done |
| v2.12.2 | ChatUser style fix, provider selector Combobox | ✅ Done |
| v2.12.3 | Reanalyze command + additional prompt input | ✅ Done |
| v2.12.4 | `include_in_report` checkboxes per bubble | Next |
| v2.13.0 | pytest coverage | Planned |
| v2.14.0 | PII improvements + debug panel | Planned |
| v2.15.0 | README case study + architecture diagrams | Planned |

---

## v2.12.3 Changes (completed 2026-09-05)

### Added
- `src/dsclinic.py` — `get_initial_analysis_report(additional_prompt: str = "")`: appends cleaned additional prompt to `system_instructions` when non-empty, preserving base config instructions.
- `src/dsclinic_gui/report_view_models.py`:
  - `var_additional_prompt: tk.StringVar` — pre-populated from `app_settings.ai_initial_task_description`.
  - `var_reanalysis_summary: tk.StringVar` — set on reanalysis completion; traced by View to add `[Reanalysis]` bubble.
  - `_is_reanalysis: bool` — flag set by `reanalyze()`, cleared in all terminal analysis event branches.
  - `reanalyze() -> None` — same trial-tier gate as `_start_analysis()`; sets `_is_reanalysis = True`; passes `additional_prompt` to worker.
  - `_run_task_initial_analyzis(additional_prompt: str = "")` — passes through to `dsclinicapp.get_initial_analysis_report()`.
  - `_apply_analysis_event()` — FINISHED branch sets `var_reanalysis_summary` and clears `_is_reanalysis` on reanalysis completion.
  - `new_session()` — resets `var_additional_prompt` and `var_reanalysis_summary`.
- `src/dsclinic_gui/chat_session_view.py`:
  - `_build_reanalyze_row()` — `ent_additional_prompt` + `btn_reanalyze` row above send row.
  - `_build_send_row()` — extracted from `_build_ui()`.
  - `_on_reanalyze()` — adds `[Reanalyze] <prompt>` user bubble, calls `view_model.reanalyze()`.
  - `_on_reanalysis_complete()` — traces `var_reanalysis_summary`; adds `[Reanalysis] <summary>` bot bubble.
  - `_update_input_state()` — extended to disable `btn_reanalyze` + `ent_additional_prompt`.

---

## v2.12.4 — Implementation Notes (next sub-version)

### `include_in_report` per chat message
- Add `include_in_report: bool = True` to `ChatMessage` in `src/models/ai.py`.
- Each bot bubble (`_add_bot_bubble()`) needs a `ttk.Checkbutton` below the `MarkdownLabel`. Default checked.
- The checkbutton's `BooleanVar` must update the corresponding `ChatMessage.include_in_report` in `_session.chat_history`. The index mapping: track bubble index as a counter in `_add_bot_bubble()` and pass it to a ViewModel delegate `set_message_inclusion(index, value)`.
- `pdf_maker.py` — filter `chat_responses` list by `include_in_report` before rendering the chat section.
- `write_report_pdf()` / `generate_report_pdf_at_filepath()` — the report object's `chat_responses` is a flat `list[str]` (see `MedicalReport.chat_responses`). Two options: (a) filter by index from `_session.chat_history[i].include_in_report`, or (b) add `include_in_report` to `MedicalReport.chat_responses` entries by replacing `list[str]` with `list[ChatMessage]`. Option (b) is cleaner and avoids index sync issues.

---

## Key Existing Code Context

- `src/dsclinic.py` — `get_initial_analysis_report(additional_prompt="")` added v2.12.3.
- `src/dsclinic_gui/report_view_models.py` — `var_additional_prompt`, `var_reanalysis_summary`, `_is_reanalysis`, `reanalyze()` added v2.12.3. `var_active_provider`, `available_provider_names()`, `set_provider_by_name()` from v2.12.2.
- `src/dsclinic_gui/chat_session_view.py` — `_build_reanalyze_row()`, `_on_reanalyze()`, `_on_reanalysis_complete()` added v2.12.3. Provider Combobox from v2.12.2. Streaming bubble from v2.12.1.
- `src/dsclinic_gui/styles.py` — `ChatUser`: `ACCENT` bg + `WHITE` fg. `ChatBot`: `WHITE` bg.
- `src/models/diagnostics.py` — `TaskStatus`: RUNNING, PROGRESS, CHUNK, FINISHED, CANCELED, FAILED.
- `src/dsclinic_gui/constants.py` — `QUEUE_POLL_INTERVAL_MS = 1000`, `CHAT_STREAM_POLL_INTERVAL_MS = 100`.
- `src/providers/factory.py` — `ProviderFactory.available_providers()`, `create()`.
- `src/dsclinic.py` — `DSClinic.set_active_provider()`, `active_provider`.
- `src/models/brand.py` — `BrandConfig`, `brand_config`, `is_feature_allowed()`.
- `src/providers/` — all six providers fully implemented.
- `src/db/app_database.py` — `patients`, `sessions`, `reports`.

---

## Previously Completed

- **v2.12.3** ✅ — Reanalyze button; additional prompt entry; `var_reanalysis_summary`; `_is_reanalysis`; `additional_prompt` param on `get_initial_analysis_report()`.
- **v2.12.2** ✅ — ChatUser style fix; provider Combobox; `var_active_provider`; `set_provider_by_name()`.
- **v2.12.1** ✅ — Streaming bubble fix; `MarkdownLabel.update_text()`; dual queue pollers; `TaskStatus.CHUNK`.
- **v2.11.1–v2.11.5** ✅ — BrandConfig, branding, settings, tier enforcement.
- **v2.10.1–v2.10.4** ✅ — OllamaProvider, VRAM guard, config.
- **v2.9.1–v2.9.4** ✅ — Groq, Together, HuggingFace providers.
- **v2.8.1–v2.8.4** ✅ — LLMProvider abstraction, ProviderFactory.
- **v2.7.1–v2.7.4** ✅ — PatientRecord, AppDatabase, session/patient sidebars.
- **v2.6.0** ✅ — Credentials to OS keyring.
- **v2.5.0** ✅ — MVVM audit, error handling, mypy, uv migration.
