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

## Current Status: v2.11.1 ✅ Complete — Next: v2.11.2

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
| v2.11.2 | Dynamic PDF report branding | Next |
| v2.11.3 | Dynamic GUI branding | Planned |
| v2.11.4 | Clinic Profile settings section | Planned |
| v2.11.5 | Subscription tier enforcement stubs | Planned |
| v2.12.0 | Chat Session View rewrite | Planned |
| v2.13.0 | pytest coverage | Planned |
| v2.14.0 | PII improvements + debug panel | Planned |
| v2.15.0 | README case study + architecture diagrams | Planned |

---

## v2.11.1 Changes (completed 2026-09-04)

### New Files
- `src/models/brand.py` — `BrandConfig(BaseModel)` with full field set, `load()`, `save()`, `resolved_logo_path()`, `is_feature_allowed()`, `primary_color_rgb()`, `secondary_color_rgb()`. `_hex_to_rgb()` helper. `brand_config` singleton initialized on import.
- `brand.json` — default deployable config at project root: `"MedAI - ViTec"`, `"standard"` tier.

### Changed
- `src/models/__init__.py` — `BrandConfig` and `brand_config` exported.
- `pyproject.toml` — version bumped to `2.11.1`.

### Key design decisions
- `brand.json` resolved via `get_base_dir_path()` — works in both dev (project root) and frozen PyInstaller build (executable dir). AD-09.
- `BrandConfig` has NO dependency on `AppSettings` and vice versa — clean separation per AD-20.
- `is_feature_allowed()` uses `_TIER_FEATURES` dict; enterprise is a superset of standard; unknown features default `False` (safe by default).
- `primary_color` / `secondary_color` drive PDF only in v2.11.x — GUI theme color support deferred.
- Default `clinic_name` is `"MedAI - ViTec"` (the enterprise product name, not the original single-clinic hardcoded string).

---

## v2.11.2 Implementation Notes (for next session)

### Target: `pdf_maker.py` — replace all hardcoded branding with `brand_config` reads

Key changes:
- Import `brand_config` from `models` at the top of `pdf_maker.py`.
- `LOGO_PATH` constant: replace the current `utils.get_resource_filepath("logo.png")` (which raises on missing file) with `brand_config.resolved_logo_path()` — returns empty string gracefully when logo absent.
- `HolisticReport.__init__`: remove the `if not os.path.exists(LOGO_PATH): raise Exception(...)` guard — logo rendering is now optional, not fatal.
- `draw_header()`: replace hardcoded `"HOLISTIČKI CENTAR DAR PRIRODE"` title string with `brand_config.clinic_name`. Replace `set_text_color(0, 51, 102)` with `brand_config.primary_color_rgb()` unpacked. Logo render: use `brand_config.resolved_logo_path()` — skip if empty.
- `draw_footer_section()`: replace hardcoded consent/note strings with `brand_config.report_consent_text` and `brand_config.report_footer_text`.
- Trial watermark: add `_draw_watermark(self)` method on `HolisticReport`. Called from `create_report_pdf()` when `brand_config.is_feature_allowed("no_watermark")` is `False`. Watermark is diagonal text across the page center using `FPDF.rotate()` + `cell()` in light gray.
- `draw_patient_info()`: if `brand_config.report_header_text` is non-empty, render it as a subtitle line below the clinic name in the header.
- `set_fill_color` for table headers: use `brand_config.secondary_color_rgb()`.
- `pdf_maker.py` is in the `mypy` exclude list — no type annotation burden, but keep the `brand_config` import clean.

### Watermark implementation sketch
```python
def _draw_watermark(self) -> None:
    # Diagonal "TRIAL" stamp — rendered behind content using transparency trick
    # (FPDF2 doesn't support true alpha; use light gray color as visual cue)
    self.set_font(FONT_BOLD, "", 60)
    self.set_text_color(220, 220, 220)
    with self.rotation(45, x=self.w / 2, y=self.h / 2):
        self.text(x=self.w / 2 - 60, y=self.h / 2, txt="TRIAL")
    self.set_text_color(0, 0, 0)  # reset
```

---

## Key Existing Code Context

- `src/models/brand.py` — NEW: `BrandConfig`, `brand_config` singleton, `is_feature_allowed()`, color helpers.
- `src/providers/` — complete: `base.py`, `gemini_provider.py`, `claude_provider.py`, `openai_compatible_provider.py`, `groq_provider.py`, `together_provider.py`, `huggingface_provider.py`, `ollama_provider.py`, `factory.py`, `__init__.py`. All six providers fully implemented. No stubs remaining.
- `src/providers/ollama_provider.py` — `OllamaProvider`: daemon-ping availability, load-on-demand with VRAM guard, streaming chat, text-only (vision multimodal deferred to v2.14.3).
- `src/providers/base.py` — `ProviderRequest` has `context: str` field for text-only providers.
- `src/dsclinic.py` — routes all AI calls through `active_provider`; no direct SDK imports. Document loading produces `genai_types.Part` list — text-only providers receive empty `documents` and rely on `context`.
- `src/db/app_database.py` — `patients`, `sessions`, `reports`, `ai_profiles` fully implemented.
- `src/dsclinic_gui/report_view_models.py` — full patient + session management.
- `src/pdf_maker.py` — all clinic branding currently hardcoded; target for v2.11.2.
- PII anonymization — working, over-anonymizes clinical values; fix in v2.14.0.

---

## Previously Completed

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
