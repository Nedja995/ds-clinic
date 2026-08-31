# Architecture Decisions Record — DSClinic

This document tracks the key architectural decisions made for **DSClinic** and the rationale behind each. Because this application is evolving toward an enterprise-ready product, we prioritize long-term maintainability and structural cleanliness over legacy backward-compatibility.

---

## AD-01: MVVM (Model-View-ViewModel) Architecture
* **Decision:** Rebuild the GUI in a strict Model-View-ViewModel (MVVM) pattern, migrating away from the legacy MVC patterns.
* **Rationale:** ViewModels own the application state (exposed via `tk.StringVar`/`IntVar`/`BooleanVar` properties for reactive binding) and background task lifecycles. Views (`src/dsclinic_gui/*_view.py`) handle layout, themed styling (`ttk`), and event bindings.
* **Strict Separation:**
  * ViewModels must **never** import Tkinter widgets or directly call UI dialogues/message boxes (e.g., `filedialog` or `messagebox`). ViewModels must use callback delegates passed from the View or two-step prepare/execute sequences to keep the business logic 100% independent of the UI layer.
  * *Current State:* Some parts of the codebase may still have lingering MVC/MVVM coupling. Auditing and refactoring these areas is high priority (v2.5.1).

---

## AD-02: Threading Discipline & Queue-Based UI Sync
* **Decision:** Direct update of Tkinter widgets from background worker threads is strictly prohibited. Communication must occur via `queue.Queue` with main-thread polling.
* **Rationale:** Tkinter is not thread-safe. Background threads (AI completion, OCR, PDF generation) write structured progress events (`running`, `progress`, `finished`, `failed`) into a thread-safe Queue. The View or ViewModel on the main thread polls this queue via `root.after()` loops.
* **No Direct Signals:** Worker threads must never call `event_generate()` or interact with the main Tkinter thread directly, avoiding deadlocks or random crashes on Windows client machines.

---

## AD-03: Multi-Provider AI Fallback Strategy
* **Decision:** Implement native SDK clients for both **Google Gemini (`api_gemini`)** and **Anthropic Claude (`api_claude`)**, avoiding abstract intermediate wrappers.
* **Rationale:** Gives us absolute control over model-specific parameters (like temperature, top-p, thinking level, and system prompts) and prompt formats.
* **Superseded by AD-19:** In v2.5.3, direct clients are wrapped behind the `LLMProvider` abstraction. The native SDK clients remain but are accessed only through concrete `Provider` classes.

---

## AD-04: Multi-Client White-Labeling (Branding) & SaaS Flexibility
* **Decision:** Decouple all brand-specific configurations, report logos, clinic headers, and document styles from core app code.
* **Rationale:** To support multiple monetization and distribution business models:
  1. **White-Labeled Client Builds:** Direct customized builds for specific clinics with assets compiled into the directory.
  2. **Standardized SaaS / Subscription App:** A single distributed application where users pay a subscription and dynamically configure their own clinic headers, report appearances, and doctor names.
* Storing branding properties, customized layout definitions, and license keys in the writeable local `settings.json` supports both strategies seamlessly.
* **Extended by AD-20:** In v2.5.6, this is implemented via a dedicated `BrandConfig` model loaded from `brand.json`.

---

## AD-05: Local OCR & Privacy Anonymization Pipeline
* **Decision:** Perform local, offline PII (Personally Identifiable Information) scrubbing on images and PDFs before sending any data to external cloud AI servers.
* **Rationale:** Patient data privacy is paramount.
* **Implementation:** The `redaction_worker.py` pipeline runs a sequential `EasyOCRAdapter` (supporting both Latin and Cyrillic Serbian scripts) to extract layout text. It uses a local `Presidio AnalyzerEngine` and `spaCy` to locate names, precise addresses, and the 13-digit Serbian National Identification Number (JMBG). It draws solid black boxes over these regions. For PDFs, pages are dynamically converted to high-resolution images, scrubbed, and processed.
* **Status:** Implemented in commit `5d5b2f4`. Known issue: over-anonymization of clinical numeric values. Improvement planned in v2.5.9.

---

## AD-06: Local Document JSON Database (`src/db/`)
* **Decision:** Use a local, file-based JSON document collection engine rather than a centralized cloud database.
* **Rationale:** Storing clinical data in a generic `JsonCollection[T]` under the local `app_data/` directory guarantees:
  1. Complete offline capability for clinic workers.
  2. Absolute data sovereignty (patient records never leave the local machine except for anonymized AI analysis).
  3. Zero cloud hosting or database management costs.
  * Fast listings are maintained via a flat index file (`_index.json`) that can be rebuilt from disk if corrupted.
