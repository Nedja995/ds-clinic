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

## Current Status: v2.10.0 ✅ Complete — Next: v2.11.0

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
| v2.10.1 | Ollama infra & config | ✅ Done |
| v2.10.2 | `OllamaProvider` core implementation | ✅ Done |
| v2.10.3 | Load-on-demand & VRAM sequential guard | ✅ Done |
| v2.10.4 | Register Ollama in `ProviderFactory` | ✅ Done |
| v2.11.0 | BrandConfig + white-label + subscription | Planned |
| v2.12.0 | Chat Session View rewrite | Planned |
| v2.13.0 | pytest coverage | Planned |
| v2.14.0 | PII improvements + debug panel | Planned |
| v2.15.0 | README case study + architecture diagrams | Planned |

---

## v2.10.0 Changes (completed 2026-09-03)

### Architecture
All six `LLMProvider` backends are now fully implemented. `ProviderFactory` has no stubs remaining.

### v2.10.1
- `config.json` — `ollama_initial_model_config` (`llama3.2-vision:q4_0`, `base_url`) and `ollama_supported_models` (5 quantized model tags) added.
- `src/models/settings.py` — `ollama_model_name: str`, `ollama_base_url: str` writable fields; `ollama_supported_models: Dict[str, str]` static field. All wired in `load_unified()`. `save_unified()` excludes `ollama_supported_models` (static) but persists `ollama_model_name` and `ollama_base_url` (user prefs, not secrets).
- `src/dsclinic_gui/settings/settings_view_model.py` — `var_ollama_base_url`, `var_ollama_model_name` `tk.StringVar`; `ollama_supported_models` list. Wired in `update_from_config()` and `save_to_config()`.
- `src/dsclinic_gui/settings/settings_view.py` — new `_build_local_ai_section()` renders "LOCAL AI (OLLAMA)" card: plain base URL entry + hint; model combobox from `ollama_supported_models`. `_HEIGHT` bumped to 1160.
- `pyproject.toml` — version bumped to `2.10.1`.

### v2.10.2 + v2.10.3
- `src/providers/ollama_provider.py` — `OllamaProvider(LLMProvider)` fully implemented:
  - `__init__`: lazy `import ollama`; `ollama.Client(host=ollama_base_url)`; daemon ping via `list()`. Startup-guard: `_available = False` when daemon down or SDK absent.
  - `is_available()` → `self._available`.
  - `analyze()`: text-only; `_JSON_SCHEMA_SUFFIX` enforced; `ollama.Client.chat()`; markdown fence strip; `MedicalReportModel.model_validate_json()`.
  - `ask()`: streaming via `client.chat(stream=True)`; `_stream_and_record()` generator; history appended on exhaustion.
  - `_ensure_model_loaded()`: unloads previous model via `keep_alive=0` before loading new one (VRAM guard, AD-13); pulls model via `ollama.pull()` only when absent from `list()`.
  - DEBUG logging of all VRAM decisions (unload, pull, active model).

### v2.10.4
- `src/providers/factory.py` — `OLLAMA` `NotImplementedError` stub replaced with lazy `OllamaProvider` import. `NotImplementedError` catch removed from `available_providers()`. Module docstring updated.
- `pyproject.toml` — version bumped to `2.10.4`.

---

## Key Existing Code Context

- `src/providers/` — complete: `base.py`, `gemini_provider.py`, `claude_provider.py`, `openai_compatible_provider.py`, `groq_provider.py`, `together_provider.py`, `huggingface_provider.py`, `ollama_provider.py`, `factory.py`, `__init__.py`. All six providers fully implemented. No stubs remaining.
- `src/providers/ollama_provider.py` — `OllamaProvider`: daemon-ping availability, load-on-demand with VRAM guard, streaming chat, text-only (vision multimodal deferred to v2.14.3).
- `src/providers/base.py` — `ProviderRequest` has `context: str` field for text-only providers.
- `src/dsclinic.py` — routes all AI calls through `active_provider`; no direct SDK imports. Document loading produces `genai_types.Part` list — text-only providers receive empty `documents` and rely on `context`.
- `src/db/app_database.py` — `patients`, `sessions`, `reports`, `ai_profiles` fully implemented.
- `src/dsclinic_gui/report_view_models.py` — full patient + session management.
- PII anonymization — working, over-anonymizes clinical values; fix in v2.14.0.

---

## Previously Completed

- **v2.10.4** ✅ — `ProviderFactory` `OLLAMA` stub replaced; all 6 providers registered and reachable.
- **v2.10.3** ✅ — Load-on-demand pull + VRAM sequential guard in `_ensure_model_loaded()`.
- **v2.10.2** ✅ — `OllamaProvider` core: init, analyze, ask, streaming.
- **v2.10.1** ✅ — Ollama config infra: `config.json`, `AppSettings`, `SettingsViewModel`, `SettingsWindow`.
- **v2.9.4** ✅ — `ProviderFactory` stubs replaced; all 5 cloud providers fully registered.
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
