# TODO — DSClinic Roadmap

> [!NOTE]
> **Sorting Rule (GASSI Standard — Strict Descending Version Order):**
> This document is always sorted **newest version number at the top, oldest at the bottom**. When a version is completed it is inserted above all older completed versions — never appended at the bottom. Sub-versions within a completed parent are also listed newest-first (v2.5.4 above v2.5.3 above v2.5.2). Completed versions use `[x]` checkboxes; no separate archive label is needed. This ordering must be enforced on every edit.
>
> **Sub-version Rule:** Every parent milestone (e.g. v2.5.0) is broken into numbered sub-tasks (v2.5.1, v2.5.2, ...). Each sub-version is a self-contained, committable unit of work. Sub-versions are completed in order; the parent is marked done only when all sub-versions are complete.
>
> **TODO Archiving Rule:** Completed versions are never collapsed or summarised. Every completed sub-version and its full task list remains fully expanded with `[x]` checkboxes indefinitely.

---

## v2.15.0 — README Engineering Case Study + Architecture Diagrams 📖 Planned

**Why:** The portfolio presentation layer. EU recruiters hiring 12-year veterans want to see *how you think* — the README is the first thing they read. Can only be written accurately after the full architecture is built.

---

### v2.15.1 — `README.md` Full Rewrite

- [ ] **Problem statement:** What clinical administrative pain does DSClinic solve? Who is the user? What is the business model?
- [ ] **"MVP to Scale" narrative:** Rapid prototype → real user validated → full architectural overhaul. The interview story arc.
- [ ] **Architecture overview:** Text-based Split-Horizon diagram (renders in GitHub).
- [ ] **GDPR compliance section:** PII scrubbing pipeline, local-first processing, keyring credential management.
- [ ] **Provider abstraction section:** `LLMProvider` interface, all 6 providers listed, factory pattern explained.
- [ ] **16GB VRAM optimization section:** Quantization, load-on-demand, sequential model switching.
- [ ] **Multi-brand / white-label section:** `BrandConfig`, dual delivery modes, subscription tiers.
- [ ] **Technical stack table:** Python, Tkinter/ttk, Pydantic v2, MVVM, PyInstaller, Presidio, keyring, Ollama, Groq, Together, HuggingFace.
- [ ] **CV-ready interview pitch quote block** from `docs/looking_for_new_job_gemini_conversation.md`.

---

### v2.15.2 — Architecture Diagrams (`docs/diagrams/`)

- [ ] Split-Horizon Hybrid Inference pipeline diagram: Input → Anonymizer → Layer 1 (local/open-weights) → Layer 2 (cloud reasoning) → Report.
- [ ] MVVM layer diagram: Model / ViewModel / View boundaries with queue communication.
- [ ] `LLMProvider` class diagram: `LLMProvider` ABC + 6 concrete providers + `ProviderFactory`.
- [ ] Patient data flow diagram: Input files → PII scrub → AI analysis → `MedicalReport` → PDF → `AppDatabase`.

---

### v2.15.3 — Final Doc Pass

- [ ] `GEMINI.md` final review: verify all AI assistant directives, coding rules, and architectural guidelines reflect the complete v2.7.0–v2.15.0 implementation. Update any sections that drifted.
- [ ] `docs/architecture.md` final cross-reference pass: verify all AD numbers are sequential, all inter-AD references (`See AD-XX`) resolve correctly, and no AD describes a planned feature that was changed during implementation.
- [ ] `docs/session_handoff.md` final entry: mark project as portfolio-complete with build/run instructions for demo purposes.

---

## v2.14.0 — PII Anonymization Improvements + Debug Panel 🔍 Planned

**Why:** Already working (commit `5d5b2f4`). Improvement driven by v2.13.2 test failures. Debug panel makes over-anonymization visible during development and demo sessions — an interviewer-facing feature.

---

### v2.14.1 — Root Cause Analysis & Presidio Tuning

- [ ] Identify which Presidio entity types cause false positives on clinical values (e.g. `DATE_TIME`, `PHONE_NUMBER` matching lab values).
- [ ] Tune `AnalyzerEngine` entity list: selectively disable or reduce confidence threshold for problematic entity types.
- [ ] Add regex-based allowlist for common lab value patterns: `\d+\.?\d*\s?(mmol/L|mg/dL|g/L|mmHg|U/L|µmol/L)`.
- [ ] Add allowlist for Serbian medical shorthand that triggers false positives.
- [ ] Run v2.13.2 test suite — all tests must pass before proceeding.

---

### v2.14.2 — PII Debug Panel (View)

