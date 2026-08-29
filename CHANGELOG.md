# Changelog

All notable changes to DSClinic will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

See [TODO.md](TODO.md) for planned sub-versions.

## [2.3.0] - 2026-08-29

### Added
- **Unified `src/models/` Package**: Consolidated all core domain schemas and configurations into a structured package folder, separating concerns into `ai.py` (chat message, LLM configs, chat session, service setups), `patient.py` (medical report, therapies, critical findings), and `diagnostics.py` (TaskStatus, ProgressEvent, ObservableList).
- **Hybrid `AppSettings` Model (`src/models/settings.py`)**: Built a robust Pydantic-Settings-based `AppSettings` model serving as the single source of truth for both static configurations and user overrides. Features a comprehensive loader `load_unified` and atomic writer `save_unified` directly on the class.
- **Portability-by-Default Layout**: Structured configuration directory (`.config/medai_vitec`) to always reside fully local and adjacent to the application base path (executable directory), creating an out-of-the-box portable application layout.
- **`settings.ini` Fallback Integration**: Added baseline fallback parsing for API keys, App Name, and Version directly from the local `settings.ini` inside `load_unified()`, with seamless override layering from `settings.json` and environmental variables.

### Changed
- Refactored `dsclinic.py`, `dsclinic_cli.py`, `src/npy/core/fileutils.py`, `src/api_gemini/utils.py`, and `src/api_claude/utils.py` codebase-wide to replace legacy global module variable calls with type-safe references to `from models import app_settings`.
- Migrated Settings UI ViewModel and Window to bind directly to and save atomically from `app_settings`.

### Removed
- Deleted legacy flat file `src/models.py`.
- Deleted deprecated `src/models_new/` directory and configuration scripts.
- Deleted legacy `src/config.py` module-globals configuration loader.
- Deleted legacy file I/O utility `src/npy/core/settings_manager.py`.

## [2.1.10] - 2026-08-28

### Added
- Brand-new "SUPPORT" card section inside the Settings window.
- Horizontal alignment for Support Email and its input Entry in the Support section.
- Auto-synchronization of the active language selection display in Settings combobox by registering the `refresh_text` callback on `TranslationManager` initialization.
- Token-optimization filters inside `src/dsclinic.py` to automatically strip out newlines and double spaces from `config.AI_INITIAL_TASK_DESCRIPTION` before transmitting it to Gemini. This keeps local assets completely readable as multiline texts while minimizing model API token usage.

### Changed
- Reworked "GENERAL" section inside the Settings window to hold only Language dropdown selection and App Version.
- Aligned "Languages:" label and dropdown horizontally on a single line.
- Centered the main report panel card titles responsively by adding `anchor="center"` on the `ttk.Label` within the `_card` helper. This centers PATIENT DATA, INPUT FINDINGS, RECOMMENDED THERAPY AND ADVICES, CRITICAL FINDINGS, and THERAPY section headers.
- Relocated "Send Logs" and "Show Logs Folder" buttons to the new "Support" card section under Support Email.

### Fixed
- Resolved a bug where multiple saves of the Settings window wrapped the initial task description list into recursive tuple strings (parentheses, nested quotes, and backslashes) inside `config.json`. Clean list-joining handles this in the ViewModel constructor and configuration synchronization loops.
