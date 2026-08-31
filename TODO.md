# TODO — DSClinic Roadmap

> [!NOTE]
> **Task Management Rule (GASSI Standard):** This document is maintained in **strict descending version order**. The current active focus and upcoming planned versions must always be placed at the top, while completed releases move down into the historical archive at the bottom. Always update this list and session handoffs on every single code change.
>
> **Sub-version Rule:** Every parent milestone (e.g. v2.5.0) is broken into numbered sub-tasks (v2.5.1, v2.5.2, ...). Each sub-version is a self-contained, committable unit of work. Sub-versions are completed in order; the parent is marked done only when all sub-versions are complete.
>
> **TODO Archiving Rule:** Completed versions are never collapsed or summarised. Every completed sub-version and its full task list remains fully expanded with `[x]` checkboxes indefinitely.

---

## v2.5.0 — Enterprise MedTech Platform: Core Architecture & Feature Pipeline 🚀 Active

**The "MVP to Scale" portfolio narrative.** An MVP was rapidly prototyped to validate a medical business idea with a real user. This milestone drives the full architectural overhaul to make it enterprise-grade: strict MVVM, pluggable multi-provider inference pipeline, patient session management, PII compliance, multi-brand white-labeling, and automated test coverage. Every sub-version is a demonstrable portfolio piece that answers a specific EU recruiter question.

---

### v2.5.1 — MVVM Strict Compliance & Defensive Error Handling Audit

**Why first:** Everything built on top of a broken foundation stays broken. Medical apps cannot silently crash or leak state. This is the #1 discipline question in EU HealthTech interviews.

- [ ] **Full MVVM boundary audit across all ViewModels:**
  - [ ] Grep entire `src/dsclinic_gui/` for any `tkinter` widget imports (`Label`, `Button`, `Frame`, `ttk.*`) inside ViewModel files — must be zero.
  - [ ] Verify no ViewModel calls `filedialog`, `messagebox`, or any dialog directly — delegate pattern only.
  - [ ] Verify all background tasks use `threading.Thread` + `queue.Queue` + `root.after` polling — no direct widget mutations from worker threads.
  - [ ] Verify `schedule_poll_fn` is the only Tkinter coupling in every ViewModel.
- [ ] **Defensive error handling audit across all source files:**
  - [ ] Grep for bare `except:` — must be zero. Replace all with specific exception types.
  - [ ] Wrap all `src/db/` file I/O operations in `try/except (OSError, json.JSONDecodeError)` with logging.
  - [ ] Wrap all keyring calls in `try/except keyring.errors.*` with graceful fallback.
  - [ ] Wrap all background worker thread bodies in `try/except Exception` — always write a `TaskStatus.FAILED` event to the queue on failure, never let the thread die silently.
  - [ ] Verify all `ProgressEvent(status=TaskStatus.FAILED)` events surface a user-readable message in the UI (not a raw Python exception string).
- [ ] **Type hints audit:**
  - [ ] Add missing return type annotations to all functions in `src/dsclinic.py`, `src/dsclinic_gui/report_view_models.py`, `src/dsclinic_gui/settings/`.
  - [ ] Run `mypy --strict src/` and fix all errors.
- [ ] **Update `docs/architecture.md`:** Verify AD-01, AD-02, AD-16 accurately reflect the post-audit state.

---

### v2.5.2 — Patient Record as First-Class Entity & Session Persistence UI

**Why second:** `AppDatabase` (sessions, reports, ai_profiles) and `JsonCollection[T]` are already fully implemented in `src/db/` but never wired to any ViewModel or View. `ChatSessionModel` and `MedicalReport` exist but are never persisted after analysis. Sessions and patient records are the data foundation everything else depends on.

**Architectural decision:** A `Patient` model is needed as a first-class entity that owns multiple sessions. Currently a patient is only a name string inside `MedicalReport`. An EU B2B clinic app must track recurring patients across visits.

- [ ] **Extend `src/models/patient.py` — add `PatientRecord` model:**
  - [ ] `PatientRecord(BaseModel)` with fields: `patient_id: str` (uuid), `full_name: str`, `date_of_birth: str`, `created_at: str`, `session_ids: list[str]` (references to `ChatSessionModel.session_id`).
  - [ ] Add `patients` collection to `AppDatabase`: `JsonCollection[PatientRecord]` at `app_data/patients/`.
  - [ ] Index fields: `patient_id`, `full_name`.
