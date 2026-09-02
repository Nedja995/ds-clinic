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

## Current Status: v2.8.3 ✅ Complete — Next: v2.8.4

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
| v2.8.1 | `LLMProvider` ABC + data contracts (`src/providers/base.py`) | ✅ Done |
| v2.8.2 | `GeminiProvider` + `ClaudeProvider` concrete implementations | ✅ Done |
| v2.8.3 | `ProviderFactory` + `__init__.py` exports | ✅ Done |
| v2.8.4 | Refactor `DSClinic` to use `ProviderFactory` | ▶ Next |
| v2.9.0 | Groq + Together + HuggingFace providers | Planned |
| v2.10.0 | Local Ollama provider | Planned |
| v2.11.0 | BrandConfig + white-label + subscription | Planned |
| v2.12.0 | Chat Session View rewrite | Planned |
| v2.13.0 | pytest coverage | Planned |
| v2.14.0 | PII improvements + debug panel | Planned |
| v2.15.0 | README case study + architecture diagrams | Planned |

---

## v2.8.3 Changes (completed 2026-09-02)

- `src/providers/factory.py` — `ProviderFactory` with two `@staticmethod` methods:
  - `create(provider_type)` — switch on `ProviderType`, lazy-import and construct the concrete provider. `GROQ`, `TOGETHER`, `HUGGINGFACE`, `OLLAMA` raise `NotImplementedError` (stubs until v2.9.x/v2.10.x).
  - `available_providers()` — iterates `_PROVIDER_PRIORITY` list, constructs each provider, calls `is_available()`, catches `NotImplementedError` and any unexpected exception, returns ordered list of available `ProviderType` values.
- `src/providers/__init__.py` — `ProviderFactory` added to exports and `__all__`.

---

## v2.8.4 Implementation Notes

Files to read before starting:
- `src/dsclinic.py` — full current `DSClinic.__init__`, `get_initial_analysis_report()`, and `ask_followup_question()` — these three methods are the primary refactor targets.
- `src/providers/factory.py` — `ProviderFactory.create()` and `available_providers()` signatures.
- `src/providers/base.py` — `LLMProvider`, `ProviderRequest`, `ProviderType`.
- `src/api_gemini/client.py` — understand what the existing `gemini_client` currently does in `get_initial_analysis_report()` so the `ProviderRequest` is built correctly.

Key decisions for v2.8.4:
- `DSClinic.__init__` drops all direct client construction (`MedicalAnalyzerClient`, `ClaudeAnalyzerClient`). Replaces with `self.active_provider: LLMProvider = ProviderFactory.create(first_available)`. If `available_providers()` is empty, log a warning and leave `active_provider` as `None` — do not crash on startup.
- `set_active_provider(provider_type: ProviderType) -> None` — calls `ProviderFactory.create(provider_type)`, assigns to `self.active_provider`. Raises `ValueError` if the constructed provider is not available.
- `get_initial_analysis_report()` — builds a `ProviderRequest` from `app_settings` and the loaded document parts, calls `self.active_provider.analyze(request)`. The document loading loop (anonymization, scrubbed file map) stays unchanged — only the final API call changes.
- `ask_followup_question()` — calls `self.active_provider.ask(question)`, accumulates `Iterator[str]` chunks into a full string, returns it. Same return type as before.
- Type annotation: `active_provider: LLMProvider | None` — `None` only during the window between startup and first key being set. All call sites guard with `if self.active_provider is None: raise RuntimeError(...)`.

---

## v2.8.2 Changes (completed 2026-09-02)

- `src/providers/gemini_provider.py` — `GeminiProvider(LLMProvider)`: delegates to `MedicalAnalyzerClient`; startup guard; `ask()` wraps accumulated string in `iter([result])`.
- `src/providers/claude_provider.py` — `ClaudeProvider(LLMProvider)`: delegates to `ClaudeAnalyzerClient`; startup guard; `ask()` delegates to `ask_followup_stream()` directly.

---

## Key Existing Code Context

- `src/db/app_database.py` — `patients`, `sessions`, `reports`, `ai_profiles` fully implemented.
- `src/dsclinic_gui/session_history_view.py` — two-tab `ttk.Notebook`: Sessions (filter + load/new) + Patients (filter + new patient form).
- `src/dsclinic_gui/report_view_models.py` — full patient + session management.
- `src/providers/base.py` — `LLMProvider(ABC)`, `ProviderType`, `ProviderRequest`, `ProviderResponse` — complete.
- `src/providers/gemini_provider.py` — `GeminiProvider` — complete.
- `src/providers/claude_provider.py` — `ClaudeProvider` — complete.
- `src/providers/factory.py` — `ProviderFactory` — complete.
- PII anonymization — working, over-anonymizes clinical values; fix in v2.14.0.

---

## Previously Completed

- **v2.8.3** ✅ — `ProviderFactory` + updated `__init__.py` exports.
- **v2.8.2** ✅ — `GeminiProvider` + `ClaudeProvider` concrete implementations.
- **v2.8.1** ✅ — `src/providers/` package + `base.py`: `LLMProvider` ABC, `ProviderType`, `ProviderRequest`, `ProviderResponse`.
- **v2.7.4** ✅ — Patient list panel, inline new-patient form, patient→session linkage, session filter.
- **v2.7.3** ✅ — `SessionHistoryView` sidebar, `load_session()`, `new_session()`, `on_sessions_changed`.
- **v2.7.2** ✅ — `AppDatabase` wired; report + session auto-persist.
- **v2.7.1** ✅ — `PatientRecord` model, `AppDatabase.patients` collection.
- **v2.6.0** ✅ — Credentials to OS keyring, `settings.ini` deleted.
- **v2.5.0** ✅ — MVVM audit, error handling, `mypy --strict` clean, `uv` migration.
