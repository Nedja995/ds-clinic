# Architecture Decisions Record — DSClinic

This document tracks the key architectural decisions made for **DSClinic** and the rationale behind each. Because this application has been co-developed across multiple manual and AI sessions, some components may require refactoring in future sprints to fully align with these decisions.

---

## AD-01: MVVM (Model-View-ViewModel) Architecture
* **Decision:** Rebuild the GUI in a strict Model-View-ViewModel (MVVM) pattern, migrating away from the legacy MVC patterns.
* **Rationale:** ViewModels own the application state (exposed via `tk.StringVar`/`IntVar`/`BooleanVar` properties for reactive binding) and background task lifecycles. Views (`src/dsclinic_gui/*_view.py`) handle layout, themed styling (`ttk`), and event bindings.
* **Strict Separation:** 
  * ViewModels must **never** import Tkinter widgets or directly call UI dialogues/message boxes (e.g., `filedialog` or `messagebox`). ViewModels must use callback delegates passed from the View or two-step prepare/execute sequences to keep the business logic 100% independent of the UI layer.
  * *Current State:* Some parts of the codebase may still have lingering MVC/MVVM coupling. Auditing and refactoring these areas is high priority.

---

## AD-02: Threading Discipline & Queue-Based UI Sync
* **Decision:** Direct update of Tkinter widgets from background worker threads is strictly prohibited. Communication must occur via `queue.Queue` with main-thread polling.
* **Rationale:** Tkinter is not thread-safe. Background threads (AI completion, OCR, PDF generation) write structured progress events (`running`, `progress`, `finished`, `failed`) into a thread-safe Queue. The View or ViewModel on the main thread polls this queue via `root.after()` loops.
* **No Direct Signals:** Worker threads must never call `event_generate()` or interact with the main Tkinter thread directly, avoiding deadlocks or random crashes on Windows client machines.

---

## AD-03: Multi-Provider AI Fallback Strategy
* **Decision:** Implement native SDK clients for both **Google Gemini (`api_gemini`)** and **Anthropic Claude (`api_claude`)**, avoiding abstract intermediate wrappers.
* **Rationale:** Gives us absolute control over model-specific parameters (like temperature, top-p, thinking level, and system prompts) and prompt formats.
* **API Congestion/Busy Solutions:** During peak business hours, Gemini's backend frequently encounters high latency, rate limits, or capacity limits. We will design a resilient fallback mechanism:
  1. Auto-retry on rate limits (using exponential backoff).
  2. Automatic failover to Anthropic Claude (or alternative models) if the primary model is busy, ensuring clinic workers experience zero disruptions.

---

## AD-04: Multi-Client White-Labeling (Branding)
* **Decision:** Decouple all brand-specific configurations, report logos, clinic headers, and document styles from core app code.
* **Rationale:** To enable selling DSClinic to different medical/holistic clinics under their own unique brand (white-labeling), the app must load its layout titles, PDF logos, fonts, and contact footers dynamically from `config.json` and local assets. This allows creating custom-branded builds easily via simple asset swaps.

---

## AD-05: Local OCR & Privacy Anonymization Pipeline
* **Decision:** Perform local, offline PII (Personally Identifiable Information) scrubbing on images and PDFs before sending any data to external cloud AI servers.
* **Rationale:** Patient data privacy is paramount.
* **Implementation:** The `redaction_worker.py` pipeline runs a sequential `EasyOCRAdapter` (supporting both Latin and Cyrillic Serbian scripts) to extract layout text. It uses a local `Presidio AnalyzerEngine` and `spaCy` to locate names, precise addresses, and the 13-digit Serbian National Identification Number (JMBG). It draws solid black boxes over these regions. For PDFs, pages are dynamically converted to high-resolution images, scrubbed, and processed.

---

## AD-06: Local Document JSON Database (`src/db/`)
* **Decision:** Use a local, file-based JSON document collection engine rather than a centralized cloud database.
* **Rationale:** Storing clinical data in a generic `JsonCollection[T]` under the local `app_data/` directory guarantees:
  1. Complete offline capability for clinic workers.
  2. Absolute data sovereignty (patient records never leave the local machine except for anonymized AI analysis).
  3. Zero cloud hosting or database management costs.
  * Fast listings are maintained via a flat index file (`_index.json`) that can be rebuilt from disk if corrupted.

---

## AD-07: Monolithic Desktop Distribution (PyInstaller)
* **Decision:** Distribute the application as a standalone, zero-dependency Windows executable (`.exe`) compiled via PyInstaller.
* **Rationale:** Medical and holistic clinic computers are often locked-down or lack Python environments. Distributing a single, self-extracting executable with embedded resources (Serbian translations, Arial Unicode TTF fonts, and custom window icons) ensures a simple, double-click install experience.
