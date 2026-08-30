# Changelog

All notable changes to DSClinic will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

See [TODO.md](TODO.md) for planned sub-versions.

## [2.6.0] - Planned — Secure Credential Management & `settings.ini` Elimination

### Security
- **Keyring-based credential storage (`src/models/keyring_manager.py`):** All API keys (`GOOGLE_API_KEY`, `ANTHROPIC_API_KEY`) and the Google Project ID (`GOOGLE_PROJECT_ID`) moved from `settings.ini` into the OS-native credential store (Windows Credential Manager / macOS Keychain / libsecret) via the `keyring` library. Keys are never written to any file on disk.
- **`settings.ini` fully deleted:** File removed from disk and from git history. No longer gitignored — it simply does not exist.
- **Masked key entry fields in Settings UI:** All credential entry fields use `show="*"`. Each field reads from and writes to keyring only. A hint label confirms: "Stored securely in OS keyring — never written to disk."
- **`AppSettings` purged of secret fields:** `google_api_key` and `anthropic_api_key` fields removed from `AppSettings`. They are never loaded from `settings.json` or any disk file.
- **`DSClinic.__init__` reads from keyring:** `get_credential("gemini")` replaces `app_settings.google_api_key`. Logs a clear warning if the key is not configured, instead of crashing.

### Changed
- **`app_name` and `app_version` sourced from `pyproject.toml`:** Read at runtime via `importlib.metadata.metadata("dsclinic")`. Single source of truth — no more version duplication between `settings.ini` and `pyproject.toml`.
- **`GOOGLE_PROJECT_LOCATION` moved to `config.json`:** Non-secret location string (`"us-central1"`) stored in the committed `config.json` under `"google": { "project_location": "..." }` and exposed as a normal `AppSettings` field.
- **`configparser` / `settings.ini` parsing block removed from `AppSettings.load_unified()`.**
- **`keyring` added to `pyproject.toml` dependencies.**

### Sub-versions
- v2.6.1 — Manual security triage: rotate exposed keys, `git rm --cached settings.ini`.
- v2.6.2 — `pyproject.toml` as single source of truth for `app_name` / `app_version` via `importlib.metadata`.
- v2.6.3 — New `src/models/keyring_manager.py` module.
- v2.6.4 — `AppSettings` and `load_unified()` purged of all secret fields and `settings.ini` parsing.
- v2.6.5 — Settings UI masked key fields with keyring read/write.
- v2.6.6 — Runtime key consumption updated in `dsclinic.py`, `api_gemini/`, `api_claude/`.
- v2.6.7 — Delete `settings.ini`, final codebase audit, `GEMINI.md` update.

---

## [2.5.0] - Planned — Chat Session View & Pluggable Multi-Provider Pipeline

### Added
- **Chat Session View:** Full rewrite of `chat_session_view.py` with streaming bubble fix, `MarkdownLabel.update_text()` for in-place streaming, correct user/bot bubble alignment and colors.
- **`LLMProvider` Abstraction:** Pluggable multi-provider interface (Gemini, Claude, Groq, Together, HuggingFace, Local Ollama).
- **PII Anonymization Layer:** Presidio-based local scrubbing before any cloud API call.
- **`pytest` Coverage:** Automated tests for parsing, anonymization, and provider fallback logic.

---

## [2.3.0] - 2026-08-29

### Added
- **Unified `src/models/` Package**: Consolidated all core domain schemas and configurations into a structured package folder, separating concerns into `ai.py`, `patient.py`, and `diagnostics.py`.
- **Hybrid `AppSettings` Model (`src/models/settings.py`)**: Pydantic-Settings-based single source of truth with `load_unified` and atomic `save_unified`.
- **Portability-by-Default Layout**: `.config/medai_vitec` always local and adjacent to the executable.
- **`settings.ini` Fallback Integration**: Baseline fallback parsing for API keys, App Name, and Version inside `load_unified()` (superseded by v2.6.0).

### Changed
- Refactored `dsclinic.py`, `dsclinic_cli.py`, `src/npy/core/fileutils.py`, `src/api_gemini/utils.py`, and `src/api_claude/utils.py` to use `from models import app_settings`.
- Migrated Settings UI ViewModel and Window to bind directly to `app_settings`.

### Removed
- Deleted legacy flat file `src/models.py`.
- Deleted deprecated `src/models_new/` directory.
- Deleted legacy `src/config.py` module-globals configuration loader.
- Deleted legacy `src/npy/core/settings_manager.py`.

---

## [2.1.10] - 2026-08-28

### Added
- Brand-new "SUPPORT" card section inside the Settings window.
- Horizontal alignment for Support Email and its input Entry in the Support section.
- Auto-synchronization of the active language selection display in Settings combobox.
- Token-optimization filters inside `src/dsclinic.py` to strip newlines and double spaces before Gemini API calls.

### Changed
- Reworked "GENERAL" section inside the Settings window to hold only Language dropdown and App Version.
- Centered main report panel card titles responsively via `anchor="center"` on the `_card` helper label.
- Relocated "Send Logs" and "Show Logs Folder" buttons to the new "Support" card section.

### Fixed
- Resolved a bug where multiple saves of the Settings window wrapped the initial task description list into recursive tuple strings inside `config.json`.
