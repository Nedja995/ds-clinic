# Changelog

All notable changes to DSClinic will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

See [TODO.md](TODO.md) for planned sub-versions.

## [2.6.5] - 2026-08-30

### Changed
- **`SettingsWindow._build_analyze_instructions_panel`:** Replaced single plain `_entry_field("Google API Key", ...)` with three `_credential_field(...)` calls — Google API Key, Anthropic API Key, Google Project ID.
- **New `_credential_field` helper:** Renders a masked `ttk.Entry` (`show="*"`) plus a `SUBTLE`-coloured hint label `"Stored securely in OS keyring — never written to disk."` Extracted as a dedicated method to keep credential rendering consistent and DRY.
- **`_HEIGHT` bumped from 760 to 860px** to accommodate the two additional credential fields.

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

## [2.6.0] - Planned — Secure Credential Management & `settings.ini` Elimination

### Sub-versions
- v2.6.1 ✅ — `app_name`/`app_version` from `pyproject.toml`.
- v2.6.2 ✅ — `keyring_manager.py`.
- v2.6.3 ✅ — `AppSettings` purged of secret fields + `configparser` block removed.
- v2.6.4 ✅ — `SettingsViewModel` reads/writes via keyring.
- v2.6.5 ✅ — Settings UI masked credential fields + hint labels.
- v2.6.6 — Full audit: `api_gemini/`, `api_claude/`.
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
- Hybrid `AppSettings` Model with `load_unified` and atomic `save_unified`.
- Portability-by-Default Layout.
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
- Horizontal alignment for Support Email and its input Entry.
- Auto-synchronization of active language selection display in Settings combobox.
- Token-optimization filters inside `src/dsclinic.py`.

### Changed
- Reworked "GENERAL" section to hold only Language dropdown and App Version.
- Centered main report panel card titles via `anchor="center"` on `_card` helper label.
- Relocated "Send Logs" and "Show Logs Folder" buttons to new "Support" card section.

### Fixed
- Resolved nested-tuple serialization bug on multiple settings saves in `config.json`.