- [ ] Toggle-able debug panel in the main UI (hidden by default; enabled when `app_settings.app_debug_response` is `True`).
- [ ] Shows side-by-side diff: original text vs anonymized text with highlighted redacted regions.
- [ ] Lists each detected entity: type, confidence score, matched text snippet, action taken (redacted / kept).
- [ ] Export debug report to `logs/pii_debug_{timestamp}.json` for analysis.

---

### v2.14.3 — Local Model Integration Stubs

- [ ] Stub integration point for Llama 3.2 Vision (via Ollama) as second-pass PII checker for low-confidence EasyOCR scans.
- [ ] MONAI slice extraction stub for DICOM MRI inputs — preprocessing only, actual analysis routes to cloud/MedGemma.
- [ ] Both stubs log a `DEBUG` message when triggered: `"[STUB] MONAI preprocessing not yet implemented — passing raw input."`.

---

## v2.13.0 — pytest Coverage 🧪 Planned

**Why:** Quality gate. Now we have a solid, refactored codebase to write tests against. Tests written before the architecture is stable are thrown away. Medical apps cannot fail silently.

---

### v2.13.1 — pytest Infrastructure

- [ ] `pytest`, `pytest-mock` already in `[dependency-groups] dev` in `pyproject.toml`. Add `pytest-asyncio`.
- [ ] Create `tests/` directory with `conftest.py` and shared fixture helpers.
- [ ] Verify `[tool.pytest.ini_options]` block in `pyproject.toml` is correct (testpaths, asyncio_mode).

---

### v2.13.2 — PII Scrubber Tests (`tests/test_anonymization.py`)

- [ ] Test that known PII patterns (JMBG, full names, phone numbers, addresses) are redacted.
- [ ] Test that clinical values (hemoglobin `11.2 mmol/L`, glucose `7.8`, BP `140/90`) are NOT redacted — over-anonymization regression tests.
- [ ] Test both Serbian Cyrillic and Latin script inputs.
- [ ] Test PDF page image redaction produces expected black-box coordinates.

---

### v2.13.3 — Medical Report Parser Tests (`tests/test_parsers.py`)

- [ ] Test `MedicalReportModel.model_validate_json()` against known good and bad JSON fixtures.
- [ ] Test `MedicalCriticalFindingModel` field extraction.
- [ ] Test empty / partial report graceful defaults.

---

### v2.13.4 — Provider Abstraction Tests (`tests/test_providers.py`)

- [ ] Mock `GeminiProvider.analyze()` and `ClaudeProvider.analyze()` — verify `ProviderFactory` routes correctly per `ProviderType`.
- [ ] Test `is_available()` returns `False` when keyring key is absent (mocked keyring).
- [ ] Test `ProviderFactory.available_providers()` with fully mocked keyring returning various key states.
- [ ] Test `DSClinic.set_active_provider()` switches correctly.

---

### v2.13.5 — `AppDatabase` / `JsonCollection` Tests (`tests/test_db.py`)

- [ ] Test save → load round-trip for `MedicalReport`, `ChatSessionModel`, `PatientRecord`.
- [ ] Test `list_index()` returns correct index entries without loading full record files.
- [ ] Test `delete()` removes record file and updates `_index.json`.
- [ ] Test `_rebuild_index_from_disk()` recovers correctly from a corrupted or missing `_index.json`.
- [ ] Test `count()` returns accurate value after save and delete operations.

---

### v2.13.6 — `AppSettings` / `load_unified` Tests (`tests/test_settings.py`)

- [ ] Test `load_unified()` correctly layers `config.json` → `settings.json` overrides.
- [ ] Test `importlib.metadata` `PackageNotFoundError` fallback returns field defaults.
- [ ] Test `save_unified()` excludes secret field names from written JSON.
- [ ] Test `BrandConfig` loads from `brand.json` and falls back to defaults when file absent.

---

## v2.12.0 — Chat Session View Rewrite + New Features 💬 Planned

**Why:** UX layer. Depends on v2.7.0 (sessions wired), v2.8.0 (provider abstraction ready). The Chat View is where users interact with analysis results — it must showcase the full pipeline and support the features that make the app feel like a real clinical tool.

---

### v2.12.1 — Streaming Bubble Fix & `MarkdownLabel.update_text()`

- [ ] Add `update_text(new_text: str)` method to `MarkdownLabel`: enable widget → clear → re-insert markdown → disable → recalculate height.
- [ ] Track `self._current_bot_bubble: Optional[MarkdownLabel]` in `ChatSessionView`.
- [ ] On first chunk: spawn one bubble, store reference. On subsequent chunks: call `_current_bot_bubble.update_text(full_text)` in-place.
- [ ] Clear reference when `var_is_analyzing` transitions `True → False`.
- [ ] Auto-scroll to bottom on each chunk update.

---

### v2.12.2 — Style Fixes & Provider Selector

