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

## Current Status: v2.8.2 ✅ Complete — Next: v2.8.3

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
| v2.8.3 | `ProviderFactory` + `__init__.py` exports | ▶ Next |
| v2.8.4 | Refactor `DSClinic` to use `ProviderFactory` | Planned |
| v2.9.0 | Groq + Together + HuggingFace providers | Planned |
| v2.10.0 | Local Ollama provider | Planned |
| v2.11.0 | BrandConfig + white-label + subscription | Planned |
| v2.12.0 | Chat Session View rewrite | Planned |
| v2.13.0 | pytest coverage | Planned |
| v2.14.0 | PII improvements + debug panel | Planned |
| v2.15.0 | README case study + architecture diagrams | Planned |

---

## v2.8.2 Changes (completed 2026-09-02)

- `src/providers/gemini_provider.py` — `GeminiProvider(LLMProvider)`:
  - Constructs `MedicalAnalyzerClient` from keyring key + `app_settings` in `__init__`. Startup guard: `_client = None` if key absent, no exception raised.
  - `analyze()` delegates to `_client.initial_analysis_report_from_chat_stream()`, raises `RuntimeError` on `None` result.
  - `ask()` wraps `_client.ask_followup_question()` (returns `str`) in `iter([result])` to satisfy `Iterator[str]` contract without modifying the existing client.
  - `is_available()` → `self._client is not None and self._client.client is not None`.
- `src/providers/claude_provider.py` — `ClaudeProvider(LLMProvider)`:
  - Same startup-guard pattern. Constructs `ClaudeAnalyzerClient` from keyring key + `app_settings`.
  - `analyze()` delegates to `_client.initial_analysis_report_from_chat_stream()`, raises `RuntimeError` on `None`.
  - `ask()` delegates directly to `_client.ask_followup_stream()` — already yields `Iterator[str]`.
  - `is_available()` → `self._client is not None and self._client.client is not None`.

---

## v2.8.3 Implementation Notes

Files to read before starting:
- `src/providers/base.py` — `LLMProvider`, `ProviderType`, `ProviderRequest` — the interface `ProviderFactory` constructs against.
- `src/providers/gemini_provider.py` — `GeminiProvider.__init__` signature (no args) — factory constructs by calling `GeminiProvider()`.
- `src/providers/claude_provider.py` — `ClaudeProvider.__init__` signature (no args) — same pattern.

Key decisions for v2.8.3:
- `ProviderFactory` is a plain class with two `@staticmethod` methods — no instance needed.
- `create(provider_type: ProviderType) -> LLMProvider` — switch on `ProviderType`, construct and return the appropriate concrete class. For `GROQ`/`TOGETHER`/`HUGGINGFACE`/`OLLAMA`: raise `NotImplementedError` with a message pointing to v2.9.0/v2.10.0 — these are stubs in v2.8.3.
- `available_providers() -> list[ProviderType]` — iterate over the priority list `[GEMINI, CLAUDE, GROQ, TOGETHER, HUGGINGFACE, OLLAMA]`, construct each via `create()`, call `is_available()`, collect those that return `True`. For providers that raise `NotImplementedError` (v2.9.0+), catch and skip.
- Update `src/providers/__init__.py` to also export `ProviderFactory`.

---

## v2.8.1 Changes (completed 2026-09-02)

- `src/providers/` — new package directory.
- `src/providers/__init__.py` — exports `LLMProvider`, `ProviderType`, `ProviderRequest`, `ProviderResponse`.
- `src/providers/base.py` — `ProviderType(StrEnum)`, `ProviderRequest(BaseModel)`, `ProviderResponse(BaseModel)`, `LLMProvider(ABC)` with abstract methods `analyze()`, `ask()`, `provider_type()`, `is_available()`.
  - `ProviderRequest.documents: list[Any]` — intentionally untyped at the base: Gemini providers receive `list[genai_types.Part]`; Claude providers receive `list[dict[str, Any]]`. Concrete classes cast internally.
  - `LLMProvider` startup-guard contract documented: subclasses must NOT raise in `__init__` when a key is absent — set `_available = False` and return early.

---

## Key Existing Code Context

- `src/db/app_database.py` — `patients`, `sessions`, `reports`, `ai_profiles` fully implemented.
- `src/dsclinic_gui/session_history_view.py` — two-tab `ttk.Notebook`: Sessions (filter + load/new) + Patients (filter + new patient form).
- `src/dsclinic_gui/report_view_models.py` — full patient + session management: `_active_patient_id`, `save_new_patient()`, `set_active_patient()`, `_link_session_to_patient()`, `load_session()`, `new_session()`.
- `src/models/patient.py` — `PatientRecord`, `MedicalReport`, `MedicalReportModel`.
- `src/providers/base.py` — `LLMProvider(ABC)`, `ProviderType`, `ProviderRequest`, `ProviderResponse` — complete.
- `src/providers/gemini_provider.py` — `GeminiProvider` — complete.
- `src/providers/claude_provider.py` — `ClaudeProvider` — complete.
- PII anonymization — working, over-anonymizes clinical values; fix in v2.14.0.

---

## Previously Completed

- **v2.8.2** ✅ — `GeminiProvider` + `ClaudeProvider` concrete implementations.
- **v2.8.1** ✅ — `src/providers/` package + `base.py`: `LLMProvider` ABC, `ProviderType`, `ProviderRequest`, `ProviderResponse`.
- **v2.7.4** ✅ — Patient list panel, inline new-patient form, patient→session linkage, session filter.
- **v2.7.3** ✅ — `SessionHistoryView` sidebar, `load_session()`, `new_session()`, `on_sessions_changed`.
- **v2.7.2** ✅ — `AppDatabase` wired; report + session auto-persist.
- **v2.7.1** ✅ — `PatientRecord` model, `AppDatabase.patients` collection.
- **v2.6.0** ✅ — Credentials to OS keyring, `settings.ini` deleted.
- **v2.5.0** ✅ — MVVM audit, error handling, `mypy --strict` clean, `uv` migration.