- [ ] **Wire `AppDatabase` into `DSClinicViewModel`:**
  - [ ] Instantiate `AppDatabase` once in `DSClinicViewModel.__init__`.
  - [ ] After successful analysis (`TaskStatus.FINISHED` with `MedicalReport`): auto-save the report via `db.reports.save(report.report_id, report)`.
  - [ ] After each follow-up Q&A exchange: update and re-save the `ChatSessionModel` via `db.sessions.save(session.session_id, session)`.
- [ ] **Session history panel / patient list (new View or sidebar section):**
  - [ ] List recent sessions from `db.sessions.list_index()` (fast, no full records loaded).
  - [ ] Allow clicking a session to load the full `ChatSessionModel` and restore the analysis state.
  - [ ] Allow clicking a patient to show all their sessions.
- [ ] **Add `AD-18` to `docs/architecture.md`:** Document `PatientRecord` as first-class entity and `AppDatabase` wiring decision.

---

### v2.5.3 — `src/providers/` LLMProvider Abstraction (Gemini + Claude)

**Why third:** The core architectural showpiece. Every cloud/local provider sub-version (v2.5.4, v2.5.5) depends on this interface. The interview pitch is: *"I designed a pluggable inference pipeline that hot-swaps between 6 providers without touching business logic."* Currently `DSClinic` is hard-coupled to `MedicalAnalyzerClient` — this is vendor lock-in.

**Package structure:**
```
src/providers/
    __init__.py          # exports LLMProvider, ProviderFactory, ProviderType
    base.py              # LLMProvider ABC + ProviderRequest/ProviderResponse dataclasses
    factory.py           # ProviderFactory.create(provider_type, config) → LLMProvider
    gemini_provider.py   # GeminiProvider — delegates to api_gemini/client.py
    claude_provider.py   # ClaudeProvider — delegates to api_claude/client.py
```

- [ ] **Define `LLMProvider` abstract base (`src/providers/base.py`):**
  - [ ] `ProviderType(StrEnum)`: `GEMINI`, `CLAUDE`, `GROQ`, `TOGETHER`, `HUGGINGFACE`, `OLLAMA`.
  - [ ] `ProviderRequest(BaseModel)`: `documents: list`, `question: str`, `system_instructions: list[str]`, `temperature: float`, `max_tokens: int`.
  - [ ] `ProviderResponse(BaseModel)`: `text: str`, `provider: ProviderType`, `model_name: str`, `tokens_used: int | None`.
  - [ ] `LLMProvider(ABC)`: abstract methods `analyze(request) → MedicalReportModel`, `ask(question: str) → Iterator[str]`, `provider_type() → ProviderType`, `is_available() → bool`.
- [ ] **Implement `GeminiProvider` (`src/providers/gemini_provider.py`):**
  - [ ] Wraps existing `MedicalAnalyzerClient`. Implements `LLMProvider` interface.
  - [ ] `is_available()` → `bool` based on keyring key presence and client init status.
- [ ] **Implement `ClaudeProvider` (`src/providers/claude_provider.py`):**
  - [ ] Wraps existing `ClaudeAnalyzerClient`. Implements `LLMProvider` interface.
  - [ ] `is_available()` → checks keyring + client init status.
- [ ] **Implement `ProviderFactory` (`src/providers/factory.py`):**
  - [ ] `create(provider_type: ProviderType, ...) → LLMProvider` — constructs the right provider from keyring credentials + app_settings.
  - [ ] `available_providers() → list[ProviderType]` — returns all providers that have valid credentials.
- [ ] **Refactor `DSClinic` to use `ProviderFactory`:**
  - [ ] Replace direct `MedicalAnalyzerClient` / `ClaudeAnalyzerClient` instantiation with `ProviderFactory.create(provider_type)`.
  - [ ] Add `active_provider: LLMProvider` attribute to `DSClinic`.
  - [ ] `get_initial_analysis_report()` → calls `active_provider.analyze(request)`.
  - [ ] `ask_followup_question()` → calls `active_provider.ask(question)`.