- [ ] Fix `ChatUser.TFrame/TLabel` colors in `styles.py`: solid `ACCENT` blue + `WHITE` text (currently pale `ACCENT_LT`).
- [ ] Add provider selector dropdown in chat toolbar: lists `ProviderFactory.available_providers()`.
- [ ] Selecting a provider calls `DSClinic.set_active_provider(ProviderType)` immediately.
- [ ] Disable input area while `var_is_analyzing` is `True`; show loading indicator.

---

### v2.12.3 — Reanalyze Command & Additional Prompt Input

- [ ] Add "Reanalyze" button in chat toolbar.
- [ ] Reanalyze re-runs the initial analysis with an additional user prompt appended to system instructions.
- [ ] Additional prompt entry field: multiline `ttk.Entry` above the send button, pre-populated with current task description.
- [ ] Reanalyze result spawns a new bubble with `[Reanalysis]` prefix label.

---

### v2.12.4 — Report Inclusion Checkboxes

- [ ] Add `include_in_report: bool = True` field to `ChatMessage` model in `src/models/ai.py`.
- [ ] Each bot response bubble has a checkbox (default checked).
- [ ] Unchecked responses are excluded from the final PDF export.
- [ ] `ChatSessionModel.chat_history` stores the updated `include_in_report` flag per message.
- [ ] `write_report_pdf()` filters `chat_responses` by `include_in_report` before rendering.

---

## v2.11.0 — Enterprise Multi-Brand / White-Label & Subscription Config 🏢 Planned

**Why:** What makes DSClinic a real B2B SaaS product rather than a single-clinic tool. Two delivery modes: white-labeled per-client builds and a subscription SaaS app. See AD-04 and AD-20.

---

### v2.11.1 — `BrandConfig` Model & Loader (`src/models/brand.py`)

- [ ] Define `BrandConfig(BaseModel)` with fields: `clinic_name: str`, `clinic_subtitle: str`, `clinic_address: str`, `logo_path: str`, `primary_color: str`, `secondary_color: str`, `report_header_text: str`, `report_footer_text: str`, `subscription_tier: str` (`"trial"` / `"standard"` / `"enterprise"`).
- [ ] Load from `brand.json` adjacent to executable. Fall back to defaults if absent.
- [ ] Export `brand_config` singleton from `src/models/__init__.py`.

---

### v2.11.2 — Dynamic PDF Report Branding

- [ ] `pdf_maker.py` reads `brand_config` at generation time for logo, clinic name, header/footer text.
- [ ] Logo path resolved relative to executable directory (portable layout, AD-09).
- [ ] PDF color scheme driven by `brand_config.primary_color`.
- [ ] Trial tier: add watermark text overlay to every page.

---

### v2.11.3 — Dynamic GUI Branding

- [ ] Window title = `brand_config.clinic_name`.
- [ ] Toolbar/header label = `brand_config.clinic_name` + `brand_config.clinic_subtitle`.
- [ ] Logo image shown in main panel header if `brand_config.logo_path` resolves to an existing file.

---

### v2.11.4 — Clinic Profile Settings Section

- [ ] New "Clinic Profile" card in `settings_view.py`.
- [ ] Entry fields: Clinic Name, Subtitle, Address, Report Header Text, Report Footer Text.
- [ ] Logo file picker: View shows `filedialog.askopenfilename` via delegate callback; ViewModel holds path string.
- [ ] Save writes to `brand.json` via `BrandConfig` save method.
- [ ] Subscription tier display (read-only label for now).

---

### v2.11.5 — Subscription Tier Enforcement Stubs

- [ ] `trial`: PDF watermark active (v2.11.2), session limit warning after N analyses per day.
- [ ] `standard`: No watermark, unlimited sessions.
- [ ] `enterprise`: Stub only — multi-user and custom model support flagged as future milestone.
- [ ] Tier check implemented as a single `is_feature_allowed(feature: str) -> bool` gate function.

---

## v2.10.0 — Local Ollama Provider (16GB VRAM Optimized) 🖥️ Planned

**Why:** The most complex provider and the biggest EU interview differentiator. Demonstrates edge hardware optimization — running quantized medical LLMs on consumer hardware within a 16GB VRAM budget. See AD-13.

---

### v2.10.1 — Ollama Infrastructure & Config

- [ ] Add `ollama` SDK to `pyproject.toml` optional extras (`local`).
- [ ] Add `ollama_base_url: str = "http://localhost:11434"` to `AppSettings` (not keyring — not a secret).
- [ ] Add `ollama_supported_models` list to `config.json` (e.g. `llama3.2-vision:q4_0`, `medgemma:q4_0`).
- [ ] Add Ollama base URL entry field (plain, unmasked) to Settings UI under a new "Local AI" section.

---

### v2.10.2 — `OllamaProvider` Core Implementation

