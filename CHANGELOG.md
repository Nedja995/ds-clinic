# Changelog

All notable changes to DSClinic will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

See [TODO.md](TODO.md) for planned sub-versions.

## [2.6.1] - 2026-08-30

### Changed
- **`app_name` and `app_version` sourced from `pyproject.toml`:** `AppSettings.load_unified()` now reads both values at runtime via `importlib.metadata.metadata("dsclinic")` as step A0, before any other source. Falls back silently to `AppSettings` field defaults when running from a frozen/non-installed build.
- **`[APP]` block removed from `settings.ini` parsing:** NAME and VERSION are no longer read from `settings.ini`. Only `[GOOGLE]` and `[ANTHROPIC]` key blocks remain in the INI reader (temporary — removed in v2.6.3).
- **`app_name` and `app_version` excluded from `save_unified()`:** Both fields added to `exclude_fields` so they are never written back to `settings.json`.
- **`pyproject.toml` is now the single source of truth** for `app_name` and `app_version`.

---

## [2.6.0] - Planned — Secure Credential Management & `settings.ini` Elimination

### Security
- Keyring-based credential storage for all API keys and Google Project ID.
- `settings.ini` fully deleted from project.
- Masked key entry fields in Settings UI, reading from and writing to keyring only.
- `AppSettings` purged of all secret fields.
- `DSClinic.__init__` reads Gemini key from keyring via `get_credential("gemini")`.

### Changed
- `app_name` / `app_version` sourced from `pyproject.toml` via `importlib.metadata` ✅ (v2.6.1).
- `GOOGLE_PROJECT_LOCATION` moved to `config.json`.
- `configparser` / `settings.ini` parsing block removed from `load_unified()`.
- `keyring` added to `pyproject.toml` dependencies.

### Sub-versions
- v2.6.1 ✅ — `app_name`/`app_version` from `pyproject.toml` via `importlib.metadata`.
- v2.6.2 — New `src/models/keyring_manager.py` module.
- v2.6.3 — `AppSettings` purged of secret fields + `configparser` block removed.
- v2.6.4 — `SettingsViewModel` reads/writes via keyring.
- v2.6.5 — Settings UI masked key fields + hint labels.
- v2.6.6 — Runtime key consumption in `dsclinic.py`, `api_gemini/`, `api_claude/`.
- v2.6.7 — Rotate keys, `git rm settings.ini`, final audit.

---

## [2.5.0] - Planned — Chat Session View & Pluggable Multi-Provider Pipeline

### Added
- Chat Session View full rewrite with streaming bubble fix and `MarkdownLabel.update_text()`.
- `LLMProvider` abstraction (Gemini, Claude, Groq, Together, HuggingFace, Local Ollama).
- PII Anonymization Layer (Presidio-based local scrubbing).
- `pytest` coverage for parsing, anonymization, provider fallback logic.

---

## [2.3.0] - 2026-08-29

### Added
- Unified `src/models/` Package.
- Hybrid `AppSettings` Model (`src/models/settings.py`) with `load_unified` and atomic `save_unified`.
- Portability-by-Default Layout (`.config/medai_vitec` adjacent to executable).
- `settings.ini` fallback integration (superseded by v2.6.x).

### Changed
- Codebase-wide refactor to `from models import app_settings`.
- Settings UI ViewModel and Window migrated to `app_settings`.

### Removed
- Legacy `src/models.py`, `src/models_new/`, `src/config.py`, `src/npy/core/settings_manager.py`.

---

## [2.1.10] - 2026-08-28

### Added
- Brand-new "SUPPORT" card section inside the Settings window.
- Horizontal alignment for Support Email and its input Entry in the Support section.
- Auto-synchronization of active language selection display in Settings combobox.
- Token-optimization filters inside `src/dsclinic.py`.

### Changed
- Reworked "GENERAL" section to hold only Language dropdown and App Version.
- Centered main report panel card titles via `anchor="center"` on `_card` helper label.
- Relocated "Send Logs" and "Show Logs Folder" buttons to new "Support" card section.

### Fixed
- Resolved nested-tuple serialization bug on multiple settings saves in `config.json`.
