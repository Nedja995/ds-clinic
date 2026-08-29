# TODO — DSClinic Roadmap

---

## v2.1.10 — UI & Layout Refinement ✅ Complete

Recent UX and layout polishing in the main panel and settings panel.

### Completed

- [x] Centered section headers in main panel: Set `anchor="center"` on card titles inside the `_card` factory in `src/dsclinic_gui/report_view.py` so they dynamically and responsively center themselves across window and split pane resizes.
- [x] Settings window layout restructuring: Reworked `_build_general_section` and created `_build_support_section` in `src/dsclinic_gui/settings/settings_view.py` to:
  - Separate General application parameters from Support features.
  - Align Language dropdown and its label horizontally on a single line in the General section.
  - Create a dedicated "SUPPORT" card section.
  - Align Support Email label and its input entry horizontally on a single line, with the validation error label rendering cleanly underneath.
  - Move the "Send Logs" and "Show Logs Folder" buttons neatly onto their own row inside the Support section.
  - Auto-synchronize the active language dropdown selection on load by registering `refresh_text` on the translator inside `SettingsWindow.__init__`.

- [x] Resolved nested-tuple serialization bug on multiple settings saves: Added list-to-string checks and joins inside `__init__` and `update_from_config()` in `src/dsclinic_gui/settings/settings_view_model.py` so multi-line text input fields load as clean, plain strings without parentheses and quote corruptions.
- [x] Token-optimized prompt transmission: Added automatic newline/whitespace cleaning inside `src/dsclinic.py` before passing `config.AI_INITIAL_TASK_DESCRIPTION` to the Gemini API. This keeps local files and UI highly readable (as multiline strings), while transmitting them as minimized, token-efficient single-line strings.

### Remaining
- [ ] Implement full Chat Session View (`chat_session_view.py` rewrite, `styles.py` additions, and `main_container.py` wiring).
- [ ] Support hot-swapping/re-applying application language instantly upon settings save without requiring an application restart.
- [ ] Migrate the codebase to a fully standardized "Good Practice" workspace structure step-by-step.

---

## v2.2.0 — Decoupled Configuration & Preferences Splitting 🚀 Planned

A complete architectural separation of concerns between static, read-only system configurations and writable, upgrade-resilient user preferences.

### Tasks

- [ ] **Define Schema Models (Pydantic v2):**
  - Establish a clear `AppConfig` Pydantic model for static system settings loaded from `config.json` (supported languages, default model lists, baseline system prompts).
  - Establish a clear `UserPreferences` Pydantic model for persistent, writable clinician customizations loaded from `settings.json` (active language_code, chosen model, doctor/clinic metadata, subscription/license details, and custom prompt templates).
- [ ] **Refactor Configuration Loader (`src/config.py`):**
  - Implement a two-tiered loader that reads `config.json` as a read-only baseline.
  - Load `settings.json` for customizable values, layered on top of the default baseline.
  - Automatically initialize a clean `settings.json` with user overrides defaults if the file is absent or malformed.
- [ ] **Rework Settings View & ViewModel (`src/dsclinic_gui/settings/`):**
  - Modify `SettingsViewModel` and `SettingsWindow` to only bind to and edit properties from `UserPreferences`.
  - Ensure that saving settings writes *exclusively* to `settings.json`, leaving `config.json` completely untouched.
- [ ] **Support Custom Prompt Templates in Preferences:**
  - Update `UserPreferences` schema to allow clinicians to add, edit, or override baseline prompt templates.
  - Retain automatic on-the-fly whitespace and newline normalization when these customized prompts are saved or transmitted to Gemini/Claude APIs to preserve token-efficiency.
- [ ] **Verify Packaging Isolation:**
  - Update PyInstaller `.spec` build configuration files to bundle `config.json` as a read-only asset, while keeping `settings.json` isolated as runtime user-data.
- [ ] **Verification & Validation:**
  - Add robust unit tests for configuration parsing, fallback logic, validation error handling of malformed `settings.json`, and proper overlaying of custom prompts.
