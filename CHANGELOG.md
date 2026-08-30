# Changelog

All notable changes to DSClinic will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

See [TODO.md](TODO.md) for planned sub-versions.

## [2.6.4] - 2026-08-30

### Changed
- **`SettingsViewModel.__init__`:** `var_google_api_key` now reads from `get_credential("gemini")` instead of `app_settings.google_api_key`. Two new vars added: `var_anthropic_api_key` (`get_credential("anthropic")`) and `var_google_project_id` (`get_credential("google_project_id")`).
- **`SettingsViewModel.update_from_config()`:** All three credential vars refreshed from keyring. No `app_settings.*_api_key` reads anywhere in the method.
- **`SettingsViewModel.save_to_config()`:** Credentials written via `set_credential(...)` after `save_unified()`. `app_settings.google_api_key` assignment removed entirely.
- **Import:** `get_credential`, `set_credential` imported from `models`.

---

## [2.6.3] - 2026-08-30

### Changed
- `google_api_key` and `anthropic_api_key` fields removed from `AppSettings`.
- Entire `configparser` / `settings.ini` INI block removed from `load_unified()`.
- `google_project_location: str = "us-central1"` added to `AppSettings`, read from `config.json ["google"]["project_location"]`.
- `config.json`: `"google": {"project_location": "us-central1"}` block added.
- `save_unified()` exclude list updated with defensive entries for removed secret fields.
- **Hotfix:** `dsclinic.py` patched to use `get_credential("gemini")` — unblocks app startup.

---

## [2.6.2] - 2026-08-30

### Added
- `src/models/keyring_manager.py` with `get_credential`, `set_credential`, `delete_credential`.
- Exported from `src/models/__init__.py`.

---

## [2.6.1] - 2026-08-30

### Changed
- `app_name`/`app_version` sourced from `pyproject.toml` via `importlib.metadata` in `load_unified()`.
- `[APP]` INI block removed. Both fields excluded from `save_unified()`.

---

## [2.6.0] - Planned — Secure Credential Management & `settings.ini` Elimination

### Sub-versions
- v2.6.1 ✅ — `app_name`/`app_version` from `pyproject.toml`.
- v2.6.2 ✅ — `keyring_manager.py`.
- v2.6.3 ✅ — `AppSettings` purged of secret fields + `configparser` block removed.
- v2.6.4 ✅ — `SettingsViewModel` reads/writes via keyring.
- v2.6.5 — Settings UI masked key fields + hint labels.
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
