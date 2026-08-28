# DSClinic — New Session Handoff Document

Read this document before starting any work. It captures everything needed to immediately continue development without reading through extensive previous chat logs, saving thousands of context tokens.

---

## What DSClinic Is

A Windows-first, cross-platform Python desktop application (`tkinter/ttk`) used by holistic and medical clinics to analyze patient diagnostic records (such as laboratory reports, PDFs, and MetaHunter holistic exports). 

The app uses Gemini or Claude models to extract structured parameters (Findings and Therapies), displays them in a rich editable form, allows interactive chat with the AI model for refinement, and compiles the final report into a styled PDF.

**Current State:** `v2.1.10` UI refinement complete. 
* Centered report card section headers responsively.
* Restructured the Settings Window (split General and Support, side-by-side Support Email alignment, and auto-synced languages on load).
* Core Findings and Therapies grids are fully editable and sync with ViewModels.
* Offline Privacy Anonymization pipeline (`redaction_worker.py`) is fully functional.

**Next Immediate Goal:** Complete the **Chat Session View** (`src/dsclinic_gui/chat_session_view.py` rewrite, styling, and `main_container.py` integration) to allow streaming chat with models.

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
3. **White-Label Design:** Decouple all branding, clinic names, contact footers, logos, and custom strings from the core code, routing them through `config.json` and asset paths to support easy clinic re-branding.
4. **Local Database:** All local clinic records, settings, and histories are stored in generic `JsonCollection[T]` documents under `app_data/` with local JSON indices.
5. **Localization:** Serbian (`sr`) translations are compiled using:
   ```cmd
   pybabel compile -d resources/locale -D app
   ```

---

## Immediate Development Roadmaps & Challenges

* **Gemini API Congestion:** Gemini servers frequently return rate limits or become busy during client business hours. We need to implement a resilient retry mechanism with exponential backoff and support automatic fallbacks to Anthropic Claude.
* **Chat Session View Integration:** The `ChatSessionViewModel` is implemented, but `chat_session_view.py` needs to be completed, styled via `styles.py`, and wired up to `main_container.py`.
* **Legacy MVVM violations:** Audit existing views and ViewModels to resolve lingering MVC couplings or direct messagebox/dialogue invocations in ViewModel files.