- [ ] Implement `OllamaProvider(LLMProvider)` in `src/providers/ollama_provider.py`.
- [ ] `is_available()` → ping `ollama.list()` — returns `True` only if daemon is running.
- [ ] `analyze()` → uses vision-capable model for document OCR + extraction into `MedicalReportModel` JSON.
- [ ] `ask()` → streaming text response via `ollama.chat(stream=True)`.

---

### v2.10.3 — Load-on-Demand & VRAM Sequential Guard

- [ ] Model pulled via `ollama.pull()` only when first needed — not at startup.
- [ ] Before loading a new model: unload previous via model swap to prevent VRAM thrashing.
- [ ] 4-bit quantization enforced via model name tag (e.g. `llama3.2-vision:q4_0`) — Ollama handles quantization automatically.
- [ ] Log VRAM optimization decisions at `DEBUG` level for portfolio demo visibility.

---

### v2.10.4 — Register Ollama in `ProviderFactory`

- [ ] Add `ProviderType.OLLAMA` to `base.py`.
- [ ] Update `ProviderFactory.create()` to construct `OllamaProvider`.
- [ ] Update `ProviderFactory.available_providers()` — Ollama listed last in priority order.

---

## v2.9.0 — Groq + Together AI + HuggingFace Cloud Providers ☁️ Planned

**Why:** Extends v2.8.0. These are the fast, GDPR-compliant open-weights API providers forming the middle tier of the Split-Horizon Architecture. Demonstrates multi-vendor resilience and cost optimization strategy to EU interviewers.

---

### v2.9.1 — Credential & Config Infrastructure for New Providers

- [ ] Add to `keyring_manager._CREDENTIAL_KEYS`: `"groq"` → `"groq_api_key"`, `"together"` → `"together_api_key"`, `"huggingface"` → `"huggingface_api_key"`.
- [ ] Add three new `var_*_api_key` vars to `SettingsViewModel`, reading from keyring.
- [ ] Add three new `_credential_field(...)` entries to Settings UI (`settings_view.py`).
- [ ] Add `groq_supported_models`, `together_supported_models`, `huggingface_supported_models` to `config.json`.
- [ ] Add new SDK dependencies to `pyproject.toml`: `groq`, `together`, `huggingface_hub`.

---

### v2.9.2 — `GroqProvider`

- [ ] Implement `GroqProvider(LLMProvider)` in `src/providers/groq_provider.py`.
- [ ] `is_available()` → keyring key present.
- [ ] `analyze()` → structured prompt → JSON response → `MedicalReportModel`.
- [ ] `ask()` → streaming chat completion via Groq API.
- [ ] Startup guard: log warning + return early if key absent.

---

### v2.9.3 — `TogetherProvider`

- [ ] Implement `TogetherProvider(LLMProvider)` in `src/providers/together_provider.py`.
- [ ] Same interface and guard pattern as `GroqProvider`.
- [ ] Configurable endpoint and model via `config.json` `together_supported_models`.

---

### v2.9.4 — `HuggingFaceProvider`

- [ ] Implement `HuggingFaceProvider(LLMProvider)` in `src/providers/huggingface_provider.py`.
- [ ] Uses `huggingface_hub` inference client.
- [ ] Configurable endpoint URL for hosted medical models (BioMistral, Llama-3-Medical).
- [ ] `is_available()` → keyring key present + endpoint reachable.

---

### v2.9.5 — Register New Providers in `ProviderFactory`

- [ ] Add `ProviderType.GROQ`, `TOGETHER`, `HUGGINGFACE` to `base.py`.
- [ ] Update `ProviderFactory.create()` to construct all three new providers.
- [ ] Update `ProviderFactory.available_providers()` to include all three.

---

## v2.8.0 — `src/providers/` LLMProvider Abstraction (Gemini + Claude) ✅ Completed

**`LLMProvider` ABC, `ProviderFactory`, `GeminiProvider`, `ClaudeProvider` implemented. `DSClinic` routes all AI calls through the provider interface. Direct SDK client imports eliminated from `dsclinic.py`.**

---

### v2.8.4 — Refactor `DSClinic` to Use `ProviderFactory` ✅ Completed

- [x] Replace direct `MedicalAnalyzerClient` / `ClaudeAnalyzerClient` instantiation with `ProviderFactory.create(provider_type)`.
- [x] Add `active_provider: LLMProvider | None` attribute to `DSClinic`.
- [x] Add `set_active_provider(provider_type: ProviderType) -> None` method.
- [x] `get_initial_analysis_report()` → builds `ProviderRequest`, calls `self.active_provider.analyze(request)`.
- [x] `ask_followup_question()` → calls `self.active_provider.ask(question)`, accumulates `Iterator[str]` into full string.
- [x] Default provider on startup: first available from `ProviderFactory.available_providers()`, priority: `GEMINI → CLAUDE → GROQ → TOGETHER → HUGGINGFACE → OLLAMA`.

