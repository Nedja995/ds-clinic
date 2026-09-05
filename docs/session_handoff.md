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
5. **Toolchain:** `uv` + `pyproject.toml` (AD-21). `uv sync --group dev`, `uv run mypy src/`, `uv run pytest`, `uv run pyinstaller ...`.
6. **Multi-Brand:** All identity/commercial config via `BrandConfig` (v2.11.0 ✅). Never hardcode clinic names.

---

## Version & Commit Discipline

```bash
git add <exact files changed>
git commit -m "vX.Y.Z: <imperative description>"
git push
```

| File | When |
|---|---|
| `CHANGELOG.md` | Every sub-version |
| `TODO.md` | Every sub-version |
| `pyproject.toml` version | Every sub-version |
| `docs/session_handoff.md` | Every sub-version |
| `docs/architecture.md` | Any design decision |
| `.dev_profile/developer_profile.md` | Any standing rule change |

---

## Current Status: v2.12.2 ✅ Complete — Next: v2.12.3

| Version | Scope | Status |
|---|---|---|
| v2.5.1 – v2.5.4 | MVVM audit, error handling, mypy, uv | ✅ Done |
| v2.7.1 – v2.7.4 | PatientRecord, AppDatabase, session/patient panels | ✅ Done |
| v2.8.1 – v2.8.4 | LLMProvider abstraction, GeminiProvider, ClaudeProvider | ✅ Done |
| v2.9.1 – v2.9.4 | Groq, Together, HuggingFace providers | ✅ Done |
| v2.10.1 – v2.10.4 | OllamaProvider, VRAM guard, config | ✅ Done |
| v2.11.1 – v2.11.5 | BrandConfig, dynamic PDF/GUI branding, settings, tier enforcement | ✅ Done |
| v2.12.1 | Streaming bubble fix, `MarkdownLabel.update_text()`, dual queue pollers | ✅ Done |
| v2.12.2 | ChatUser style fix + provider selector Combobox in chat header | ✅ Done |
| v2.12.3 | Reanalyze command + additional prompt input | Next |
| v2.12.4 | `include_in_report` checkboxes per bubble | Planned |
| v2.13.0 | pytest coverage | Planned |
| v2.14.0 | PII improvements + debug panel | Planned |
| v2.15.0 | README case study + architecture diagrams | Planned |

---

## v2.12.2 Changes (completed 2026-09-05)

### Changed
- `src/dsclinic_gui/styles.py` — `ChatUser.TFrame` background `ACCENT_LT` → `ACCENT`; `ChatUser.TLabel` background `ACCENT_LT` → `ACCENT`, foreground `TEXT` → `WHITE`. User bubbles are now solid blue with white text.

### Added
- `src/dsclinic_gui/report_view_models.py`:
  - `from providers import ProviderFactory, ProviderType` import.
  - `var_active_provider: tk.StringVar` — initialised from `dsclinicapp.active_provider.provider_type().value`; empty string when no provider configured.
  - `available_provider_names() -> list[str]` — wraps `ProviderFactory.available_providers()`; never raises.
  - `set_provider_by_name(name: str) -> None` — calls `dsclinicapp.set_active_provider(ProviderType(name))`; on `ValueError` emits `on_show_error_message` and restores `var_active_provider`.
- `src/dsclinic_gui/chat_session_view.py`:
  - `_build_header()` — extracted from `_build_ui()`; builds title label (left) + provider selector block (right).
  - `cmb_provider: ttk.Combobox` — `state="readonly"`, bound to `var_active_provider`; `postcommand` refreshes values; `<<ComboboxSelected>>` calls `_on_provider_selected()`.
  - `_refresh_provider_list()` — calls `available_provider_names()` and updates combobox values; called once at build and on every open.
  - `_on_provider_selected(event)` — delegates to `view_model.set_provider_by_name()`.
  - `_update_input_state()` — extended to disable `cmb_provider` while analyzing.
  - `ent_message` — `<Return>` binding added.

---

## v2.12.3 — Implementation Notes (next sub-version)

### Reanalyze button
- Add `reanalyze(additional_prompt: str) -> None` to `DSClinicViewModel`.
  - Sets `var_is_analyzing = True`; launches `_run_task_initial_analyzis` on `_analysis_queue`.
  - Before launching: append `additional_prompt` to a local copy of `app_settings.ai_system_instructions` and pass it in via a `ProviderRequest` override, OR temporarily mutate `dsclinicapp`'s request context for the single call. Simpler: pass `additional_prompt` as an extra system instruction in the worker — do not mutate `app_settings`.
