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

## Current Status: v2.7.0 ✅ Complete — Next: v2.8.0

| Version | Scope | Status |
|---|---|---|
| v2.5.1 | MVVM boundary audit | ✅ Done |
| v2.5.2 | Defensive error handling audit | ✅ Done |
| v2.5.3 | `mypy --strict` type hints audit | ✅ Done |
| v2.5.4 | `pyproject.toml` + `uv` migration, README | ✅ Done |
| v2.7.1 | `PatientRecord` model + `AppDatabase` extension | ✅ Done |
| v2.7.2 | Wire `AppDatabase` into `DSClinicViewModel` | ✅ Done |
| v2.7.3 | Session history panel (View + ViewModel) | ✅ Done |
| v2.7.4 | Patient list panel (View + ViewModel) | ✅ Done |
| v2.8.0 | `src/providers/` LLMProvider abstraction | ▶ Next |
| v2.9.0 | Groq + Together + HuggingFace providers | Planned |
| v2.10.0 | Local Ollama provider | Planned |
| v2.11.0 | BrandConfig + white-label + subscription | Planned |
| v2.12.0 | Chat Session View rewrite | Planned |
| v2.13.0 | pytest coverage | Planned |
| v2.14.0 | PII improvements + debug panel | Planned |
| v2.15.0 | README case study + architecture diagrams | Planned |

---

## v2.7.4 Changes (completed 2026-09-01)

- `src/dsclinic_gui/session_history_view.py` — rewritten as `ttk.Notebook` with two tabs:
  - **Sessions tab:** filter indicator label, `+ New Session` button, scrollable `tk.Listbox`. Patient filter applied when `_filter_patient_id` is set; toggle-click on selected patient clears filter. Clicking a row → `view_model.load_session()`.
  - **Patients tab:** scrollable `tk.Listbox`. Clicking a patient sets the session filter, calls `view_model.set_active_patient()`, switches to Sessions tab. Inline "New Patient" form (full name + DOB + Save button) at the bottom; calls `view_model.save_new_patient()` and clears fields on success.
  - `_filter_patient_id` / `_filter_session_ids` — View-local filter state; no ViewModel involvement.
  - `_load_patient_session_ids()` — loads `PatientRecord.session_ids` from `view_model._db` for filter construction.
- `src/dsclinic_gui/report_view_models.py`:
  - `_active_patient_id: str` — patient currently linked to new sessions; cleared only by `set_active_patient("")`.
  - `var_patients_index: list[dict]` — populated from `_db.patients.list_index()` on init.
  - `on_patients_changed: EventEmitter` — fired on every `_refresh_patients_index()` call.
  - `_refresh_patients_index()` — reloads patients index and emits `on_patients_changed`.
  - `_link_session_to_patient()` — idempotently inserts `session_id` at head of `PatientRecord.session_ids` and re-saves.
  - `_persist_session()` — now calls `_link_session_to_patient()` when `_active_patient_id` is set.
  - `save_new_patient(full_name, date_of_birth)` — creates and persists `PatientRecord`, emits `on_patients_changed`.
  - `set_active_patient(patient_id)` — sets `_active_patient_id`.
  - `PatientRecord` imported from `models`.
- `src/dsclinic_gui/styles.py` — `SidebarFormLabel.TLabel` added.

---

## v2.8.0 Implementation Notes

Files to read before starting:
- `src/dsclinic.py` — `DSClinic` class: replace `MedicalAnalyzerClient` / `ClaudeAnalyzerClient` direct construction with `ProviderFactory.create()`.
- `src/api_gemini/client.py` — `MedicalAnalyzerClient`: understand `initial_analysis_report_from_chat_stream()` and `ask_followup_question()` signatures before wrapping in `GeminiProvider`.
- `src/api_claude/client.py` — `ClaudeAnalyzerClient`: same, for `ClaudeProvider`.
- `src/models/patient.py` — `MedicalReportModel` is the return type of `analyze()`.
- `docs/architecture.md` AD-19 — full `src/providers/` package structure and `is_available()` contract.

Key decisions for v2.8.0:
- `src/providers/base.py` — `ProviderType(StrEnum)`, `ProviderRequest(BaseModel)`, `ProviderResponse(BaseModel)`, `LLMProvider(ABC)`.
- `GeminiProvider` and `ClaudeProvider` delegate to existing SDK clients — do not rewrite client logic.
- `ProviderFactory.available_providers()` priority: GEMINI → CLAUDE (additional providers added in v2.9.0 / v2.10.0).
- `DSClinic.get_initial_analysis_report()` and `ask_followup_question()` route through `self.active_provider`.
- Default provider on startup: first available from `ProviderFactory.available_providers()`.

---

## Key Existing Code Context

- `src/db/app_database.py` — `patients`, `sessions`, `reports`, `ai_profiles` fully implemented.
- `src/dsclinic_gui/session_history_view.py` — two-tab `ttk.Notebook`: Sessions (filter + load/new) + Patients (filter + new patient form).
- `src/dsclinic_gui/report_view_models.py` — full patient + session management: `_active_patient_id`, `save_new_patient()`, `set_active_patient()`, `_link_session_to_patient()`, `load_session()`, `new_session()`.
- `src/models/patient.py` — `PatientRecord`, `MedicalReport`, `MedicalReportModel`.
- PII anonymization — working, over-anonymizes clinical values; fix in v2.14.0.

---

## Previously Completed

- **v2.7.4** ✅ — Patient list panel, inline new-patient form, patient→session linkage, session filter.
- **v2.7.3** ✅ — `SessionHistoryView` sidebar, `load_session()`, `new_session()`, `on_sessions_changed`.
- **v2.7.2** ✅ — `AppDatabase` wired; report + session auto-persist.
- **v2.7.1** ✅ — `PatientRecord` model, `AppDatabase.patients` collection.
- **v2.6.0** ✅ — Credentials to OS keyring, `settings.ini` deleted.
- **v2.5.0** ✅ — MVVM audit, error handling, `mypy --strict` clean, `uv` migration.
