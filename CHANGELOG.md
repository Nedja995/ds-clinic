# Changelog

All notable changes to DSClinic will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

See [TODO.md](TODO.md) for planned sub-versions.

## [2.6.3] - 2026-08-30

### Changed
- **`google_api_key` and `anthropic_api_key` fields removed from `AppSettings`:** Credentials no longer exist as model fields. Nothing reads or writes them via `app_settings`.
- **`configparser` / `settings.ini` block removed from `load_unified()`:** Step A1 (INI parsing) deleted entirely. `configparser` import removed.
- **`google_project_location: str = "us-central1"` added to `AppSettings`:** Non-secret location read from `config.json ["google"]["project_location"]` in `load_unified()`.
- **`config.json`:** New `"google": {"project_location": "us-central1"}` block added.
- **`save_unified()` exclude list:** `"google_api_key"` and `"anthropic_api_key"` added defensively; comment added referencing AD-11.

---

## [2.6.2] - 2026-08-30

### Added
- **`src/models/keyring_manager.py`:** Single point of access for the OS-native credential store. Exposes `get_credential(name)`, `set_credential(name, value)`, `delete_credential(name)`.
- **`_KEYRING_SERVICE = "dsclinic"`** — service name for all keyring entries.
- **`_CREDENTIAL_KEYS` mapping:** `"gemini"` → `"gemini_api_key"`, `"anthropic"` → `"anthropic_api_key"`, `"google_project_id"` → `"google_project_id"`.
- **Exported from `src/models/__init__.py`:** `get_credential`, `set_credential`, `delete_credential`.

---

## [2.6.1] - 2026-08-30

### Changed
- **`app_name` and `app_version` sourced from `pyproject.toml`** via `importlib.metadata.metadata("dsclinic")` in `load_unified()`. Falls back to field defaults in frozen builds.
- **`[APP]` block removed from `settings.ini` parsing.**
- **`app_name` and `app_version` excluded from `save_unified()`.**

---

## [2.6.0] - Planned — Secure Credential Management & `settings.ini` Elimination

### Sub-versions
- v2.6.1 ✅ — `app_name`/`app_version` from `pyproject.toml` via `importlib.metadata`.
- v2.6.2 ✅ — New `src/models/keyring_manager.py` module.
- v2.6.3 ✅ — `AppSettings` purged of secret fields + `configparser` block removed.
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
