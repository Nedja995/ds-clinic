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

## Current Status: v2.11.2 ✅ Complete — Next: v2.11.3

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
| v2.11.1 | `BrandConfig` model & loader | ✅ Done |
| v2.11.2 | Dynamic PDF report branding | ✅ Done |
| v2.11.3 | Dynamic GUI branding | Next |
| v2.11.4 | Clinic Profile settings section | Planned |
| v2.11.5 | Subscription tier enforcement stubs | Planned |
| v2.12.0 | Chat Session View rewrite | Planned |
| v2.13.0 | pytest coverage | Planned |
| v2.14.0 | PII improvements + debug panel | Planned |
| v2.15.0 | README case study + architecture diagrams | Planned |

---

## v2.11.2 Changes (completed 2026-09-04)

### Changed
- `src/pdf_maker.py` — full branding decoupled from hardcoded strings:
  - `draw_header()`: `brand_config.clinic_name`, `primary_color_rgb()`, `resolved_logo_path()`, optional `report_header_text` subtitle.
  - `draw_footer_section()`: `brand_config.report_consent_text`, `brand_config.report_footer_text`.
  - `draw_table_foundings()` / `draw_table_therapy()`: `secondary_color_rgb()` for table header fill.
  - `draw_watermark()` new method: diagonal "TRIAL" stamp via `FPDF.rotation()`.
  - `create_report_pdf()`: watermark loop over all pages when `is_feature_allowed("no_watermark")` is `False`.
  - `LOGO_PATH` module constant removed — logo now optional, not fatal.
  - Module-level docstring added.
- `pyproject.toml` — version bumped to `2.11.2`.

---

## v2.11.3 Implementation Notes (for next session)

### Target files to read before implementing
- `src/dsclinic_gui/dsclinic_gui_app.py` — sets the root window title; needs `brand_config.clinic_name`.
- `src/dsclinic_gui/main_container.py` — contains the toolbar/header label; needs `brand_config.clinic_name` + `brand_config.clinic_subtitle`.

### Key changes
- `dsclinic_gui_app.py`: replace `root.title("...")` hardcoded string with `brand_config.clinic_name`. Import `brand_config` from `models`.
- `main_container.py`: locate the toolbar label widget that shows the app name. Replace its text with `f"{brand_config.clinic_name}  {brand_config.clinic_subtitle}".strip()`. If subtitle is empty, show name only.
- Logo in main panel header: if `brand_config.resolved_logo_path()` returns a non-empty path, load and display it with `PIL.Image` + `ImageTk.PhotoImage` in the toolbar. If absent, show no image (no error). Store the `PhotoImage` reference on the widget or parent to prevent GC.
- Both files are in the `mypy` exclude list — no annotation burden, but keep imports clean.
- Do NOT import `brand_config` in any ViewModel — it is View/App-layer configuration.

---

## Key Existing Code Context

- `src/models/brand.py` — `BrandConfig`, `brand_config` singleton, `is_feature_allowed()`, color helpers.
- `src/pdf_maker.py` — fully branded as of v2.11.2; `LOGO_PATH` constant removed.
- `src/providers/` — complete: all six providers implemented, no stubs.
- `src/dsclinic.py` — routes all AI calls through `active_provider`; no direct SDK imports.
- `src/db/app_database.py` — `patients`, `sessions`, `reports`, `ai_profiles` fully implemented.
- `src/dsclinic_gui/report_view_models.py` — full patient + session management.
- PII anonymization — working, over-anonymizes clinical values; fix in v2.14.0.

---

## Previously Completed

- **v2.11.2** ✅ — `pdf_maker.py` fully branded via `brand_config`; watermark; logo optional.
- **v2.11.1** ✅ — `BrandConfig` model, `brand_config` singleton, `brand.json` default file.
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
