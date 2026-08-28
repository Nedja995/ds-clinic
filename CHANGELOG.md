# Changelog

All notable changes to DSClinic will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

See [TODO.md](TODO.md) for planned sub-versions.

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