* **Current state:** `AppDatabase` with `sessions`, `reports`, `ai_profiles` collections is fully implemented in `src/db/`. Not yet wired to any ViewModel. Wiring planned in v2.5.2.

---

## AD-07: Monolithic Desktop Distribution (PyInstaller)
* **Decision:** Distribute the application as a standalone, zero-dependency Windows executable (`.exe`) compiled via PyInstaller.
* **Rationale:** Medical and holistic clinic computers are often locked-down or lack Python environments. Distributing a single, self-extracting executable with embedded resources (Serbian translations, Arial Unicode TTF fonts, and custom window icons) ensures a simple, double-click install experience.

---

## AD-08: Complete Decoupling of Static App Config and Dynamic User Preferences
* **Decision:** Maintain a strict, decoupled boundary between read-only application configurations and writeable user preferences. Legacy backward-compatibility is **not required**.
* **Configuration Specifications:**
  * **App Config (`config.json`):** Read-only developer/distributor configuration. Contains static definitions that define core application rules.
  * **User Preferences (`settings.json`):** Writeable configuration stored locally. Contains settings specific to the client instance.
* **The "Clean Update" Principle:** When updating the software, the developer only distributes the new executable and the default `config.json`. The user's custom preferences inside `settings.json` remain completely untouched.

---

## AD-09: Portable Application Layout & Local Configuration Directory
* **Decision:** Keep all application resources, static configuration, user preferences, database files, and session histories fully local and adjacent to the application entry point.
* **Rationale:** Default portability, transparency, multi-instance coexistence, extensibility.

---

## AD-10: Unified Hybrid Configuration Model (AppSettings)
* **Decision:** Replace scattered configuration variables with a single, unified Pydantic-based `AppSettings` model in `src/models/settings.py`.
* **Rationale:** Zero file clutter, cohesive loading pipeline, atomic multi-profile persistence, multi-doctor and session readiness.

---

## AD-11: OS Keyring for API Credentials & `pyproject.toml` as Version Source of Truth
* **Decision:** All API keys and sensitive project identifiers stored exclusively in OS-native credential store via `keyring`. `app_name`/`app_version` sourced exclusively from `pyproject.toml` via `importlib.metadata`.
* **Implementation:** `src/models/keyring_manager.py` — `get_credential()` / `set_credential()` / `delete_credential()`. `settings.ini` permanently deleted in v2.6.7.

---

## AD-12: Split-Horizon Hybrid Inference Architecture
* **Decision:** Layered model routing that segments tasks between local open-weights models (Ollama) and cloud reasoning engines (Gemini / Claude).
* **Rationale:** Maximizes enterprise cost-efficiency and performance while respecting strict GDPR data boundaries. Local models handle privacy-sensitive extraction; cloud models receive only pre-sanitized structured payloads.

---

## AD-13: Edge Hardware Optimization via Quantization (16GB VRAM Constraint)
* **Decision:** All local deployments optimized for a 16GB VRAM budget using 4-bit and 8-bit quantized weights via Ollama.
* **Architecture:** Sequential "Load on Demand" — only one model loaded at a time to prevent VRAM thrashing.

---

## AD-14: Multi-Modal Preprocessing vs. Raw General Vision Ingestion
* **Decision:** Prohibit passing raw unoptimized multi-dimensional clinical files directly into general Vision-Language Models.
* **Execution:** MONAI for MRI DICOM slicing; YOLOv8/Vision Transformers for cellular microscopy metrics.

---

## AD-15: Zero-Trust Local Privacy & PII Scrubbing Framework
* **Decision:** Multi-layered local data-masking pipeline — no PII ever leaves the clinic machine unredacted.
* **Execution:** `redaction_worker.py` → Presidio + spaCy NER → geometric black-box redaction on source images.

---

## AD-16: Defensive Desktop Error Isolation & UI Thread Resilience
* **Decision:** Strict "no-crash, no-freeze" UI architecture — all third-party integrations isolated in dedicated worker threads.
* **Rules:** No bare `except:`. All failures serialized as structured queue payloads. UI main loop always terminates cleanly.

---

## AD-17: Continuous Quality Verification via High-Coverage Unit Testing
* **Decision:** Automated `pytest` pipeline covering parsers, PII scrubber, provider routing, and database operations.
* **Target matrix:** PII boundary testing, provider factory mocking, `JsonCollection` CRUD + index operations.

---

