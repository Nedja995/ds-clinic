# Changelog

All notable changes to DSClinic will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

See [TODO.md](TODO.md) for planned sub-versions.

## [2.6.6] - 2026-08-30

### Fixed
- **`api_gemini/client.py` — startup guard for missing key:** Replaced `raise ValueError("GOOGLE_API_KEY environment variable is missing.")` with a `logger.warning` + early `return`. App now starts without a key; analysis raises a clear `RuntimeError` at call time instead of crashing at import.
- **`api_claude/client.py` — startup guard for missing key:** Same pattern — replaced `raise ValueError` with `logger.warning` + early `return`. `RuntimeError` raised at `initial_analysis_report_from_chat_stream` / `ask_followup_stream` call time if client was not initialized.
- **`dsclinic.py` — Claude client wired to keyring:** `ClaudeAnalyzerClient` now instantiated using `get_credential("anthropic")`. Wrapped in startup guard — `self.claude_client = None` if key absent.
- **Both clients — guard on `client`/`chat_session` before use:** `initial_analysis_report_from_chat_stream` and `ask_followup_question` check `self.client` is not `None` before proceeding, raising a clear `RuntimeError` with Settings navigation hint.

### Audit
- `src/api_gemini/client.py`: zero `app_settings.*` references — key via `config.api_key` only.
- `src/api_claude/client.py`: zero `app_settings.*` references — key via `config.api_key` only.

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

## [2.6.0] - Planned — Secure Credential Management & `settings.ini` Elimination

### Sub-versions
- v2.6.1 ✅ — `app_name`/`app_version` from `pyproject.toml`.
- v2.6.2 ✅ — `keyring_manager.py`.
- v2.6.3 ✅ — `AppSettings` purged of secret fields + `configparser` block removed.
- v2.6.4 ✅ — `SettingsViewModel` reads/writes via keyring.
- v2.6.5 ✅ — Settings UI masked credential fields + hint labels.
- v2.6.6 ✅ — Both clients startup-guarded; Claude wired to keyring; full audit.
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
