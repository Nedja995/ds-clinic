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

## Current Status: v2.11.5 ✅ Complete — v2.11.0 ✅ Complete — Next: v2.12.0

| Version | Scope | Status |
|---|---|---|
| v2.5.1 – v2.5.4 | MVVM audit, error handling, mypy, uv | ✅ Done |
| v2.7.1 – v2.7.4 | PatientRecord, AppDatabase, session/patient panels | ✅ Done |
| v2.8.1 – v2.8.4 | LLMProvider abstraction, GeminiProvider, ClaudeProvider | ✅ Done |
| v2.9.1 – v2.9.4 | Groq, Together, HuggingFace providers | ✅ Done |
| v2.10.1 – v2.10.4 | OllamaProvider, VRAM guard, config | ✅ Done |
| v2.11.1 | `BrandConfig` model & loader | ✅ Done |
| v2.11.2 | Dynamic PDF report branding | ✅ Done |
| v2.11.3 | Dynamic GUI branding | ✅ Done |
| v2.11.4 | Clinic Profile settings section | ✅ Done |
| v2.11.5 | Subscription tier enforcement stubs | ✅ Done |
| v2.12.0 | Chat Session View rewrite | Next |
| v2.13.0 | pytest coverage | Planned |
| v2.14.0 | PII improvements + debug panel | Planned |
| v2.15.0 | README case study + architecture diagrams | Planned |

---

## v2.11.5 Changes (completed 2026-09-04)

### Changed
- `src/dsclinic_gui/report_view_models.py`:
  - `brand_config` imported from `models.brand`.
  - `_TRIAL_DAILY_LIMIT = 3` module-level constant.
  - `_start_analysis()`: trial gate calls `is_feature_allowed("unlimited_sessions")`; when `False`, counts today's sessions by ISO date prefix on `list_index()`. Blocks with error message if count ≥ limit. DB read failure defaults to 0 (never silently blocks). Standard/enterprise tiers: gate not entered, zero overhead.
- `src/providers/factory.py` — `available_providers()`: enterprise stub — lazy-imports `brand_config`, logs DEBUG when `is_feature_allowed("custom_models")` is `True`. Wrapped in `except Exception: pass`.
- `pyproject.toml` — version bumped to `2.11.5`.
- `TODO.md` / `CHANGELOG.md` — v2.11.0 parent marked ✅ Completed.

---

## v2.11.0 — Complete Architecture Summary

| Sub-version | Deliverable |
|---|---|
| v2.11.1 | `BrandConfig(BaseModel)`, `brand_config` singleton, `brand.json`, `is_feature_allowed()`, color helpers |
| v2.11.2 | `pdf_maker.py` fully branded — clinic name, colors, logo, footer, trial watermark |
| v2.11.3 | Window title + toolbar label + toolbar logo from `brand_config` |
| v2.11.4 | "Clinic Profile" settings card — all brand fields editable, logo picker, brand.json saved on Settings save |
| v2.11.5 | Trial daily limit gate in `_start_analysis()`; enterprise stub in `ProviderFactory` |

---

## Key Existing Code Context

- `src/models/brand.py` — `BrandConfig`, `brand_config`, `is_feature_allowed()`, `_TIER_FEATURES`, `save()`, `resolved_logo_path()`, color helpers.
- `src/pdf_maker.py` — fully branded; watermark on trial; logo optional.
- `src/dsclinic_gui/dsclinic_gui_app.py` — window title from `brand_config.clinic_name`.
- `src/dsclinic_gui/report_view.py` — toolbar: `clinic_name · clinic_subtitle` + 22×22 logo.
- `src/dsclinic_gui/settings/settings_view_model.py` — full clinic profile vars, `brand_config.save()` on save.
- `src/dsclinic_gui/settings/settings_view.py` — "CLINIC PROFILE" card, logo picker, tier label.
- `src/dsclinic_gui/report_view_models.py` — `_TRIAL_DAILY_LIMIT`, trial gate in `_start_analysis()`.
- `src/providers/factory.py` — enterprise DEBUG stub in `available_providers()`.
- `src/providers/` — all six providers fully implemented, no stubs.
- `src/db/app_database.py` — `patients`, `sessions`, `reports`, `ai_profiles`.
- PII anonymization — working; over-anonymization fix in v2.14.0.

---

## Previously Completed

- **v2.11.5** ✅ — Trial session gate; enterprise stub in ProviderFactory. v2.11.0 complete.
- **v2.11.4** ✅ — Clinic Profile settings card; brand.json editable from UI.
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
