# DSClinic — New Session Handoff Document

Read this document before starting any work. It captures everything needed to immediately continue development without reading through extensive previous chat logs, saving thousands of context tokens.

---

## What DSClinic Is

A Windows-first, cross-platform Python desktop application (`tkinter/ttk`) used by holistic and medical clinics to analyze patient diagnostic records (such as laboratory reports, PDFs, and MetaHunter holistic exports). 

The app uses Gemini or Claude models to extract structured parameters (Findings and Therapies), displays them in a rich editable form, allows interactive chat with the AI model for refinement, and compiles the final report into a styled PDF.

**Current State:** `v2.3.0` Unified Configuration and Models Package completed successfully!
* Deprecated all legacy config modules (`config.py`, `settings_manager.py`, and `models_new/`).
* Consolidated schemas and variables into a single unified `src/models/` package, split into:
  - `patient.py`: patient, therapies, findings, and complete medical reports.
  - `ai.py`: chat history, chat sessions, and model configurations for Gemini and Claude.
  - `diagnostics.py`: task status enums, progress event structures, and the observable list.
  - `settings.py`: The single source of truth for all configurations (`AppSettings`).
* Built a hybrid, self-contained loading pipeline in `AppSettings.load_unified()` that layers defaults from `config.json`, fallback parameters from `settings.ini`, and custom clinician overrides from `settings.json`.
* Atomic writes back to `.config/medai_vitec/settings.json` are fully supported via `AppSettings.save_unified()`.
* Portability-by-default is fully enforced with adjacent subfolders.

**Next Immediate Goal:** Complete the **Chat Session View** (`src/dsclinic_gui/chat_session_view.py` rewrite, styling, and `main_container.py` integration) to allow interactive streaming chats with the AI models.

**Repo:** `D:\__STORAGE\__DEV\__PROJECTS\DSKlinika\ds-clinic_03_04_2026`
**Stack:** Python 3.x, tkinter/ttk, fpdf2, pydantic, google-genai, anthropic, easyocr, spacy, pymupdf (fitz), presidio-analyzer

---

## Key Development Documents

Read these on demand to check policies or designs, not upfront:
* `TODO.md` — To see planned development phases and task check-lists.
* `CHANGELOG.md` — To see what changed in specific version releases.
* `docs/architecture.md` — Architectural Decisions Record (ADRs) detailing MVVM, threading limits, database, and localization boundaries.
* `GEMINI.md` — Team-shared development directives and boilerplate code templates.

---

## Technical Architecture Rules

1. **Strict MVVM:** ViewModels (`*_view_models.py`) must contain **zero** tkinter widget imports and must **never** trigger dialogues or file selectors directly (use callback handlers). Views (`*_view.py`) handle layouts using native `ttk` styled widgets.
2. **Threading Isolation:** Background operations (AI calls, PDF compilation, local OCR) must run on a separate daemon thread. They write progress updates into a `queue.Queue`. The GUI thread polling loop reads this queue via `root.after()`. Worker threads must **never** touch UI widgets or call `event_generate()`.
3. **Decoupled Config & White-Label Design (No Backward-Compatibility):**
   * **Base Defaults (`config.json`):** Static, read-only defaults (supported model definitions, system prompts, initial task template).
   * **Credentials Fallback (`settings.ini`):** Holds app base name, version, and global API keys.
   * **Clinician Overrides (`settings.json`):** Holds writeable runtime overrides (active language code, chosen model, customized templates, doctor details, and keys). 
   * **Local Portable Placement:** Both files are kept in `.config/medai_vitec` adjacent to the executable directory to enforce dynamic "portable mode" out of the box.
   * **Unified `AppSettings` Interface:** Any system file accesses configuration properties purely via `from models import app_settings`. Saving updates is as simple as `app_settings.save_unified()`.
4. **Local Database:** All local clinic records, settings, and histories are stored in generic `JsonCollection[T]` documents under `app_data/` with local JSON indices.
5. **Localization:** Serbian (`sr`) translations are compiled using:
   ```cmd
   pybabel compile -d resources/locale -D app
   ```

---

## Immediate Development Roadmaps & Challenges

* **Chat Session View Integration:** The `ChatSessionViewModel` is implemented, but `chat_session_view.py` needs to be completed, styled via `styles.py`, and wired up to `main_container.py` to allow live-streaming interactive dialogues.
* **Gemini API Congestion & Fallbacks:** Gemini servers frequently return rate limits or become busy during client business hours. We need to implement a resilient retry mechanism with exponential backoff and support automatic failover to Anthropic Claude models.
* **Support Language Hot-Swapping:** Support dynamic hot-swapping and re-applying of active application languages instantly upon settings save without requiring an application restart.
* **Legacy MVVM violations:** Audit existing views and ViewModels to resolve lingering MVC couplings or direct messagebox/dialogue invocations in ViewModel files.
