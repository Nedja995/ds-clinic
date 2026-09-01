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

## Current Status: v2.7.3 ✅ Complete — Next: v2.7.4

| Version | Scope | Status |
|---|---|---|
| v2.5.1 | MVVM boundary audit | ✅ Done |
| v2.5.2 | Defensive error handling audit | ✅ Done |
| v2.5.3 | `mypy --strict` type hints audit | ✅ Done |
| v2.5.4 | `pyproject.toml` + `uv` migration, README | ✅ Done |
| v2.7.1 | `PatientRecord` model + `AppDatabase` extension | ✅ Done |
| v2.7.2 | Wire `AppDatabase` into `DSClinicViewModel` | ✅ Done |
| v2.7.3 | Session history panel (View + ViewModel) | ✅ Done |
| v2.7.4 | Patient list panel (View + ViewModel) | ▶ Next |
| v2.8.0 | `src/providers/` LLMProvider abstraction | Planned |
| v2.9.0 | Groq + Together + HuggingFace providers | Planned |
| v2.10.0 | Local Ollama provider | Planned |
| v2.11.0 | BrandConfig + white-label + subscription | Planned |
| v2.12.0 | Chat Session View rewrite | Planned |
| v2.13.0 | pytest coverage | Planned |
| v2.14.0 | PII improvements + debug panel | Planned |
| v2.15.0 | README case study + architecture diagrams | Planned |

---

## v2.7.3 Changes (completed 2026-09-01)

- `src/dsclinic_gui/session_history_view.py` — new `SessionHistoryView(ttk.Frame)`. Header strip, "New Session" button, scrollable `tk.Listbox`, empty-state label. Subscribes to `on_sessions_changed`; rebuilds list on every update. Row click → `view_model.load_session(session_id)`. Button → `view_model.new_session()`. Parallel `_session_ids` list keeps index→session_id mapping in sync with listbox.
- `src/dsclinic_gui/report_view_models.py` — added `var_sessions_index`, `on_sessions_changed` EventEmitter, `_refresh_sessions_index()`, `load_session()`, `new_session()`. `_persist_session()` now calls `_refresh_sessions_index()` after every save.
- `src/dsclinic_gui/styles.py` — added `SIDEBAR_BG`, `SIDEBAR_STRIP` constants; `SidebarPanel.TFrame`, `SidebarStrip.TFrame`, `SidebarTitle.TLabel`, `SidebarEmpty.TLabel` styles.
- `src/dsclinic_gui/main_container.py` — three-pane layout: `SessionHistoryView` (weight=2) | `MedicalReportView` (weight=6) | `ChatSessionView` (weight=2). Module + class docstrings added.
- `pyproject.toml` — `session_history_view.py` and `main_container.py` added to `[tool.mypy]` exclude list.

---

## v2.7.4 Implementation Notes

Files to read before starting:
- `src/dsclinic_gui/report_view_models.py` — add `var_patients_index`, `load_patient_sessions()`, `new_patient()`, `save_new_patient()` here.
- `src/dsclinic_gui/session_history_view.py` — add patient filter support: when a patient is selected, filter the listbox to show only sessions whose `session_id` is in the patient's `session_ids` list.
- `src/models/patient.py` — `PatientRecord` fields: `patient_id`, `full_name`, `date_of_birth`, `created_at`, `session_ids`.

Key decisions for v2.7.4:
- Patient list panel is a second tab or section within `SessionHistoryView` — use `ttk.Notebook` with two tabs: "Sessions" and "Patients". Keeps the sidebar footprint unchanged.
- "New Patient" form: inline entry fields at the bottom of the Patients tab (full_name, date_of_birth) + Save button. No separate dialog.
- Clicking a patient filters `var_sessions_index` in the Sessions tab to show only that patient's sessions. Clicking "All" or deselecting restores the full list.
- `PatientRecord.session_ids` is updated when a new session is saved and a patient is selected/active — v2.7.4 adds this linkage.

---

## Key Existing Code Context

- `src/db/app_database.py` — `patients`, `sessions`, `reports`, `ai_profiles` collections all implemented.
- `src/db/json_collection.py` — `list_index()` returns lightweight index. `save()`, `load()`, `delete()` all guarded.
- `src/models/patient.py` — `PatientRecord` (patient_id, full_name, date_of_birth, created_at, session_ids).
- `src/dsclinic_gui/session_history_view.py` — `SessionHistoryView` with `_rebuild_list()`, `_session_ids`, `on_sessions_changed` subscription.
- `src/dsclinic_gui/report_view_models.py` — `var_sessions_index`, `on_sessions_changed`, `_refresh_sessions_index()`, `load_session()`, `new_session()` all wired in v2.7.3.

---

## Previously Completed

- **v2.7.3** ✅ — `SessionHistoryView` sidebar, `load_session()`, `new_session()`, `on_sessions_changed` event, sidebar styles, three-pane `MainContainerView`.
- **v2.7.2** ✅ — `AppDatabase` wired into `DSClinicViewModel`; report + session auto-persist.
- **v2.7.1** ✅ — `PatientRecord` model, `AppDatabase.patients` collection.
- **v2.6.0** ✅ — Credentials to OS keyring, `settings.ini` deleted.
- **v2.5.0** ✅ — MVVM audit, error handling, `mypy --strict` clean, `uv` migration.
