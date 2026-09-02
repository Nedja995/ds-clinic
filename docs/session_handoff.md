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

## Current Status: v2.8.0 ✅ Complete — Next: v2.9.0

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
| v2.8.1 | `LLMProvider` ABC + data contracts | ✅ Done |
| v2.8.2 | `GeminiProvider` + `ClaudeProvider` | ✅ Done |
| v2.8.3 | `ProviderFactory` + `__init__.py` exports | ✅ Done |
| v2.8.4 | Refactor `DSClinic` to use `ProviderFactory` | ✅ Done |
| v2.9.0 | Groq + Together + HuggingFace providers | ▶ Next |
| v2.10.0 | Local Ollama provider | Planned |
| v2.11.0 | BrandConfig + white-label + subscription | Planned |
| v2.12.0 | Chat Session View rewrite | Planned |
| v2.13.0 | pytest coverage | Planned |
| v2.14.0 | PII improvements + debug panel | Planned |
| v2.15.0 | README case study + architecture diagrams | Planned |

---

## v2.8.4 Changes (completed 2026-09-02)

- `src/dsclinic.py` — full refactor to route through `ProviderFactory` / `LLMProvider`:
  - All direct SDK client imports removed. Only `api_gemini.utils` retained for document loading (Gemini Part format — a future adapter layer will generalise this when needed).
  - `DSClinic.__init__` — calls `ProviderFactory.available_providers()` and constructs the first available via `ProviderFactory.create()`. `active_provider: LLMProvider | None` attribute; `None` only when no key is configured.
  - `set_active_provider(provider_type: ProviderType) -> None` — new method; validates `is_available()` before assigning; raises `ValueError` if unavailable.
  - `get_initial_analysis_report()` — document loading loop unchanged; wraps loaded parts in `ProviderRequest`; delegates to `self.active_provider.analyze(request)`.
  - `ask_followup_question()` — delegates to `self.active_provider.ask(question)`; accumulates `Iterator[str]` into full string for ViewModel compatibility.

---

## v2.8.0 Summary (all sub-versions completed 2026-09-02)

- `src/providers/base.py` — `LLMProvider(ABC)`, `ProviderType(StrEnum)`, `ProviderRequest`, `ProviderResponse`.
- `src/providers/gemini_provider.py` — `GeminiProvider`: delegates to `MedicalAnalyzerClient`.
- `src/providers/claude_provider.py` — `ClaudeProvider`: delegates to `ClaudeAnalyzerClient`.
- `src/providers/factory.py` — `ProviderFactory.create()` + `available_providers()`.
- `src/providers/__init__.py` — exports all five public symbols.
- `src/dsclinic.py` — routes all AI calls through `active_provider`; no direct SDK imports.

---

## Key Existing Code Context

- `src/providers/` — complete: `base.py`, `gemini_provider.py`, `claude_provider.py`, `factory.py`, `__init__.py`.
- `src/dsclinic.py` — refactored: `active_provider: LLMProvider | None`, `set_active_provider()`, `get_initial_analysis_report()`, `ask_followup_question()` all route through the provider interface.
- `src/db/app_database.py` — `patients`, `sessions`, `reports`, `ai_profiles` fully implemented.
- `src/dsclinic_gui/report_view_models.py` — full patient + session management.
- PII anonymization — working, over-anonymizes clinical values; fix in v2.14.0.

---

## Previously Completed

- **v2.8.4** ✅ — `DSClinic` refactored to `ProviderFactory`; direct SDK client imports eliminated.
- **v2.8.3** ✅ — `ProviderFactory` + updated `__init__.py` exports.
- **v2.8.2** ✅ — `GeminiProvider` + `ClaudeProvider` concrete implementations.
- **v2.8.1** ✅ — `src/providers/` package + `base.py`: `LLMProvider` ABC, `ProviderType`, `ProviderRequest`, `ProviderResponse`.
- **v2.7.4** ✅ — Patient list panel, inline new-patient form, patient→session linkage, session filter.
- **v2.7.3** ✅ — `SessionHistoryView` sidebar, `load_session()`, `new_session()`, `on_sessions_changed`.
- **v2.7.2** ✅ — `AppDatabase` wired; report + session auto-persist.
- **v2.7.1** ✅ — `PatientRecord` model, `AppDatabase.patients` collection.
- **v2.6.0** ✅ — Credentials to OS keyring, `settings.ini` deleted.
- **v2.5.0** ✅ — MVVM audit, error handling, `mypy --strict` clean, `uv` migration.
