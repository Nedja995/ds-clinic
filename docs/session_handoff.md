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

## Current Status: v2.9.0 ✅ Complete — Next: v2.10.0

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
| v2.9.1 | Credential & config infra for new providers | ✅ Done |
| v2.9.2 | `OpenAICompatibleProvider` base class | ✅ Done |
| v2.9.3 | `GroqProvider`, `TogetherProvider`, `HuggingFaceProvider` | ✅ Done |
| v2.9.4 | Register new providers in `ProviderFactory` | ✅ Done |
| v2.10.0 | Local Ollama provider | Planned |
| v2.11.0 | BrandConfig + white-label + subscription | Planned |
| v2.12.0 | Chat Session View rewrite | Planned |
| v2.13.0 | pytest coverage | Planned |
| v2.14.0 | PII improvements + debug panel | Planned |
| v2.15.0 | README case study + architecture diagrams | Planned |

---

## v2.9.0 Changes (completed 2026-09-02)

### Architecture decision (Option A — confirmed by developer)
`ProviderRequest.context: str` field added to `base.py`. Text-only providers (Groq, Together, HuggingFace, Ollama) cannot consume binary `documents` — callers must pre-extract text into `context`. This makes the Split-Horizon Layer 1/2 boundary explicit in the data model (AD-12).

### v2.9.1
- `src/models/keyring_manager.py` — added `"groq"`, `"together"`, `"huggingface"` to `_CREDENTIAL_KEYS`.
- `src/providers/base.py` — `ProviderRequest.context: str` field added with full docstring explaining Split-Horizon usage.
- `src/models/settings.py` — `groq_model_name`, `together_model_name`, `huggingface_model_name` fields; `groq_supported_models`, `together_supported_models`, `huggingface_supported_models` dicts; all wired in `load_unified()` and excluded from `save_unified()`.
- `config.json` — `groq_initial_model_config` + `groq_supported_models`, `together_initial_model_config` + `together_supported_models`, `huggingface_initial_model_config` + `huggingface_supported_models` added.
- `src/dsclinic_gui/settings/settings_view_model.py` — `var_groq_api_key`, `var_together_api_key`, `var_huggingface_api_key`; all wired in `update_from_config()` and `save_to_config()`.
- `src/dsclinic_gui/settings/settings_view.py` — three new `_credential_field()` calls; `_HEIGHT` bumped to 1020.
- `pyproject.toml` — version bumped to `2.9.1`.

### v2.9.2
- `src/providers/openai_compatible_provider.py` — `OpenAICompatibleProvider(LLMProvider)` shared base. Parameterised by `_BASE_URL` / `_CREDENTIAL_NAME`. `analyze()`: text-only, warns on `documents`, enforces JSON schema via `_JSON_SCHEMA_SUFFIX`, strips markdown fences, parses `MedicalReportModel`. `ask()`: streaming via `_stream_and_record()` generator that records history on exhaustion. Catches all OpenAI SDK errors → `RuntimeError`.

### v2.9.3
- `src/providers/groq_provider.py` — `GroqProvider`: `_BASE_URL="https://api.groq.com/openai/v1"`.
- `src/providers/together_provider.py` — `TogetherProvider`: `_BASE_URL="https://api.together.xyz/v1"`.
- `src/providers/huggingface_provider.py` — `HuggingFaceProvider`: `_BASE_URL="https://router.huggingface.co/v1"`. Key-only `is_available()` per AD-16.

### v2.9.4
- `src/providers/factory.py` — `NotImplementedError` stubs for GROQ, TOGETHER, HUGGINGFACE replaced with lazy imports of concrete classes. OLLAMA stub retained.

---

## Key Existing Code Context

- `src/providers/` — complete: `base.py`, `gemini_provider.py`, `claude_provider.py`, `openai_compatible_provider.py`, `groq_provider.py`, `together_provider.py`, `huggingface_provider.py`, `factory.py`, `__init__.py`.
- `src/providers/base.py` — `ProviderRequest` now has `context: str` field for text-only providers.
- `src/dsclinic.py` — routes all AI calls through `active_provider`; no direct SDK imports. Document loading produces `genai_types.Part` list — text-only providers receive empty `documents` and rely on `context`.
- `src/db/app_database.py` — `patients`, `sessions`, `reports`, `ai_profiles` fully implemented.
- `src/dsclinic_gui/report_view_models.py` — full patient + session management.
- PII anonymization — working, over-anonymizes clinical values; fix in v2.14.0.

---

## Previously Completed

- **v2.9.4** ✅ — `ProviderFactory` stubs replaced; all 5 implemented providers fully registered.
- **v2.9.3** ✅ — `GroqProvider`, `TogetherProvider`, `HuggingFaceProvider` concrete subclasses.
- **v2.9.2** ✅ — `OpenAICompatibleProvider` shared base; single `openai` SDK covers all three backends.
- **v2.9.1** ✅ — Credential infra, `AppSettings`, Settings UI, `config.json`, `ProviderRequest.context`.
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
