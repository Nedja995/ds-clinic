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