- [ ] **Add `AD-19` to `docs/architecture.md`:** Document `src/providers/` package structure, `LLMProvider` interface, and `ProviderFactory` pattern.
- [ ] **Export from `src/providers/__init__.py`:** `LLMProvider`, `ProviderFactory`, `ProviderType`, `ProviderRequest`, `ProviderResponse`.

---

### v2.5.4 — Groq + Together AI + HuggingFace Cloud Providers

**Why here:** Extends v2.5.3. These are the fast, GDPR-compliant open-weights API providers that form the middle tier of the Split-Horizon Architecture. Groq/Together serve anonymized extraction tasks; cloud Gemini/Claude handle reasoning on the cleaned output.

```
src/providers/
    groq_provider.py
    together_provider.py
    huggingface_provider.py
```

- [ ] **Add provider credentials to keyring:**
  - [ ] Add `"groq"` → `"groq_api_key"`, `"together"` → `"together_api_key"`, `"huggingface"` → `"huggingface_api_key"` to `keyring_manager._CREDENTIAL_KEYS`.
  - [ ] Add the three new vars to `SettingsViewModel` and Settings UI (`_credential_field` each).
- [ ] **Implement `GroqProvider` (`src/providers/groq_provider.py`):**
  - [ ] Uses `groq` Python SDK (`pip install groq`). Add to `pyproject.toml`.
  - [ ] Startup guard: `is_available()` checks keyring key.
  - [ ] `analyze()` → sends anonymized structured prompt, parses JSON response into `MedicalReportModel`.
  - [ ] `ask()` → streaming chat response via Groq chat completion API.
  - [ ] Supported models configurable via `app_settings` / `config.json`.
- [ ] **Implement `TogetherProvider` (`src/providers/together_provider.py`):**
  - [ ] Uses `together` Python SDK. Add to `pyproject.toml`.
  - [ ] Same interface as `GroqProvider`.
- [ ] **Implement `HuggingFaceProvider` (`src/providers/huggingface_provider.py`):**
  - [ ] Uses `huggingface_hub` inference client. Add to `pyproject.toml`.
  - [ ] Configurable endpoint URL for hosted medical models (BioMistral, Llama-3-Medical).
- [ ] **Add `ProviderType.GROQ`, `TOGETHER`, `HUGGINGFACE` to `base.py` and `factory.py`.**
- [ ] **Add supported models to `config.json`:** `groq_supported_models`, `together_supported_models`, `huggingface_supported_models`.

---

### v2.5.5 — Local Ollama Provider (16GB VRAM Optimized, Load-on-Demand)

**Why here:** The most complex provider. Demonstrates edge hardware optimization — a major EU interview differentiator. 16GB VRAM constraint means sequential "load on demand" model switching, not concurrent loading.

```
src/providers/
    ollama_provider.py
```

