# Changelog

All notable changes to DSClinic will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

See [TODO.md](TODO.md) for planned versions.

---

## [2.15.0] - Planned — README Engineering Case Study + Architecture Diagrams
- `README.md` full rewrite as portfolio engineering case study.
- Architecture diagrams: Split-Horizon pipeline, MVVM layers, `LLMProvider` class diagram, patient data flow.
- Final `GEMINI.md` and `docs/architecture.md` review pass.

## [2.14.0] - Planned — PII Anonymization Improvements + Debug Panel
- Root cause analysis and Presidio entity tuning for over-anonymization of clinical values.
- Side-by-side PII debug panel (toggle via `app_settings.app_debug_response`).
- Regex allowlist for clinical value patterns (`mmol/L`, `mg/dL`, `mmHg`, etc.).
- Local model integration stubs: Llama 3.2 Vision second-pass checker, MONAI DICOM slice stub.

## [2.13.0] - Planned — pytest Coverage
- pytest infrastructure: `tests/`, `conftest.py`, `pytest.ini`.
- PII scrubber tests: redaction coverage + over-anonymization regression tests.
- Medical report parser tests: `MedicalReportModel` good/bad JSON fixtures.
- Provider abstraction tests: `ProviderFactory` routing with mocked keyring.
- `AppDatabase` / `JsonCollection` CRUD + index tests.
- `AppSettings` / `load_unified` + `BrandConfig` fallback tests.

## [2.12.0] - Planned — Chat Session View Rewrite + New Features
- Streaming bubble fix: `MarkdownLabel.update_text()` + `_current_bot_bubble` tracking.
- `ChatUser` style fix: solid `ACCENT` blue + `WHITE` text.
- Provider selector dropdown in chat toolbar.
- Reanalyze command with additional prompt input.
- Report inclusion checkboxes per response bubble (`include_in_report` flag in `ChatMessage`).

## [2.11.0] - Planned — Enterprise Multi-Brand / White-Label & Subscription Config
- `BrandConfig` model + `brand.json` loader with fallback defaults.
- Dynamic PDF branding: logo, clinic name, header/footer, color scheme, trial watermark.
- Dynamic GUI branding: window title, toolbar header, logo in main panel.
- Clinic Profile settings card in Settings UI.
- Subscription tier enforcement stubs: `trial` / `standard` / `enterprise`.

## [2.10.0] - Planned — Local Ollama Provider (16GB VRAM Optimized)
- `OllamaProvider(LLMProvider)` with `is_available()` daemon ping.
- Load-on-demand: model pulled only when first needed.
- 4-bit quantization via Ollama model name tags.
- Sequential VRAM guard: one model loaded at a time.
- Ollama base URL in `AppSettings` + Settings UI "Local AI" section.

## [2.9.0] - Planned — Groq + Together AI + HuggingFace Cloud Providers
- Keyring credentials + Settings UI fields for Groq, Together, HuggingFace.
- `GroqProvider`, `TogetherProvider`, `HuggingFaceProvider` concrete implementations.
- New SDK dependencies: `groq`, `together`, `huggingface_hub`.
- All three registered in `ProviderFactory`.

## [2.8.0] - Planned — `src/providers/` LLMProvider Abstraction (Gemini + Claude)
- `src/providers/` package: `base.py` (ABC + data contracts), `factory.py`, `gemini_provider.py`, `claude_provider.py`.
- `LLMProvider` ABC: `analyze()`, `ask()`, `provider_type()`, `is_available()`.
- `ProviderFactory.create()` and `ProviderFactory.available_providers()`.
- `DSClinic` refactored to use `ProviderFactory` — direct SDK client coupling removed.

## [2.7.0] - Planned — Patient Record as First-Class Entity & Session Persistence
- `PatientRecord` model added to `src/models/patient.py`.
- `AppDatabase.patients` collection added.
- `AppDatabase` wired into `DSClinicViewModel` — reports and sessions auto-saved after analysis.
- Session history panel + patient list panel in main View.

---

## [2.5.0] - Planned — MVVM Strict Compliance & Defensive Error Handling Audit
- Full MVVM boundary audit: zero widget imports in ViewModels, no direct dialog calls.
- Defensive error handling: no bare `except:`, all I/O wrapped, all thread failures queued.
- Type hints audit: `mypy --strict src/` passing.