---

### v2.8.3 — `ProviderFactory` (`src/providers/factory.py`) ✅ Completed

- [x] Implement `ProviderFactory`:
  - [x] `create(provider_type: ProviderType) -> LLMProvider` — constructs provider; raises `NotImplementedError` for v2.9.x/v2.10.x backends (stub). Lazy imports per provider type to keep SDK dependencies deferred.
  - [x] `available_providers() -> list[ProviderType]` — iterates `_PROVIDER_PRIORITY`, skips `NotImplementedError` and unexpected exceptions; returns ordered list of available types.
- [x] Export `ProviderFactory` from `src/providers/__init__.py`.

---

### v2.8.2 — `GeminiProvider` & `ClaudeProvider` Concrete Implementations ✅ Completed

- [x] Implement `GeminiProvider(LLMProvider)` in `src/providers/gemini_provider.py`:
  - [x] Delegates to existing `api_gemini/client.py::MedicalAnalyzerClient`.
  - [x] `is_available()` → checks keyring key presence + client init status.
- [x] Implement `ClaudeProvider(LLMProvider)` in `src/providers/claude_provider.py`:
  - [x] Delegates to existing `api_claude/client.py::ClaudeAnalyzerClient`.
  - [x] `is_available()` → checks keyring key + client init status.

---

### v2.8.1 — `LLMProvider` Abstract Base & Data Contracts (`src/providers/base.py`) ✅ Completed

- [x] Create `src/providers/` package with `__init__.py`.
- [x] Define `ProviderType(StrEnum)`: `GEMINI`, `CLAUDE`, `GROQ`, `TOGETHER`, `HUGGINGFACE`, `OLLAMA`.
- [x] Define `ProviderRequest(BaseModel)`: `documents: list[Any]`, `question: str`, `system_instructions: list[str]`, `temperature: float`, `max_tokens: int`.
- [x] Define `ProviderResponse(BaseModel)`: `text: str`, `provider: ProviderType`, `model_name: str`, `tokens_used: int | None`.
- [x] Define `LLMProvider(ABC)` with abstract methods:
  - [x] `analyze(request: ProviderRequest) -> MedicalReportModel`
  - [x] `ask(question: str) -> Iterator[str]`
  - [x] `provider_type() -> ProviderType`
  - [x] `is_available() -> bool`

---

## v2.7.0 — Patient Record as First-Class Entity & Session Persistence ✅ Completed

**AppDatabase fully wired. Reports and sessions auto-persisted. PatientRecord is a first-class entity with a full CRUD sidebar (Sessions + Patients tabs). Session→Patient linkage complete.**

---

### v2.7.4 — Patient List Panel (View + ViewModel) ✅ Completed

- [x] Add `var_patients_index: list[dict]` to ViewModel, populated from `self._db.patients.list_index()`.
- [x] Build a patient list panel listing all patients (name, created_at, session count).
- [x] Clicking a patient filters the session history panel to show only their sessions.
- [x] Add a "New Patient" form: full name, date of birth → creates `PatientRecord` and saves to `_db.patients`.

---

### v2.7.3 — Session History Panel (View + ViewModel) ✅ Completed

- [x] Add `var_sessions_index: list[dict]` observable to ViewModel, populated from `self._db.sessions.list_index()`.
- [x] Build a session history sidebar or panel in the main View listing recent sessions (patient name, date, session_id).
- [x] Clicking a session loads the full `ChatSessionModel` via `self._db.sessions.load(session_id)` and restores analysis state.
- [x] Add a "New Session" button that clears current state and starts fresh.

---

### v2.7.2 — Wire `AppDatabase` into `DSClinicViewModel` ✅ Completed

- [x] Instantiate `AppDatabase` once in `DSClinicViewModel.__init__` — store as `self._db`.
- [x] After successful analysis (`TaskStatus.FINISHED` with `MedicalReport`): auto-save report via `self._db.reports.save(report.report_id, report)`.
- [x] After each follow-up Q&A exchange: update and re-save `ChatSessionModel` via `self._db.sessions.save(session.session_id, session)`.
- [x] Wrap all `_db` calls in `try/except (OSError, json.JSONDecodeError)` — log error and continue without crashing.

---

### v2.7.1 — `PatientRecord` Model & `AppDatabase` Extension ✅ Completed

- [x] Add `PatientRecord(BaseModel)` to `src/models/patient.py`:
  - [x] Fields: `patient_id: str` (uuid4 hex), `full_name: str`, `date_of_birth: str`, `created_at: str`, `session_ids: list[str]`.
