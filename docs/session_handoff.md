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

## Current Status: v2.11.4 ✅ Complete — Next: v2.11.5

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
| v2.11.3 | Dynamic GUI branding | ✅ Done |
| v2.11.4 | Clinic Profile settings section | ✅ Done |
| v2.11.5 | Subscription tier enforcement stubs | Next |
| v2.12.0 | Chat Session View rewrite | Planned |
| v2.13.0 | pytest coverage | Planned |
| v2.14.0 | PII improvements + debug panel | Planned |
| v2.15.0 | README case study + architecture diagrams | Planned |

---

## v2.11.4 Changes (completed 2026-09-04)

### Changed
- `src/dsclinic_gui/settings/settings_view_model.py`:
  - `brand_config` imported from `models.brand`.
  - 7 clinic profile `tk.StringVar` vars + `on_pick_logo_file` delegate.
  - `update_from_config()` refreshes clinic profile from `brand_config`.
  - `save_to_config()` mutates `brand_config` fields and calls `brand_config.save()`.
- `src/dsclinic_gui/settings/settings_view.py`:
  - `_build_clinic_profile_section()` — "CLINIC PROFILE" card, first in scroll area.
  - `_on_logo_pick()` — `filedialog.askopenfilename`, sets `var_logo_path`.
  - `on_pick_logo_file` delegate wired in `__init__` before `_setup_ui()`.
  - `_HEIGHT` 1160 → 1380.
- `pyproject.toml` — version bumped to `2.11.4`.

---

## v2.11.5 Implementation Notes (for next session)

### Scope
Subscription tier enforcement stubs. `brand_config.is_feature_allowed()` is already implemented in `src/models/brand.py` — this sub-version wires it into application behaviour.

### Changes needed

**Trial tier — session limit warning (`src/dsclinic_gui/report_view_models.py`)**
- Add a session counter check in `toggle_analysis()` (or the worker launch path).
- `brand_config.is_feature_allowed("unlimited_sessions")` → if `False`, check count of today's sessions from `_db.sessions.list_index()` filtered by today's date. If count ≥ `_TRIAL_DAILY_LIMIT` (e.g. 3), emit `on_show_error_message` with a tier upgrade message and return without launching analysis.
- `_TRIAL_DAILY_LIMIT = 3` module-level constant in `report_view_models.py`.

**Standard / Enterprise — no action needed** (both allow `unlimited_sessions`).

**Enterprise stub — `is_feature_allowed("multi_user")` / `"custom_models"`**
- Add `is_enterprise_feature_stub(feature: str) -> bool` to `src/models/brand.py` — not needed, `is_feature_allowed()` already returns `False` for enterprise features on non-enterprise tiers with a DEBUG log. No additional code needed unless a UI gate is required.
- For the portfolio demo: add a `DEBUG`-level log in `ProviderFactory.available_providers()` when `brand_config.subscription_tier == "enterprise"` — `"[Enterprise] Custom model provider routing available"`. This makes the stub visible in logs without affecting behaviour.

**Watermark already active** — done in v2.11.2. No changes needed.

### Files to touch
- `src/dsclinic_gui/report_view_models.py` — session limit gate in analysis launch path.
- `src/providers/factory.py` — enterprise DEBUG log stub (one line).
- `pyproject.toml`, `CHANGELOG.md`, `TODO.md`, `session_handoff.md` — standard doc updates.

---

## Key Existing Code Context

- `src/models/brand.py` — `BrandConfig`, `brand_config`, `is_feature_allowed()`, `_TIER_FEATURES`, `save()`.
- `src/dsclinic_gui/settings/settings_view_model.py` — full clinic profile vars + save/refresh wired.
- `src/dsclinic_gui/settings/settings_view.py` — "CLINIC PROFILE" card with logo picker and tier label.
- `src/pdf_maker.py` — fully branded, watermark on trial tier.
- `src/dsclinic_gui/dsclinic_gui_app.py` — window title from `brand_config.clinic_name`.
- `src/dsclinic_gui/report_view.py` — toolbar shows `clinic_name · clinic_subtitle` + 22×22 logo.
- `src/providers/` — all six providers implemented, no stubs.

---

## Previously Completed

- **v2.11.4** ✅ — Clinic Profile settings section; brand.json editable from UI.
- **v2.11.3** ✅ — Window title + toolbar branding from `brand_config`; logo in toolbar.
- **v2.11.2** ✅ — `pdf_maker.py` fully branded; watermark on trial; logo optional.
- **v2.11.1** ✅ — `BrandConfig` model, `brand_config` singleton, `brand.json` default file.
- **v2.10.4** ✅ — `ProviderFactory` `OLLAMA` stub replaced; all 6 providers registered.
- **v2.10.3** ✅ — Load-on-demand pull + VRAM sequential guard.
- **v2.10.2** ✅ — `OllamaProvider` core: init, analyze, ask, streaming.
- **v2.10.1** ✅ — Ollama config infra.
- **v2.9.4** ✅ — All 5 cloud providers registered in `ProviderFactory`.
- **v2.9.3** ✅ — `GroqProvider`, `TogetherProvider`, `HuggingFaceProvider`.
- **v2.9.2** ✅ — `OpenAICompatibleProvider` shared base.
- **v2.9.1** ✅ — Credential infra, `AppSettings`, Settings UI, `config.json`.
- **v2.8.4** ✅ — `DSClinic` refactored to `ProviderFactory`.
- **v2.8.3** ✅ — `ProviderFactory` + `__init__.py` exports.
- **v2.8.2** ✅ — `GeminiProvider` + `ClaudeProvider`.
- **v2.8.1** ✅ — `src/providers/` package + `base.py`.
- **v2.7.4** ✅ — Patient list panel, session linkage.
- **v2.7.3** ✅ — `SessionHistoryView` sidebar.
- **v2.7.2** ✅ — `AppDatabase` wired.
- **v2.7.1** ✅ — `PatientRecord` model.
- **v2.6.0** ✅ — Credentials to OS keyring.
- **v2.5.0** ✅ — MVVM audit, error handling, `mypy --strict`, `uv` migration.