- [ ] **Add `keyring_manager` entry for Ollama base URL** (local, not a secret, but keep consistent): `"ollama_base_url"` → stored in `app_settings` (not keyring, it's not sensitive).
- [ ] **Implement `OllamaProvider` (`src/providers/ollama_provider.py`):**
  - [ ] Uses `ollama` Python SDK (`pip install ollama`). Add to `pyproject.toml`.
  - [ ] `is_available()` → pings `ollama.list()` to check if daemon is running.
  - [ ] **Load-on-demand:** Model is pulled (`ollama.pull()`) only when first needed, not at startup.
  - [ ] `analyze()` → uses vision-capable model (e.g. `llama3.2-vision`) for document OCR + extraction into `MedicalReportModel` JSON.
  - [ ] `ask()` → streaming text response via `ollama.chat()` with `stream=True`.
  - [ ] **4-bit quantization:** Configured via model name tag (e.g. `llama3.2-vision:q4_0`) — Ollama handles quantization automatically.
  - [ ] **VRAM sequential guard:** Only one model loaded at a time. Before loading a new model, unload the previous via `ollama.delete()` or model swap.
  - [ ] Supported local models configurable via `config.json` `ollama_supported_models` list.
- [ ] **Add `ProviderType.OLLAMA` to `base.py` and `factory.py`.**
- [ ] **Add Ollama base URL field to `AppSettings` and Settings UI** (plain entry field, no masking — not a secret).

---

### v2.5.6 — Enterprise Multi-Brand / White-Label & Subscription Config

**Why here:** The system must work before it can be branded. Depends on `AppDatabase` (v2.5.2) being wired for per-clinic settings. This is what makes the app a real B2B SaaS product, not a single-clinic tool.

**Business model:** Two delivery modes:
1. **White-labeled B2B:** Custom logo, clinic name, colors, PDF header/footer per client. Distributed as a branded `.exe` with a pre-configured `brand.json`.
2. **Subscription SaaS:** Single app, user pays subscription, configures their own clinic profile via Settings → Clinic Profile.

- [ ] **`BrandConfig` model (`src/models/brand.py`):**
  - [ ] Fields: `clinic_name: str`, `clinic_subtitle: str`, `clinic_address: str`, `logo_path: str`, `primary_color: str`, `secondary_color: str`, `report_header_text: str`, `report_footer_text: str`, `subscription_tier: str` (`"trial"`, `"standard"`, `"enterprise"`).
  - [ ] Loaded from `brand.json` (adjacent to `.exe`). If absent, falls back to defaults.
  - [ ] `brand_config` singleton exported from `src/models/`.
- [ ] **Dynamic PDF report branding:**
  - [ ] `pdf_maker.py` reads `brand_config` at generation time for logo, clinic name, header/footer text.
  - [ ] Logo path resolved relative to executable directory (portable layout, AD-09).
  - [ ] PDF color scheme driven by `brand_config.primary_color`.
- [ ] **Dynamic GUI branding:**
  - [ ] Window title = `brand_config.clinic_name`.
  - [ ] Toolbar/header displays `brand_config.clinic_name` + `brand_config.clinic_subtitle`.
  - [ ] Logo image shown in main panel header if `brand_config.logo_path` exists.
- [ ] **Clinic Profile settings section** (new card in `settings_view.py`):
  - [ ] Entry fields: Clinic Name, Subtitle, Address, Report Header Text, Report Footer Text.
  - [ ] Logo file picker (View shows dialog, ViewModel holds path string).
  - [ ] Saved to `brand.json` via `save_unified()` equivalent.
- [ ] **`subscription_tier` enforcement stubs:**
  - [ ] `trial`: Watermark on PDF reports, limited sessions per day.
  - [ ] `standard`: Full reports, no watermark.
  - [ ] `enterprise`: Multi-user, custom models, advanced analytics.
  - [ ] Tier check is a simple gate function for now — actual license validation is a future milestone.
- [ ] **Add `AD-20` to `docs/architecture.md`:** Document `BrandConfig`, dual delivery modes, and subscription tier architecture.

---

### v2.5.7 — Chat Session View Rewrite + New Features

**Why here:** UX layer. Depends on v2.5.2 (sessions wired), v2.5.3 (provider abstraction ready). The Chat View is where the user interacts with the analysis — it must showcase the full pipeline.

- [ ] **Fix streaming bubble bug:**
  - [ ] Track `self._current_bot_bubble: Optional[MarkdownLabel]` in View.
  - [ ] On first chunk: spawn one bubble, store reference.
  - [ ] On subsequent chunks: call `_current_bot_bubble.update_text(full_text)` in-place.
  - [ ] Clear reference when `var_is_analyzing` transitions to `False`.
  - [ ] Add `update_text(new_text: str)` method to `MarkdownLabel`: enable → clear → re-insert markdown → disable → recalculate height.
- [ ] **Fix `ChatUser.TFrame/TLabel` colors in `styles.py`:** Solid `ACCENT` blue + `WHITE` text (currently pale `ACCENT_LT`).
- [ ] **Provider selector UI:** Dropdown in chat toolbar to switch the active provider (Gemini, Claude, Groq, Ollama, etc.) on the fly. Calls `DSClinic.set_active_provider(ProviderType)`.
- [ ] **Reanalyze command:** Button or `/reanalyze` command in the chat input that re-runs the initial analysis with an additional user prompt appended to the system instructions.
- [ ] **Report inclusion checkboxes:** Each AI response bubble has a checkbox. Checked responses are included in the final exported PDF report. Unchecked ones are excluded. Stored in `ChatSessionModel.chat_history` with an `include_in_report: bool` flag added to `ChatMessage`.
- [ ] **Auto-scroll:** Scroll to bottom on each new chunk. Disable input area while request is in-flight.

---

### v2.5.8 — pytest Coverage

**Why here:** Now we have a solid, refactored codebase to write tests against. Tests written before the architecture is stable are thrown away.

- [ ] **Setup pytest infrastructure:**
  - [ ] Add `pytest`, `pytest-mock`, `pytest-asyncio` to `pyproject.toml` dev dependencies.
  - [ ] Create `tests/` directory with `conftest.py` and fixture helpers.
- [ ] **PII scrubber tests (`tests/test_anonymization.py`):**
  - [ ] Test that known PII patterns (JMBG, names, phone numbers) are redacted.
  - [ ] Test that clinical values (hemoglobin: 11.2, glucose: 7.8) are NOT redacted (over-anonymization regression test).
  - [ ] Test both Serbian Cyrillic and Latin script inputs.
- [ ] **Medical report parser tests (`tests/test_parsers.py`):**
  - [ ] Test `MedicalReportModel.model_validate_json()` against known good/bad JSON fixtures.
  - [ ] Test `MedicalCriticalFindingModel` field extraction.
- [ ] **Provider abstraction tests (`tests/test_providers.py`):**
  - [ ] Mock `GeminiProvider.analyze()` and `ClaudeProvider.analyze()` — verify `ProviderFactory` routes correctly.
  - [ ] Test `is_available()` returns `False` when keyring key is absent.
  - [ ] Test `ProviderFactory.available_providers()` with mocked keyring.
- [ ] **`AppDatabase` / `JsonCollection` tests (`tests/test_db.py`):**
  - [ ] Test save → load round-trip for `MedicalReport`, `ChatSessionModel`, `PatientRecord`.
  - [ ] Test `list_index()` returns correct index entries without loading full records.
  - [ ] Test `delete()` removes record and updates index.
  - [ ] Test `_rebuild_index_from_disk()` recovers from corrupted index.
- [ ] **`AppSettings` / `load_unified` tests (`tests/test_settings.py`):**
  - [ ] Test `load_unified()` correctly layers `config.json` → `settings.json` overrides.
  - [ ] Test `importlib.metadata` fallback when package is not installed.

---

### v2.5.9 — PII Anonymization Improvements + Debug Panel

**Why here:** Already working (commit `5d5b2f4`). Needs tuning and a debug feature before being considered production-grade. Moving to end so improvements can be driven by test failures from v2.5.8.

- [ ] **Root cause analysis of over-anonymization:**
  - [ ] Identify which Presidio entity types are causing false positives (e.g. lab values being flagged as dates or phone numbers).
  - [ ] Tune `AnalyzerEngine` entity list: disable `DATE_TIME` and `PHONE_NUMBER` globally or add whitelists for clinical value patterns.
  - [ ] Add regex-based allowlist for common lab patterns (e.g. `\d+\.\d+ mmol/L`, `\d+/\d+ mmHg`).
- [ ] **PII Debug Panel (new optional View section):**
  - [ ] Toggle-able debug panel in the main UI (hidden by default, enabled via `app_settings.app_debug_response`).
  - [ ] Shows a side-by-side diff: original text vs anonymized text with highlighted redacted regions.
  - [ ] Lists each detected entity: type, confidence score, matched text snippet, action taken (redacted/kept).
  - [ ] Allows developer to quickly identify false positives without running the full pipeline.
- [ ] **Local model integration stubs for enhanced PII extraction:**
  - [ ] Stub integration point for Llama 3.2 Vision (via Ollama) as a second-pass PII checker for scanned handwritten documents where EasyOCR confidence is low.
  - [ ] MONAI slice extraction stub for DICOM MRI inputs (preprocessing only — actual analysis routes to cloud/MedGemma).
- [ ] **Regression test pass:** Run v2.5.8 PII test suite against improved anonymizer. All tests must pass.

---

### v2.5.10 — README Engineering Case Study + Architecture Diagrams

**Why last:** Can only be written accurately after the architecture is built. This is the portfolio presentation layer — the thing EU recruiters actually read.

- [ ] **`README.md` full rewrite as engineering case study:**
  - [ ] **Problem statement:** What clinical administrative pain does DSClinic solve? Who is the user?
  - [ ] **"MVP to Scale" narrative:** Rapid prototype → real user → enterprise architectural overhaul. The story arc.
  - [ ] **Architecture overview section** with the Split-Horizon diagram (text-based, renders in GitHub).
  - [ ] **GDPR compliance section:** Explain PII scrubbing pipeline, local-first processing, keyring credential management.
  - [ ] **Provider abstraction section:** Explain `LLMProvider` interface, list all 6 providers, explain the factory pattern.
  - [ ] **16GB VRAM optimization section:** Explain quantization, load-on-demand, sequential model switching.
  - [ ] **Multi-brand / white-label section:** Explain `BrandConfig`, dual delivery modes, subscription tiers.
  - [ ] **Technical stack table:** Python, Tkinter/ttk, Pydantic v2, MVVM, PyInstaller, Presidio, keyring, Ollama.
  - [ ] **Interview pitch quote block:** The CV-ready one-liner from the strategy documents.
- [ ] **Architecture diagrams (`docs/diagrams/`):**
  - [ ] Split-Horizon Hybrid Inference pipeline diagram (input → anonymizer → reasoning layer).
  - [ ] MVVM layer diagram (Model / ViewModel / View boundaries).
  - [ ] Provider abstraction class diagram (`LLMProvider` ABC + 6 concrete providers).
  - [ ] Patient data flow diagram (input files → anonymization → AI → report → PDF → DB).
- [ ] **`GEMINI.md` and `docs/architecture.md` final pass:** Ensure both accurately reflect the fully-built v2.5.x architecture.

---

## v2.6.0 — Secure Credential Management & `settings.ini` Elimination ✅ Completed

**All credentials migrated to OS keyring. `settings.ini` permanently deleted. Keys rotated. App verified working.**

### v2.6.1 — `pyproject.toml`: App Name & Version as Single Source of Truth ✅ Completed

- [x] `importlib.metadata.metadata("dsclinic")` reads `app_name` and `app_version` in `load_unified()` as step A0.
- [x] `[APP]` NAME/VERSION block removed from `settings.ini` INI parsing.
- [x] `app_name` and `app_version` added to `exclude_fields` in `save_unified()`.
- [x] `pyproject.toml` is now the single source of truth for both fields.

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

### v2.6.4 — `SettingsViewModel`: Read & Write Credentials via Keyring ✅ Completed

- [x] `var_google_api_key` reads from `get_credential("gemini") or ""`.
- [x] `var_anthropic_api_key = tk.StringVar(value=get_credential("anthropic") or "")` added.
- [x] `var_google_project_id = tk.StringVar(value=get_credential("google_project_id") or "")` added.
- [x] `update_from_config()` refreshes all three from keyring.
- [x] `save_to_config()` writes all three via `set_credential(...)`. Does **not** write via `save_unified()`.
- [x] `app_settings.google_api_key` assignment removed from `save_to_config()`.
- [x] `get_credential`, `set_credential` imported from `models`.

---

### v2.6.5 — Settings UI: Masked Key Entry Fields ✅ Completed

- [x] New `_credential_field(parent, label, var)` helper: masked `ttk.Entry` (`show="*"`) + `SUBTLE`-coloured hint label `"Stored securely in OS keyring — never written to disk."`.
- [x] Three credential fields rendered in `_build_analyze_instructions_panel`: Google API Key, Anthropic API Key, Google Project ID.
- [x] Old plain `_entry_field("Google API Key", ...)` call replaced.
- [x] `_HEIGHT` bumped from 760 to 860px to accommodate the additional fields.

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

## v2.4.0 — Unified Configuration, MVVM Schema & High-Privacy Alignment ✅ Completed

### Completed

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

### Completed

- [x] Centered section headers in main panel: `anchor="center"` on card titles in `_card` factory.
- [x] Settings window layout restructuring: Reworked `_build_general_section`, created `_build_support_section`.
- [x] Resolved nested-tuple serialization bug on multiple settings saves.
- [x] Token-optimized prompt transmission: Automatic newline/whitespace cleaning before Gemini API calls.