- [x] Add `patients: JsonCollection[PatientRecord]` collection to `AppDatabase` at `app_data/patients/`.
- [x] Index fields for patients: `patient_id`, `full_name`, `created_at`.
- [x] Export `PatientRecord` from `src/models/__init__.py`.

---

## v2.6.0 — Secure Credential Management & `settings.ini` Elimination ✅ Completed

**All credentials migrated to OS keyring. `settings.ini` permanently deleted. Keys rotated. App verified working.**

### v2.6.7 — Rotate Keys, Delete `settings.ini`, Final Cleanup ✅ Completed

- [x] Revoked and regenerated `GOOGLE_API_KEY` in Google AI Studio.
- [x] Revoked and regenerated `ANTHROPIC_API_KEY` in Anthropic Console.
- [x] New keys entered via Settings → AI → credential fields — written to OS keyring.
- [x] App verified working end-to-end with keyring-sourced Gemini key.
- [x] `git rm settings.ini` — file permanently deleted from repository.
- [x] `GEMINI.md` updated: credential management rule added to § 3.D, `keyring` added to § 2 Technical Stack.
- [x] `CHANGELOG.md` updated with full v2.6.0 release entry.
- [x] `docs/session_handoff.md` advanced to v2.5.0 active.

---

### v2.6.6 — Runtime Key Consumption: `dsclinic.py` & API Clients ✅ Completed

- [x] `ClaudeAnalyzerClient` instantiated in `DSClinic.__init__` using `get_credential("anthropic")` — was previously missing entirely.
- [x] Claude client wrapped in startup guard: `self.claude_client = None` if key absent — app starts without crashing.
- [x] `ClaudeModelConfig` and `ClaudeAIServiceConfig` imported and wired in `dsclinic.py`.
- [x] `api_gemini/client.py` — replaced `raise ValueError` on missing key with `logger.warning` + early `return`. `RuntimeError` raised at call time with Settings navigation hint.
- [x] `api_claude/client.py` — same startup guard pattern applied.
- [x] Both clients guard `self.client`/`self.chat_session` before use — `RuntimeError` with clear message if called without a key.
- [x] `src/api_gemini/client.py`: zero `app_settings.*` references — key via `config.api_key` only.
- [x] `src/api_claude/client.py`: zero `app_settings.*` references — key via `config.api_key` only.

---

### v2.6.5 — Settings UI: Masked Key Entry Fields ✅ Completed

- [x] New `_credential_field(parent, label, var)` helper: masked `ttk.Entry` (`show="*"`) + `SUBTLE`-coloured hint label `"Stored securely in OS keyring — never written to disk."`.
- [x] Three credential fields rendered in `_build_analyze_instructions_panel`: Google API Key, Anthropic API Key, Google Project ID.
- [x] Old plain `_entry_field("Google API Key", ...)` call replaced.
- [x] `_HEIGHT` bumped from 760 to 860px to accommodate the additional fields.

---

### v2.6.4 — `SettingsViewModel`: Read & Write Credentials via Keyring ✅ Completed

- [x] `var_google_api_key` reads from `get_credential("gemini") or ""`.
- [x] `var_anthropic_api_key = tk.StringVar(value=get_credential("anthropic") or "")` added.
- [x] `var_google_project_id = tk.StringVar(value=get_credential("google_project_id") or "")` added.
- [x] `update_from_config()` refreshes all three from keyring.
- [x] `save_to_config()` writes all three via `set_credential(...)`. Does **not** write via `save_unified()`.
- [x] `app_settings.google_api_key` assignment removed from `save_to_config()`.
- [x] `get_credential`, `set_credential` imported from `models`.

---

### v2.6.3 — `AppSettings`: Remove All Secret Fields ✅ Completed

- [x] `google_api_key: str = ""` and `anthropic_api_key: str = ""` removed from `AppSettings`.
- [x] Entire `configparser` / `settings.ini` INI block removed from `load_unified()`.
- [x] `configparser` import removed.
- [x] `"google": {"project_location": "us-central1"}` block added to `config.json`.
- [x] `google_project_location: str = "us-central1"` field added to `AppSettings`.
- [x] `google_project_location` read from `config.json` in `load_unified()`.
- [x] `"google_api_key"` and `"anthropic_api_key"` added to `exclude_fields` in `save_unified()`.
- [x] Hotfix: `dsclinic.py` patched to use `get_credential("gemini")` — unblocks app startup.

---

### v2.6.2 — `keyring_manager.py`: Secure Credential Store Module ✅ Completed