- Add `var_additional_prompt: tk.StringVar` to `DSClinicViewModel.__init__` — pre-populated with `app_settings.ai_initial_task_description`.
- In `ChatSessionView._build_header()`: add a "↺ Reanalyze" `ttk.Button` (`style="Toolbar.TButton"`) that calls `view_model.reanalyze(view_model.var_additional_prompt.get())`.
- Add a `ttk.Entry` bound to `var_additional_prompt` in the input pane (above the send row), replacing or augmenting the existing single entry.
- Reanalyze result: the FINISHED handler detects a `MedicalReport` result and emits `on_vm_data_changed` as usual. The chat view listens and adds a bot bubble prefixed with `[Reanalysis]`.
- The `_run_task_initial_analyzis` worker needs a way to receive the additional prompt — add an optional `additional_prompt: str = ""` parameter that is appended to `system_instructions` in the `ProviderRequest`.

---

## Key Existing Code Context

- `src/dsclinic_gui/styles.py` — `ChatUser` bubble: `ACCENT` bg + `WHITE` fg (fixed v2.12.2). `ChatBot` bubble: `WHITE` bg.
- `src/dsclinic_gui/report_view_models.py` — `var_active_provider`, `available_provider_names()`, `set_provider_by_name()` added v2.12.2.
- `src/dsclinic_gui/chat_session_view.py` — `cmb_provider`, `_build_header()`, `_refresh_provider_list()`, `_on_provider_selected()` added v2.12.2. `<Return>` binding on `ent_message`.
- `src/models/diagnostics.py` — `TaskStatus` (RUNNING, PROGRESS, CHUNK, FINISHED, CANCELED, FAILED).
- `src/dsclinic_gui/constants.py` — `QUEUE_POLL_INTERVAL_MS = 1000`, `CHAT_STREAM_POLL_INTERVAL_MS = 100`.
- `src/dsclinic_gui/report_view_models.py` — `_analysis_queue`, `_chat_queue`, `var_chunk`, `_streaming_buffer`, `_poll_analysis_queue()`, `_poll_chat_queue()`, `_apply_analysis_event()`, `_apply_chat_event()`.
- `src/dsclinic_gui/chat_session_view.py` — `MarkdownLabel.update_text()`, `_current_bot_bubble`, `_on_chunk()`, `_add_bot_bubble()`, `add_user_bubble()`.
- `src/providers/factory.py` — `ProviderFactory.available_providers()`, `create()`.
- `src/dsclinic.py` — `DSClinic.set_active_provider(provider_type)`, `active_provider`.
- `src/models/brand.py` — `BrandConfig`, `brand_config`, `is_feature_allowed()`.
- `src/pdf_maker.py` — fully branded; watermark on trial; logo optional.
- `src/providers/` — all six providers fully implemented.
- `src/db/app_database.py` — `patients`, `sessions`, `reports`, `ai_profiles`.

---

## Previously Completed

- **v2.12.2** ✅ — ChatUser style fix (solid ACCENT); provider Combobox in chat header; `var_active_provider`, `available_provider_names()`, `set_provider_by_name()` in ViewModel; `<Return>` binding on message entry.
- **v2.12.1** ✅ — Streaming bubble fix; `MarkdownLabel.update_text()`; dual queue pollers; `TaskStatus.CHUNK`; `CHAT_STREAM_POLL_INTERVAL_MS`.
- **v2.11.5** ✅ — Trial session gate; enterprise stub in ProviderFactory. v2.11.0 complete.
- **v2.11.4** ✅ — Clinic Profile settings card.
- **v2.11.3** ✅ — Window title + toolbar branding.
- **v2.11.2** ✅ — `pdf_maker.py` fully branded; watermark; logo optional.
- **v2.11.1** ✅ — `BrandConfig` model, `brand_config` singleton, `brand.json`.
- **v2.10.4** ✅ — All 6 providers registered in ProviderFactory.
- **v2.10.1–v2.10.3** ✅ — OllamaProvider, VRAM guard, config infra.
- **v2.9.1–v2.9.4** ✅ — Groq, Together, HuggingFace providers.
- **v2.8.1–v2.8.4** ✅ — LLMProvider abstraction, GeminiProvider, ClaudeProvider, ProviderFactory.
- **v2.7.1–v2.7.4** ✅ — PatientRecord, AppDatabase, session/patient sidebars.
- **v2.6.0** ✅ — Credentials to OS keyring.
- **v2.5.0** ✅ — MVVM audit, error handling, mypy, uv migration.
