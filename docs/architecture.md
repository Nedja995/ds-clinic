# Architecture Decisions Record — DSClinic

This document tracks the key architectural decisions made for **DSClinic** and the rationale behind each. Because this application is evolving toward an enterprise-ready product, we prioritize long-term maintainability and structural cleanliness over legacy backward-compatibility.

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

## AD-04: Multi-Client White-Labeling (Branding) & SaaS Flexibility
* **Decision:** Decouple all brand-specific configurations, report logos, clinic headers, and document styles from core app code.
* **Rationale:** To support multiple monetization and distribution business models:
  1. **White-Labeled Client Builds:** Direct customized builds for specific clinics with assets compiled into the directory.
  2. **Standardized SaaS / Subscription App:** A single distributed application where users pay a subscription and dynamically configure their own clinic headers, report appearances, and doctor names.
* Storing branding properties, customized layout definitions, and license keys in the writeable local `settings.json` supports both strategies seamlessly.

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

---

## AD-08: Complete Decoupling of Static App Config and Dynamic User Preferences
* **Decision:** Maintain a strict, decoupled boundary between read-only application configurations and writeable user preferences. Legacy backward-compatibility is **not required**.
* **Configuration Specifications:**
  * **App Config (`config.json`):** Read-only developer/distributor configuration. Contains static definitions that define core application rules:
    * Supported languages map: `{"English": "en", "Srpski": "sr", "Español": "es"}`.
    * Default/fallback application language (e.g. `"sr"` or `"en"`) set on development.
    * Lists of supported AI models.
    * Base default Task prompt templates.
  * **User Preferences (`settings.json`):** Writeable configuration stored in user AppData. Contains settings that are specific to the client instance:
    * Currently active `language_code` (which must match a code defined in the App Config's supported languages).
    * Custom user-defined Task prompts (clinicians can create, modify, or extend default prompts, saved dynamically to `settings.json` so updates to `config.json` don't overwrite them).
    * User variables: active model selection, clinic names, custom report headers, doctor credentials, and billing/license parameters.
* **The "Clean Update" Principle:** When updating the software, the developer only distributes the new executable and the default `config.json` (allowing prompt upgrades or supported model expansions). The user's custom preferences inside `settings.json` remain completely untouched, ensuring zero clinical data or configuration loss!