- [x] Created `src/models/keyring_manager.py` with `_KEYRING_SERVICE = "dsclinic"`.
- [x] `_CREDENTIAL_KEYS` mapping: `"gemini"` → `"gemini_api_key"`, `"anthropic"` → `"anthropic_api_key"`, `"google_project_id"` → `"google_project_id"`.
- [x] `get_credential(name: str) -> str | None` implemented.
- [x] `set_credential(name: str, value: str) -> None` implemented.
- [x] `delete_credential(name: str) -> None` implemented.
- [x] All three exported from `src/models/__init__.py`.
- [x] `keyring` in `pyproject.toml` dependencies.

---

### v2.6.1 — `pyproject.toml`: App Name & Version as Single Source of Truth ✅ Completed

- [x] `importlib.metadata.metadata("dsclinic")` reads `app_name` and `app_version` in `load_unified()` as step A0.
- [x] `[APP]` NAME/VERSION block removed from `settings.ini` INI parsing.
- [x] `app_name` and `app_version` added to `exclude_fields` in `save_unified()`.
- [x] `pyproject.toml` is now the single source of truth for both fields.

---

## v2.5.0 — MVVM Strict Compliance & Defensive Error Handling Audit ✅ Completed

### v2.5.4 — `pyproject.toml` + `uv` Migration & README Rewrite ✅ Completed

- [x] `pyproject.toml` — added `requires-python`, `authors`, `readme`, `license` metadata (GASSI pattern, AD-21).
- [x] `pyproject.toml` — full runtime dep set with version pins: `fpdf2>=2.7`, `presidio-analyzer>=2.2`, `presidio-anonymizer>=2.2`, `spacy>=3.7`, `easyocr>=1.7`, `Pillow>=11.0`, `pdf2image>=1.17`.
- [x] `pyproject.toml` — added `[project.optional-dependencies]`: `claude`, `local`, `providers` extras.
- [x] `pyproject.toml` — added `[dependency-groups] dev`: `mypy>=1.13`, `pytest>=8.3`, `pytest-mock>=3.14`, `pyinstaller>=6.11`.
- [x] `pyproject.toml` — all tool config migrated in: `[tool.mypy]` (full exclude list), `[tool.pytest.ini_options]`, `[tool.autopep8]`.
- [x] `mypy.ini` — deleted (`git rm mypy.ini`). All config now in `[tool.mypy]`.
- [x] `README.md` — full rewrite: `uv` install, `uv sync --group dev`, optional extras, spaCy model download, keyring credential setup, run/mypy/pytest/pyinstaller commands, project structure, Split-Horizon architecture overview.
- [x] `.dev_profile/developer_profile.md` — added §6 Code Commenting Standard.
- [x] `docs/architecture.md` — added AD-21: `pyproject.toml` + `uv` canonical toolchain.

---

### v2.5.3 — Type Hints Audit (`mypy --strict`) ✅ Completed

- [x] Add missing return type annotations to all functions in `src/dsclinic.py`, `src/dsclinic_gui/report_view_models.py`, `src/dsclinic_gui/settings/`.
- [x] Add missing type annotations to `src/db/app_database.py` and `src/db/json_collection.py`.
- [x] Run `mypy --strict src/` and fix all errors — **0 errors across 26 checked files**.
  - `db/json_collection.py` — all bare `dict` → `dict[str, Any]`; `_load_raw_index` return typed; `_build_index_entry` node traversal typed.
  - `models/ai.py` — `tuple` → `tuple[str, ...]` on both `system_instruction` fields.
  - `models/diagnostics.py` — `UserList[T]` parameterised; `ObservableList` fully annotated (`__init__`, `extend`, `__setitem__`, `__delitem__`, `__iter__`).
  - `api_gemini/client.py` — `chat_session: Optional[Any]`; `-> None` on all methods; `SafetySetting` uses enum members; `system_instruction` passed as `str`.
  - `api_gemini/utils.py` — `Optional[types.Part]` return; `None` init removed.
  - `api_claude/client.py` — unused `MessageParam` import removed; `user_content: Any` cast eliminates TypedDict mismatch; all bare `dict` type-args filled; `# type: ignore` codes corrected.
  - `api_claude/utils.py` — `dict[str, Any]` throughout; `frozenset[str]` constants typed.
  - `dsclinic.py` — `__init__ -> None`; explicit `result: str` on `ask_followup_question` removes `no-any-return`.
  - `dsclinic_gui/report_view_models.py` — `callable` → `Callable[..., Any]`; `mp_input_queue`/`mp_output_queue` annotated as `multiprocessing.Queue[Any]`; `_` calls suppressed with `# type: ignore[name-defined]`.
  - `dsclinic_gui/chat_session_view.py` — full annotations on `MarkdownLabel`; `_wheel` typed as `Any`; `anchor` typed as `Literal["e", "w"]`; unused `Optional` import and unused `# type: ignore` comments removed.
