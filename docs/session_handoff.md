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
6. **Multi-Brand:** All identity/commercial config via `BrandConfig` (v2.11.0). Never hardcode clinic names.

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

## Current Status: v2.7.2 ✅ Complete — Next: v2.7.3

| Version | Scope | Status |
|---|---|---|
| v2.5.1 | MVVM boundary audit | ✅ Done |
| v2.5.2 | Defensive error handling audit | ✅ Done |
| v2.5.3 | `mypy --strict` type hints audit | ✅ Done |
| v2.5.4 | `pyproject.toml` + `uv` migration, README | ✅ Done |
| v2.7.1 | `PatientRecord` model + `AppDatabase` extension | ✅ Done |
| v2.7.2 | Wire `AppDatabase` into `DSClinicViewModel` | ✅ Done |
| v2.7.3 | Session history panel (View + ViewModel) | ▶ Next |
| v2.7.4 | Patient list panel (View + ViewModel) | Planned |
| v2.8.0 | `src/providers/` LLMProvider abstraction | Planned |
| v2.9.0 | Groq + Together + HuggingFace providers | Planned |
| v2.10.0 | Local Ollama provider | Planned |
| v2.11.0 | BrandConfig + white-label + subscription | Planned |
| v2.12.0 | Chat Session View rewrite | Planned |
| v2.13.0 | pytest coverage | Planned |
| v2.14.0 | PII improvements + debug panel | Planned |
| v2.15.0 | README case study + architecture diagrams | Planned |

---

## v2.7.2 Changes (completed 2026-09-01)

- `src/dsclinic_gui/report_view_models.py`:
  - `self._db: AppDatabase` instantiated once in `__init__`.
  - `self._session: ChatSessionModel` tracks the active session (wraps current report + chat history).
  - `self._pending_question: str` stashes submitted question text so the `FINISHED` handler can build the `ChatMessage` pair without re-reading the already-cleared `StringVar`.
  - `_persist_report()`: saves `MedicalReport` to `_db.reports`; failures logged and swallowed.
  - `_persist_session()`: re-saves `ChatSessionModel` to `_db.sessions`; syncs `session.report` to current model before writing.
  - `_apply_progress_event` `FINISHED/MedicalReport` branch: calls `_persist_report` → creates fresh `ChatSessionModel` → calls `_persist_session`.
  - `_apply_progress_event` `FINISHED/str` branch: appends `ChatMessage` pair to `_session.chat_history`, clears `_pending_question`, calls `_persist_session`.
  - `followup_question_submit()`: stashes question into `_pending_question` before clearing `var_initial_question`.

---

## v2.7.3 Implementation Notes

Files to read before starting:
- `src/dsclinic_gui/report_view_models.py` — `self._db` and `self._session` now available; add `var_sessions_index` observable here.
- `src/dsclinic_gui/report_view.py` — main View file; this is where the session history panel widget gets added.
- `src/db/json_collection.py` — `list_index()` returns `list[dict[str, Any]]`; index keys for sessions are `session_id`, `report_report_date`, `report_content_patient_name` (dot-paths flattened with `_`).

Key decisions for v2.7.3:
- `var_sessions_index` is a plain Python list attribute on the ViewModel (not a `tk.StringVar`) — the View reads it on `on_vm_data_changed` to rebuild the listbox/treeview.
- Session history panel is a sidebar or collapsible panel in the existing main View layout — do not create a new top-level window.
- Loading a session replaces `self._model` and `self._session` on the ViewModel and emits `on_vm_data_changed`.
- "New Session" resets `_model`, `_session`, `_pending_question`, and all observable vars to defaults, then emits `on_vm_data_changed`.

---

## Key Existing Code Context

- `src/db/app_database.py` — `patients`, `sessions`, `reports`, `ai_profiles` collections all implemented.
- `src/db/json_collection.py` — `JsonCollection[T]`, fully typed and guarded. `list_index()` returns lightweight index without loading full records.
- `src/models/patient.py` — `PatientRecord` added in v2.7.1. `MedicalReport` existing.
- `src/models/ai.py` — `ChatSessionModel` (session_id, model_settings, report, chat_history), `ChatMessage`.
- `src/dsclinic_gui/report_view_models.py` — `self._db`, `self._session`, `_persist_report()`, `_persist_session()` all wired in v2.7.2.
- PII anonymization — working, over-anonymizes clinical values; fix in v2.14.0.

---

## Previously Completed

- **v2.7.2** ✅ — `AppDatabase` wired into `DSClinicViewModel`; report + session auto-persist after analysis and Q&A.
- **v2.7.1** ✅ — `PatientRecord` model, `AppDatabase.patients` collection, export from `models/__init__`.
- **v2.6.0** ✅ — Credentials to OS keyring, `settings.ini` deleted.
- **v2.5.0** ✅ — MVVM audit, error handling, `mypy --strict` clean, `uv` migration.
