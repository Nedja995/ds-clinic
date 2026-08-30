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
* **The "Clean Update" Principle:** When updating the software, the developer only distributes the new executable and the default `config.json` (allowing prompt upgrades or supported model expansions). The user's custom preferences inside `settings.json` remain completely untouched, ensuring zero clinical data or configuration loss.

---

## AD-09: Portable Application Layout & Local Configuration Directory
* **Decision:** Keep all application resources, static configuration (`config.json`), user preferences (`settings.json`), database files, and session histories **fully local and adjacent to the application entry point (the executable's directory)**. They must be structured inside a dedicated subfolder (e.g., `.config/` or `app_data/` adjacent to the `.exe` file) instead of utilizing global, hidden OS user data directories (like `%LOCALAPPDATA%` on Windows or `~/Library/Application Support` on macOS).
* **Rationale:**
  1. **Default Portability:** Enforcing a local layout enables a "portable mode" by default. Users can copy the entire application directory to a USB flash drive or another partition, and run it with all settings, database records, and session history intact.
  2. **Transparency and Ease of Backup:** Clinical users can easily locate, backup, clone, or migrate their files, configurations, and logs. They do not need to navigate hidden system paths.
  3. **Multi-Instance and Version Coexistence:** Clinicians can run multiple distinct instances of the application (e.g., with different prompt configurations or separate patient databases) side-by-side on the same machine without file collisions or registry contamination.
  4. **Extensibility and Upgradability:** Placing configurations in a structured subfolder adjacent to the executable simplifies adding future features (e.g., prompt plugins, custom templates, multiple patient database files, or different preferences versions) under a single easily-managed folder hierarchy.

---

## AD-10: Unified Hybrid Configuration Model (AppSettings)
* **Decision:** Replace the scattered configuration variables and duplicate managers (`config.py`, `models_new/config.py`, `settings_manager.py`) with a single, unified Pydantic-based `AppSettings` model inside `src/models/settings.py` that utilizes a **Hybrid Pattern** (serving as both data validation schema and file-system I/O loader/saver).
* **Rationale:**
  1. **Zero File Clutter:** Eliminating auxiliary manager files (like `settings_manager.py` and module-globals `config.py`) means that if a configuration field is added, modified, or deprecated, it only needs to be updated in a single file: `src/models/settings.py`.
  2. **Cohesive Loading Pipeline:** The model class itself exposes a cohesive loader: `load_unified(profile_id="default", preset_name=None)` which handles layering and merging (Static config.json Defaults → Predefined Preset Presets → Active Clinician settings_profile.json Override) in a highly readable, deterministic order.
  3. **Atomic Multi-Profile Persistence:** The model instance exposes a `save_unified(profile_id="default")` method that dynamically filters writable fields from static defaults and executes an atomic .tmp file swap write-back to protect against database/preference corruption.
  4. **Multi-Doctor and Session Readiness:** The load/save signature natively supports session isolation and profile switching out of the box, allowing clinic workspaces to seamlessly hot-swap doctor credentials or prompt configurations without global variable re-assignment side-effects.

---

## AD-11: OS Keyring for API Credentials & `pyproject.toml` as Version Source of Truth
* **Decision:** All API keys (`GOOGLE_API_KEY`, `ANTHROPIC_API_KEY`) and sensitive project identifiers (`GOOGLE_PROJECT_ID`) are stored exclusively in the OS-native credential store via the `keyring` library. They are never written to any file on disk (`settings.ini`, `settings.json`, `config.json`, or any other). `app_name` and `app_version` are sourced exclusively from `pyproject.toml`, read at runtime via `importlib.metadata.metadata("dsclinic")`.
* **Rationale:**
  1. **Security:** Plain-text API keys committed to a public git repository are immediately compromised. The OS keyring (Windows Credential Manager, macOS Keychain, libsecret on Linux) is the correct, platform-native secret store — it is encrypted, access-controlled, and never appears in version history.
  2. **Single Source of Truth for Version:** Before this decision, `app_name` and `app_version` were duplicated across `settings.ini` and `pyproject.toml`. Any release required updating both files, risking drift. `pyproject.toml` is already the authoritative packaging manifest; `importlib.metadata` reads it at runtime with zero duplication.
  3. **`settings.ini` Elimination:** With API keys in keyring and version in `pyproject.toml`, `settings.ini` has no remaining purpose and is deleted entirely (v2.6.7), removing the risk of accidentally committing secrets.
* **Implementation (`src/models/keyring_manager.py`):**
  * `_KEYRING_SERVICE = "dsclinic"` — service name for all keyring entries.
  * `get_credential(name)` / `set_credential(name, value)` / `delete_credential(name)` — the only three functions that touch the keyring. All other modules call these; nothing calls `keyring` directly.
  * `_CREDENTIAL_KEYS` dict maps logical names (`"gemini"`, `"anthropic"`, `"google_project_id"`) to keyring usernames (`"gemini_api_key"`, etc.).
* **`AppSettings` impact:** `google_api_key` and `anthropic_api_key` fields removed in v2.6.3. `load_unified()` no longer reads `settings.ini`. `save_unified()` never writes secrets.
* **Frozen build fallback:** When running as a PyInstaller executable, `importlib.metadata` raises `PackageNotFoundError`. `load_unified()` catches this silently and falls back to `AppSettings` field defaults (`app_name = "DSClinic"`, `app_version = "2.6.x"`).

---

## AD-12: Split-Horizon Hybrid Inference Architecture
* **Decision:** Implement a layered model routing framework that dynamically segments tasks between local Open-Weights models (via Ollama) and Cloud Reasoning Engines (Gemini Pro / Claude Sonnet).
* **Rationale:** Maximizes enterprise cost-efficiency and performance while respecting severe data boundaries. Local models handle tasks where low-cost ingestion or high privacy is prioritized. Heavy cloud models are treated as deterministic data synthesis engines, receiving only pre-sanitized payloads.

---

## AD-13: Edge Hardware Optimization via Quantization (16GB VRAM Constraint)
* **Decision:** Optimize all local deployment topologies (LXC/Proxmox) to run exclusively on a 16GB VRAM budget using 4-bit and 8-bit quantized weights via `vLLM` or `Ollama` engines.
* **Architecture:** 
  1. Text Extraction/OCR: Managed via `Llama 3.2 Vision (11B)` quantized to 4-bit (~8GB-12GB VRAM allocation).
  2. Medical Vision: Managed via `MedGemma (7B)` or specialized vision classifiers.
  3. Orchestration: The Python backend implements sequential processing ("Load on Demand") to ensure multiple models never contend for memory simultaneously, avoiding VRAM thrashing or CUDA out-of-memory errors.

---

## AD-14: Multi-Modal Preprocessing vs. Raw General Vision Ingestion
* **Decision:** Prohibit passing raw, un-optimized multi-dimensional clinical files (like 3D DICOM MRI volumes) or raw cellular microscopy images directly into generic Vision-Language Models (VLMs).
* **Execution Strategy:**
  1. For MRIs: Use the **MONAI** framework locally on CPU/GPU to run algorithmic spatial slicing and isolate suspicious regions of interest (e.g., tumor/lesion boundaries) before passing flat 2D targets to an LLM.
  2. For Lab Microscopy/Blood Smears: Bypass LLM vision layers completely to eliminate hallucinated cellular metrics. Utilize specialized object detection nodes (e.g., **YOLOv8** or fine-tuned **Vision Transformers**) trained on medical datasets to extract strict, immutable numerical parameters into a JSON schema.

---

## AD-15: Zero-Trust Local Privacy & PII Scrubbing Framework
* **Decision:** Implement a multi-layered local data-masking pipeline that ensures no Personally Identifiable Information (PII) ever leaves the clinic machine.
* **Execution Strategy:** 
  1. Image & Document Scanning: The local `redaction_worker.py` utilizes a native pipeline to extract raw text layout coordinates before any network calls are dispatched.
  2. Automated Anonymization: A local Microsoft Presidio Engine + `spaCy` text pipeline scans the layout strings to capture patient names, dates of birth, precise medical IDs, phone numbers, and the 13-digit Serbian National Identification Number (JMBG).
  3. Geometric Blurring/Redaction: The application draws solid opaque black rectangles over the detected coordinate regions on the source image, creating a permanent, sanitized copy of the asset for secondary processing.

---

## AD-16: Defensive Desktop Error Isolation & UI Thread Resilience
* **Decision:** Enforce a strict "no-crash, no-freeze" UI architecture by isolating all third-party integrations, OS keyrings, local disk I/O, and remote model completions into dedicated worker threads.
* **Execution Strategy:**
  1. Asynchronous Workflows: Every processing pipeline must derive from a non-blocking background thread (`threading.Thread`) and utilize a thread-safe synchronized `queue.Queue` to broadcast life-cycle mutations back to the UI.
  2. Failure Packaging: Bare `except:` statements are strictly prohibited. All potential points of failure (e.g., rate limits, bad server returns, missing local dependencies, missing hardware allocations) must be wrapped in granular `try/except` blocks.
  3. Graceful UI Failovers: When an exception triggers, the background worker must catch it, serialize a safe `{"status": "failed", "error": "User-friendly description + logs"}` payload into the communication queue, and allow the UI main loop to cleanly terminate processing states without locking up or crashing the execution environment.

---

## AD-17: Continuous Quality Verification via High-Coverage Unit Testing
* **Decision:** Establish an automated testing pipeline using `pytest` to guarantee system regressions are caught instantly during architectural refactoring phases.
* **Execution Strategy:**
  1. Deterministic Parser Validation: Every script parsing medical JSON outputs, clinic layouts, or raw lab report strings must be accompanied by a dedicated test case verifying mock inputs yield precise target data types.
  2. Service Decoupling via Mocking: Tests interacting with external resources (such as the Gemini API or local Ollama engines) must use `unittest.mock` to simulate real-world payloads, protecting local execution pipelines from environmental network drops during test execution.
  3. Target Matrix: The test suite must actively evaluate the processing boundaries of the PII scrubbing pipeline, the abstract routing factory logic, and database index operations under standard and edge-case criteria.
   