- [x] `mypy.ini` created with strict config and exclude list for View-layer files deferred to rewrite milestones.
- [x] `src/test_guis/` removed from git tracking via `git rm -r src/test_guis/`.
- [x] Verify `docs/architecture.md` AD-01, AD-02, AD-16 accurately reflect the post-audit state.

---

### v2.5.2 — Defensive Error Handling Audit ✅ Completed

- [x] Grep entire `src/` for bare `except:` — must be zero. Replace all with specific exception types.
- [x] Wrap all `src/db/` file I/O operations in `try/except (OSError, json.JSONDecodeError)` with logging.
  - `json_collection.py` `_write_raw_index()`: `OSError` guard added, logs and re-raises.
  - `json_collection.py` `save()`: record `write_text()` wrapped in `OSError` guard.
  - `json_collection.py` `load()`: `read_text()` + `model_validate_json()` wrapped in `(OSError, json.JSONDecodeError, ValidationError)` — returns `None` on any failure.
  - `json_collection.py` `delete()`: `path.unlink()` wrapped in `OSError` guard.
- [x] Wrap all keyring calls in `try/except keyring.errors.*` with graceful fallback.
  - `keyring_manager.py` `get_credential()`: `keyring.errors.KeyringError` guard added — returns `None`.
  - `keyring_manager.py` `set_credential()`: `keyring.errors.KeyringError` guard added — logs and returns without raising.
  - `keyring_manager.py` `delete_credential()`: added `keyring.errors.KeyringError` branch alongside existing `PasswordDeleteError`.
- [x] Wrap all background worker thread bodies in `try/except Exception` — always write `TaskStatus.FAILED` event to queue on failure, never let thread die silently.
  - `report_view_models.py` worker threads: already fully wrapped (verified in v2.5.1 audit).
- [x] Verify all `ProgressEvent(status=TaskStatus.FAILED)` events surface a user-readable message in the UI — not a raw Python exception string.
  - Verified: all `FAILED` events emit `ErrorMessageEvent` via `on_show_error_message` in `_apply_progress_event`.
- [x] Additional: `dsclinic.py` `get_initial_analysis_report()` — added `None` check on `report_content`; raises `RuntimeError` with user-readable message instead of crashing on `MedicalReport(content=None)`.

---

### v2.5.1 — MVVM Boundary Audit ✅ Completed

- [x] Grep entire `src/dsclinic_gui/` for any `tkinter` widget imports (`Label`, `Button`, `Frame`, `ttk.*`) inside ViewModel files — must be zero.
- [x] Verify no ViewModel calls `filedialog`, `messagebox`, or any dialog directly — delegate pattern only.
- [x] Verify all background tasks use `threading.Thread` + `queue.Queue` + `root.after` polling — no direct widget mutations from worker threads.
- [x] Verify `schedule_poll_fn` is the only Tkinter coupling in every ViewModel.
- [x] Document any violations found and fix each one.
  - Fixed: `chat_session_view.py` directly mutated `view_model._model.chat_responses` — replaced with `view_model.append_chat_response(text)` delegate method.
  - Fixed: `execute_export()` raised raw exceptions to the View — now catches internally and emits `on_show_error_message`.
  - Added `-> None` return type annotations to all unannotated ViewModel methods.

---

## v2.4.0 — Unified Configuration, MVVM Schema & High-Privacy Alignment ✅ Completed

- [x] **Consolidate Models into `src/models/` Package:**
  - [x] Created unified package folder.
  - [x] Migrated patient schemas into `src/models/patient.py` and diagnostic structures into `src/models/diagnostics.py`.
  - [x] Deleted legacy flat `src/models.py` and `src/models_new/` folders.
- [x] **Implement Future-Proof Unified `src/models/settings.py`:**
  - [x] Built the Pydantic-Settings `AppSettings` class as single source of truth.
  - [x] Merged layered loading (`load_unified`) from baselines and clinician overrides under `.config/medai_vitec/settings.json`.
  - [x] Supported atomic `save_unified` writes.
  - [x] Deleted legacy `src/config.py` and `src/npy/core/settings_manager.py`.
- [x] **Codebase-Wide Import Refactoring:** All files use `from models.settings import app_settings`.
- [x] **Settings UI Migration:** `SettingsViewModel` and `SettingsWindow` bind directly to `app_settings`.
- [x] **Refactor Configuration Loader:** Two-tiered loader reading `config.json` layered with `settings.json`.

---

## v2.1.10 — UI & Layout Refinement ✅ Completed

- [x] Centered section headers in main panel: `anchor="center"` on card titles in `_card` factory.
- [x] Settings window layout restructuring: Reworked `_build_general_section`, created `_build_support_section`.
- [x] Resolved nested-tuple serialization bug on multiple settings saves.
- [x] Token-optimized prompt transmission: Automatic newline/whitespace cleaning before Gemini API calls.