## AD-18: `PatientRecord` as First-Class Entity (v2.5.2)
* **Decision:** Introduce a `PatientRecord` Pydantic model as a first-class persistent entity, separate from `MedicalReport`. A patient is a recurring entity across multiple visits/sessions; a report is the output of a single session.
* **Rationale:** The current data model stores patient identity only as a plain name string inside `MedicalReport`. An enterprise B2B clinic product must track recurring patients across multiple analysis sessions, correlate historical reports per patient, and support patient-level history browsing. Treating the patient as a first-class entity enables all of this without schema hacks.
* **Data model:**
  * `PatientRecord`: `patient_id (uuid)`, `full_name`, `date_of_birth`, `created_at`, `session_ids: list[str]`.
  * `AppDatabase.patients: JsonCollection[PatientRecord]` at `app_data/patients/`.
  * `ChatSessionModel.session_id` is the join key between `PatientRecord.session_ids` and the sessions collection.
* **DB layer status:** `AppDatabase`, `JsonCollection[T]`, `ChatSessionModel`, `MedicalReport` are all fully implemented in `src/db/` and `src/models/`. Not yet wired to any ViewModel. Wiring + `PatientRecord` addition both happen in v2.5.2.

---

## AD-19: `src/providers/` LLMProvider Abstraction Package (v2.5.3)
* **Decision:** Introduce a dedicated `src/providers/` package containing an abstract `LLMProvider` base class and concrete provider implementations for all six supported inference backends. `DSClinic` and all ViewModels interact exclusively with the `LLMProvider` interface — never with SDK-specific client classes directly.
* **Rationale:**
  1. **Vendor lock-in elimination:** Currently `DSClinic.__init__` is hard-coupled to `MedicalAnalyzerClient` (Gemini) and `ClaudeAnalyzerClient`. Adding a seventh provider requires modifying core business logic. The abstraction removes this entirely.
  2. **Portfolio showpiece:** The ability to hot-swap or failover between 6 providers at runtime is the core architectural differentiator that answers *"How does your system handle vendor outages?"* in EU HealthTech interviews.
  3. **Split-Horizon enablement:** The abstraction is what makes the Split-Horizon pipeline (AD-12) implementable — the Layer 1 extraction task and Layer 2 reasoning task can each be assigned a different `LLMProvider` instance.
* **Package structure:**
  ```
  src/providers/
      __init__.py           → exports LLMProvider, ProviderFactory, ProviderType
      base.py               → LLMProvider (ABC), ProviderRequest, ProviderResponse, ProviderType (StrEnum)
      factory.py            → ProviderFactory.create(), ProviderFactory.available_providers()
      gemini_provider.py    → GeminiProvider (wraps api_gemini/client.py)
      claude_provider.py    → ClaudeProvider (wraps api_claude/client.py)
      groq_provider.py      → GroqProvider (v2.5.4)
      together_provider.py  → TogetherProvider (v2.5.4)
      huggingface_provider.py → HuggingFaceProvider (v2.5.4)
      ollama_provider.py    → OllamaProvider, load-on-demand, 4-bit quant (v2.5.5)
  ```
* **Existing `api_gemini/` and `api_claude/` packages:** Remain as raw SDK wrapper layers. Concrete provider classes in `src/providers/` delegate to them. This preserves the existing SDK tuning investment while adding the clean abstraction on top.
* **`is_available()` contract:** Every provider must implement `is_available() → bool` — returns `True` only if the required credential is in the keyring AND the client initialized without error. `ProviderFactory.available_providers()` calls this to build the runtime provider list shown in the UI selector.

---

## AD-20: `BrandConfig` + Dual Delivery Mode Architecture (v2.5.6)
* **Decision:** Introduce a `BrandConfig` Pydantic model loaded from a `brand.json` file adjacent to the executable. All GUI strings (window title, toolbar header), PDF output (logo, clinic name, header/footer text, color scheme), and subscription enforcement gates are driven exclusively by `BrandConfig` at runtime.
* **Rationale:**
  1. **B2B white-labeling:** A clinic receives a branded `.exe` with a pre-configured `brand.json` containing their logo path, name, and subscription tier. Zero code changes required per client.
  2. **SaaS subscription model:** The same binary serves multiple clinics. Each configures their brand profile via Settings → Clinic Profile, saved to a local `brand.json`. Subscription tier gates features (PDF watermark for `trial`, multi-user for `enterprise`).
  3. **Clean separation from app logic:** `AppSettings` governs AI configuration and user preferences. `BrandConfig` governs identity and commercial tier. Never mixed.
* **Two delivery modes:**
  * **White-labeled B2B build:** Distributor pre-populates `brand.json` + logo asset alongside the `.exe`. Client sees only their clinic branding; DSClinic name is invisible.
  * **Subscription SaaS:** Single `.exe` distributed publicly. User fills in clinic profile via Settings UI. `brand.json` written locally. Tier enforced by license key check (stub in v2.5.6, full validation in a future milestone).
* **`subscription_tier` values:** `"trial"` (PDF watermark, session limit), `"standard"` (full reports), `"enterprise"` (multi-user, custom models, advanced analytics).
