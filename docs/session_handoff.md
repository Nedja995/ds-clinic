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

## Current Status: v2.11.3 ✅ Complete — Next: v2.11.4

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
| v2.11.4 | Clinic Profile settings section | Next |
| v2.11.5 | Subscription tier enforcement stubs | Planned |
| v2.12.0 | Chat Session View rewrite | Planned |
| v2.13.0 | pytest coverage | Planned |
| v2.14.0 | PII improvements + debug panel | Planned |
| v2.15.0 | README case study + architecture diagrams | Planned |

---

## v2.11.3 Changes (completed 2026-09-04)

### Changed
- `src/dsclinic_gui/dsclinic_gui_app.py` — `self.title()` → `brand_config.clinic_name`; `brand_config` imported.
- `src/dsclinic_gui/report_view.py` — `_build_toolbar()`: branded identity block on right side of toolbar:
  - `ttk.Label` showing `clinic_name · clinic_subtitle` (subtitle omitted when empty).
  - Logo: `PIL.Image.open()` → resize 22×22 → `ImageTk.PhotoImage`; ref stored on `self._toolbar_logo_image` (GC guard); whole block try/except skipped on error.
  - `PIL` and `brand_config` imports added.
- `pyproject.toml` — version bumped to `2.11.3`.

### Design note
`brand_config` imported directly in View files — it is presentation-layer configuration, not business logic. ViewModel layer must never import it (MVVM boundary).

---

## v2.11.4 Implementation Notes (for next session)

### Target files
- `src/dsclinic_gui/settings/settings_view_model.py` — add `BrandConfig`-backed vars and save logic.
- `src/dsclinic_gui/settings/settings_view.py` — add "Clinic Profile" card with entry fields + logo picker + tier label.

### ViewModel changes (`settings_view_model.py`)
Add at end of `__init__` (after existing vars):
```python
# v2.11.4 — Clinic profile vars (read from brand_config, written to brand.json)
self.var_clinic_name         = tk.StringVar(value=brand_config.clinic_name)
self.var_clinic_subtitle     = tk.StringVar(value=brand_config.clinic_subtitle)
self.var_clinic_address      = tk.StringVar(value=brand_config.clinic_address)
self.var_report_header_text  = tk.StringVar(value=brand_config.report_header_text)
self.var_report_footer_text  = tk.StringVar(value=brand_config.report_footer_text)
self.var_logo_path           = tk.StringVar(value=brand_config.logo_path)
self.var_subscription_tier   = tk.StringVar(value=brand_config.subscription_tier)
# Delegate set by View — called when logo picker button is clicked (MVVM: no filedialog in VM)
self.on_pick_logo_file: Callable[[], None] | None = None
```

Add save logic in `save_to_config()` before `app_settings.save_unified()`:
```python
# Persist clinic profile to brand.json — separate from app_settings (AD-20)
brand_config.clinic_name        = self.var_clinic_name.get().strip()
brand_config.clinic_subtitle    = self.var_clinic_subtitle.get().strip()
brand_config.clinic_address     = self.var_clinic_address.get().strip()
brand_config.report_header_text = self.var_report_header_text.get().strip()
brand_config.report_footer_text = self.var_report_footer_text.get().strip()
brand_config.logo_path          = self.var_logo_path.get().strip()
try:
    brand_config.save()
except OSError as exc:
    logger.error(f"Failed to save brand.json: {exc}")
```

Add `update_from_config()` refresh for brand vars (at end of the method):
```python
self.var_clinic_name.set(brand_config.clinic_name)
self.var_clinic_subtitle.set(brand_config.clinic_subtitle)
self.var_clinic_address.set(brand_config.clinic_address)
self.var_report_header_text.set(brand_config.report_header_text)
self.var_report_footer_text.set(brand_config.report_footer_text)
self.var_logo_path.set(brand_config.logo_path)
self.var_subscription_tier.set(brand_config.subscription_tier)
```

Import needed: `from models.brand import brand_config` at top of `settings_view_model.py`.

### View changes (`settings_view.py`)
- New `_build_clinic_profile_section()` method — call it in `_setup_ui()` between `_build_patient_data_section()` and `_build_ai_section()`.
- Uses existing `_entry_field()` helper for all text fields.
- Logo picker row: `ttk.Entry` (bound to `var_logo_path`, read-only `state="readonly"`) + `ttk.Button("Browse…")`. Button `command` calls `self._on_logo_pick()` which runs `filedialog.askopenfilename` and sets `view_model.var_logo_path` — file dialog stays in View, ViewModel holds the path string.
- Subscription tier: read-only `ttk.Label` bound to `view_model.var_subscription_tier` with `SUBTLE` foreground.
- `_HEIGHT` bump: +180 px to accommodate the new card.
- Import needed: `from models.brand import brand_config` NOT needed in view — all data flows through ViewModel vars.

---

## Key Existing Code Context

- `src/models/brand.py` — `BrandConfig`, `brand_config` singleton, `is_feature_allowed()`, color helpers, `save()`.
- `src/pdf_maker.py` — fully branded via `brand_config` as of v2.11.2.
- `src/dsclinic_gui/dsclinic_gui_app.py` — window title from `brand_config.clinic_name`.
- `src/dsclinic_gui/report_view.py` — toolbar shows `clinic_name · clinic_subtitle` + logo (22×22).
- `src/dsclinic_gui/settings/settings_view.py` — existing card pattern: `_card(title)` → returns content `ttk.Frame`. `_entry_field()`, `_credential_field()`, `_text_field()` helpers available.
- `src/dsclinic_gui/settings/settings_view_model.py` — existing `save_to_config()` and `update_from_config()` pattern to follow.
- PII anonymization — working, over-anonymizes clinical values; fix in v2.14.0.

---

## Previously Completed

- **v2.11.3** ✅ — Window title + toolbar branding from `brand_config`; logo in toolbar.
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
