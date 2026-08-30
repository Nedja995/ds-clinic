# TODO — DSClinic Roadmap

> [!NOTE]
> **Task Management Rule (GASSI Standard):** This document is maintained in **strict descending version order**. The current active focus and upcoming planned versions must always be placed at the top, while completed releases move down into the historical archive at the bottom. Always update this list and session handoffs on every single code change.

---

## v2.5.0 — Chat Session View & Pluggable Multi-Provider Pipeline 🚀 Active

Our current active engineering milestone. Establishes the interactive chat experience and a completely decoupled, flexible multi-provider AI backend supporting Gemini, Claude, Groq, Together, HuggingFace, and Local Ollama, along with testing coverage.

### Tasks

- [ ] **Implement full Chat Session View (`chat_session_view.py` rewrite, `styles.py` additions, and `main_container.py` wiring):**
  - [ ] Complete the Tkinter widget layout inside `src/dsclinic_gui/chat_session_view.py` using standard `ttk` styled components.
  - [ ] Support non-blocking, asynchronous text streaming from background worker threads using the `queue.Queue` and main-thread polling (`root.after`).
  - [ ] Style the user messages and AI response bubbles/boxes beautifully using the centralized definitions in `src/dsclinic_gui/styles.py`.
  - [ ] Wire the `ChatSessionView` and `ChatSessionViewModel` together inside `src/dsclinic_gui/main_container.py` to allow live-streaming interactive dialogues.
  - [ ] Prevent user input or show a loading indicator in the input area when an AI request is in-flight.
  - [ ] Handle auto-scrolling of the chat transcript as new text chunks are streamed into the view.
- [ ] **Build Unified `LLMProvider` Abstraction & Hybrid Pipeline:**
  - [ ] Design a generic, decoupled `LLMProvider` interface to prevent vendor lock-in.
  - [ ] Integrate Google Gemini API (`google-genai`) and Anthropic Claude API (`anthropic`) under this unified interface.
  - [ ] Add support for hosted open-weights providers (Groq API, Together AI, HuggingFace API) to allow ultra-fast open-weights inference.
  - [ ] Implement local Ollama support with 4-bit and 8-bit quantization for absolute on-premises data sovereignty.
- [ ] **Establish PII Anonymization Layer & Local Preprocessors:**
  - [ ] Build a robust local PII scrubbing mechanism (using RegEx and Presidio) to strip patient names and JMBG before data hits the cloud.
  - [ ] Incorporate local preprocessor stubs (MONAI for MRI slice selection; YOLOv8/Vision Transformer hooks for microscopy blood smears).
- [ ] **Rigorous Unit Testing (`pytest`):**
  - [ ] Install `pytest` and build robust automated test suites verifying medical data parsing, PII anonymization, and extraction fallback logic.

---

## v2.4.0 — Unified Configuration, MVVM Schema & High-Privacy Alignment ✅ Completed

A major structural consolidation migrating all models, settings, and dynamic preference files into a unified Pydantic v2 package under `src/models/`, completely eliminating legacy file clutter.

### Completed

- [x] **Consolidate Models into `src/models/` Package:**
  - [x] Created unified package folder.
  - [x] Migrated and split patient schemas into `src/models/patient.py` and diagnostic structures into `src/models/diagnostics.py`.
  - [x] Deleted legacy flat `src/models.py` and `src/models_new/` folders completely.
- [x] **Implement Future-Proof Unified `src/models/settings.py`:**
  - [x] Built the Pydantic-Settings `AppSettings` class to serve as the single, clean source of truth for both static configurations and user customizations.
  - [x] Merged layered loading (`load_unified`) from default baselines and clinician overrides under `.config/medai_vitec/settings.json`.
  - [x] Supported atomic `save_unified` writes back to local folders.
  - [x] Deleted legacy `src/config.py` and `src/npy/core/settings_manager.py` completely.
- [x] **Codebase-Wide Import Refactoring:**
  - [x] Safely refacted all system files to import config settings cleanly via `from models.settings import app_settings`.
- [x] **Settings UI Migration:**
  - [x] Updated `SettingsViewModel` and `SettingsWindow` to bind directly to `app_settings`.
- [x] **Refactor Configuration Loader (`src/config.py`):**
  - [x] Implemented a two-tiered loader that reads `config.json` as a read-only baseline and layered `settings.json` on top.

---

## v2.1.10 — UI & Layout Refinement ✅ Completed

Recent UX and layout polishing in the main panel and settings panel.

### Completed

- [x] Centered section headers in main panel: Set `anchor="center"` on card titles inside the `_card` factory in `src/dsclinic_gui/report_view.py` so they dynamically and responsively center themselves.
- [x] Settings window layout restructuring: Reworked `_build_general_section` and created `_build_support_section` in `src/dsclinic_gui/settings/settings_view.py` to separate General and Support.
- [x] Resolved nested-tuple serialization bug on multiple settings saves in `src/dsclinic_gui/settings/settings_view_model.py`.
- [x] Token-optimized prompt transmission: Added automatic newline/whitespace cleaning inside `src/dsclinic.py` before passing templates to the Gemini API.