---

## [2.6.7] - 2026-08-30

### Security
- `settings.ini` permanently deleted from the repository (`git rm settings.ini`).
- Both `GOOGLE_API_KEY` and `ANTHROPIC_API_KEY` regenerated and entered via Settings UI → written to OS keyring.
- App verified working end-to-end with keyring-sourced Gemini key.

### Changed
- `GEMINI.md` § 2 Technical Stack: Added `keyring` / `keyring_manager.py`.
- `GEMINI.md` § 3.D Coding Conventions: Added credential management rule (AD-11 reference) and client startup guard pattern.

---

## [2.6.6] - 2026-08-30

### Fixed
- `api_gemini/client.py` — replaced `raise ValueError` on missing key with `logger.warning` + early `return`.
- `api_claude/client.py` — same startup guard pattern applied.
- `dsclinic.py` — `ClaudeAnalyzerClient` wired to keyring; startup guard added.
- Both clients guard `self.client` before use — `RuntimeError` with Settings navigation hint if called without a key.

---

## [2.6.5] - 2026-08-30

### Changed
- New `_credential_field` helper: masked `ttk.Entry` (`show="*"`) + `SUBTLE`-coloured hint label.
- Three credential fields in Settings UI: Google API Key, Anthropic API Key, Google Project ID.
- `_HEIGHT` bumped from 760 to 860px.

---

## [2.6.4] - 2026-08-30

### Changed
- `SettingsViewModel` reads all three credentials from keyring on init and `update_from_config()`.
- Writes all three via `set_credential()` in `save_to_config()`.
- `app_settings.google_api_key` assignment removed entirely.

---

## [2.6.3] - 2026-08-30

### Changed
- `google_api_key`/`anthropic_api_key` removed from `AppSettings`.
- `configparser`/`settings.ini` block removed from `load_unified()`.
- `google_project_location` field added; read from `config.json`.
- Hotfix: `dsclinic.py` uses `get_credential("gemini")`.

---

## [2.6.2] - 2026-08-30

### Added
- `src/models/keyring_manager.py` with `get_credential`, `set_credential`, `delete_credential`.
- Exported from `src/models/__init__.py`.

---

## [2.6.1] - 2026-08-30

### Changed
- `app_name`/`app_version` sourced from `pyproject.toml` via `importlib.metadata`.
- `[APP]` INI block removed. Both fields excluded from `save_unified()`.

---

## [2.6.0] - 2026-08-30 — Secure Credential Management & `settings.ini` Elimination ✅ Released

### Security
- All API keys and sensitive identifiers moved to OS-native credential store via `keyring`.
- `settings.ini` permanently deleted.
- Settings UI credential fields masked with keyring hint labels.
- `AppSettings` purged of all secret fields.

### Changed
- `app_name`/`app_version` sourced from `pyproject.toml` via `importlib.metadata`.
- `GOOGLE_PROJECT_LOCATION` moved to `config.json`.
- `GEMINI.md` updated with credential management rules and startup guard pattern.

---

## [2.3.0] - 2026-08-29

### Added
- Unified `src/models/` Package with `patient.py`, `ai.py`, `diagnostics.py`, `settings.py`.
- Hybrid `AppSettings` Model with `load_unified` and atomic `save_unified`.
- Portability-by-Default Layout.

### Changed
- Codebase-wide refactor to `from models import app_settings`.
- Settings UI ViewModel and Window migrated to `app_settings`.

### Removed
- Legacy `src/models.py`, `src/models_new/`, `src/config.py`, `src/npy/core/settings_manager.py`.

---

## [2.1.10] - 2026-08-28

### Added
- Brand-new "SUPPORT" card section inside the Settings window.
- Horizontal alignment for Support Email and its input Entry.
- Auto-synchronization of active language selection display in Settings combobox.
- Token-optimization filters inside `src/dsclinic.py`.

### Changed
- Reworked "GENERAL" section to hold only Language dropdown and App Version.
- Centered main report panel card titles via `anchor="center"` on `_card` helper label.
- Relocated "Send Logs" and "Show Logs Folder" buttons to new "Support" card section.

### Fixed
- Resolved nested-tuple serialization bug on multiple settings saves in `config.json`.
