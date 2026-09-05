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
- [ ] Test `OpenAICompatibleProvider.analyze()` with mocked `openai.OpenAI` client — verify JSON strip, `model_validate_json`, and `RuntimeError` on parse failure.
- [ ] Test `OpenAICompatibleProvider.ask()` streaming: verify chunks yielded and history appended after exhaustion.
- [ ] Test `OllamaProvider.is_available()` returns `False` when daemon not reachable (mocked `ollama.Client.list()` raising).
- [ ] Test `OllamaProvider._ensure_model_loaded()` calls `pull()` when model absent from `list()` response.

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

### v2.12.2 — Style Fixes & Provider Selector ✅ Completed

- [x] Fix `ChatUser.TFrame/TLabel` colors in `styles.py`: solid `ACCENT` blue + `WHITE` text (currently pale `ACCENT_LT`).
- [x] Add provider selector dropdown in chat toolbar: lists `ProviderFactory.available_providers()`.
- [x] Selecting a provider calls `DSClinic.set_active_provider(ProviderType)` immediately.
- [x] Disable input area while `var_is_analyzing` is `True`; show loading indicator.

---

### v2.12.1 — Streaming Bubble Fix & `MarkdownLabel.update_text()` ✅ Completed

- [x] Add `update_text(new_text: str)` method to `MarkdownLabel`: enable widget → clear → re-insert markdown → disable → recalculate height.
- [x] Track `self._current_bot_bubble: Optional[MarkdownLabel]` in `ChatSessionView`.
- [x] On first chunk: spawn one bubble, store reference. On subsequent chunks: call `_current_bot_bubble.update_text(full_text)` in-place.
- [x] Clear reference when `var_is_analyzing` transitions `True → False`.
- [x] Auto-scroll to bottom on each chunk update.

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

## v2.11.0 — Enterprise Multi-Brand / White-Label & Subscription Config 🏢 ✅ Completed

**BrandConfig model, brand.json, dynamic PDF branding, dynamic GUI branding, Clinic Profile settings section, and subscription tier enforcement all complete.**

---

### v2.11.5 — Subscription Tier Enforcement Stubs ✅ Completed

- [x] `trial`: PDF watermark active (v2.11.2). Daily session limit enforced in `_start_analysis()` via `is_feature_allowed("unlimited_sessions")` — blocks analysis with upgrade prompt when count ≥ `_TRIAL_DAILY_LIMIT` (3).
- [x] `standard`: No watermark, unlimited sessions — `is_feature_allowed("unlimited_sessions")` returns `True`, gate skipped.
- [x] `enterprise`: Stub in `ProviderFactory.available_providers()` — logs `DEBUG` message when `is_feature_allowed("custom_models")` is `True`.
- [x] Tier check implemented via the existing `is_feature_allowed(feature: str) -> bool` gate in `BrandConfig` (v2.11.1).

---

### v2.11.4 — Clinic Profile Settings Section ✅ Completed

- [x] New "Clinic Profile" card in `settings_view.py` — placed first in the scroll area.
- [x] Entry fields: Clinic Name, Subtitle, Address, Report Header Text, Report Footer Text.
- [x] Logo file picker: readonly `ttk.Entry` (path display) + "Browse…" button; `_on_logo_pick()` opens `filedialog.askopenfilename` in the View; ViewModel holds path `tk.StringVar` only.
- [x] Save writes all clinic profile fields to `brand_config` singleton then calls `brand_config.save()` — atomic write to `brand.json`.
- [x] Subscription tier display (read-only `ttk.Label` bound to `var_subscription_tier`).
- [x] `_HEIGHT` bumped to 1380 px.

---

### v2.11.3 — Dynamic GUI Branding ✅ Completed

- [x] Window title = `brand_config.clinic_name`.
- [x] Toolbar header label = `brand_config.clinic_name` + `brand_config.clinic_subtitle` (condensed `·`-separated, right side of toolbar).
- [x] Logo image shown in toolbar if `brand_config.resolved_logo_path()` returns a valid path — resized to 22×22 px; `PhotoImage` reference stored on `self` to prevent GC; skipped gracefully on error.

---

### v2.11.2 — Dynamic PDF Report Branding ✅ Completed

- [x] `pdf_maker.py` reads `brand_config` at generation time for logo, clinic name, header/footer text.
- [x] Logo path resolved relative to executable directory (AD-09).
- [x] PDF color scheme driven by `brand_config.primary_color` (header text) and `brand_config.secondary_color` (table fills).
- [x] Trial tier: diagonal `"TRIAL"` watermark stamped on every page via `draw_watermark()` when `is_feature_allowed("no_watermark")` is `False`.
- [x] `LOGO_PATH` module constant removed — logo is now optional, not fatal on missing file.
- [x] Optional `report_header_text` subtitle line rendered below clinic name when non-empty.

---

### v2.11.1 — `BrandConfig` Model & Loader (`src/models/brand.py`) ✅ Completed

- [x] Define `BrandConfig(BaseModel)` with all brand/subscription fields.
- [x] Load from `brand.json`; fall back to defaults if absent.
- [x] `BrandConfig.save()`, `resolved_logo_path()`, `is_feature_allowed()`, color helpers.
- [x] `brand_config` singleton exported from `src/models/__init__.py`.
- [x] `brand.json` default file at project root.

---

## v2.10.0 — Local Ollama Provider (16GB VRAM Optimized) 🖥️ ✅ Completed

---

### v2.10.4 — Register Ollama in `ProviderFactory` ✅ Completed

- [x] `ProviderFactory.create()` constructs `OllamaProvider`.
- [x] `NotImplementedError` catch removed (all six providers implemented).

---

### v2.10.3 — Load-on-Demand & VRAM Sequential Guard ✅ Completed

- [x] Model pulled on first use; previous model unloaded before loading new one.
- [x] 4-bit quantization via Ollama model name tag.

---

### v2.10.2 — `OllamaProvider` Core Implementation ✅ Completed

- [x] `OllamaProvider(LLMProvider)` — `is_available()`, `analyze()`, `ask()`.

---

### v2.10.1 — Ollama Infrastructure & Config ✅ Completed

- [x] `ollama` SDK optional extra; `AppSettings` fields; Settings UI "Local AI" card.

---

## v2.9.0 — Groq + Together AI + HuggingFace Cloud Providers ☁️ ✅ Completed

---

### v2.9.4 — Register New Providers in `ProviderFactory` ✅ Completed

- [x] Groq, Together, HuggingFace stubs replaced with lazy imports.

---

### v2.9.3 — `GroqProvider`, `TogetherProvider`, `HuggingFaceProvider` ✅ Completed

- [x] All three implemented as `OpenAICompatibleProvider` subclasses.

---

### v2.9.2 — `OpenAICompatibleProvider` Base Class ✅ Completed

- [x] Shared base for all OpenAI-compatible `/v1/chat/completions` backends.

---

### v2.9.1 — Credential & Config Infrastructure ✅ Completed

- [x] Keyring keys, SettingsViewModel vars, Settings UI fields, config.json, AppSettings.
- [x] `ProviderRequest.context: str` field (AD-12).

---

## v2.8.0 — `src/providers/` LLMProvider Abstraction (Gemini + Claude) ✅ Completed

---

### v2.8.4 — Refactor `DSClinic` to Use `ProviderFactory` ✅ Completed

- [x] `active_provider: LLMProvider | None`; `set_active_provider()`; all AI calls via provider interface.

---

### v2.8.3 — `ProviderFactory` ✅ Completed

- [x] `create()` and `available_providers()` static methods.

---

### v2.8.2 — `GeminiProvider` & `ClaudeProvider` ✅ Completed

- [x] Both delegate to existing SDK clients; startup-guard contract.

---

### v2.8.1 — `LLMProvider` Abstract Base & Data Contracts ✅ Completed

- [x] `src/providers/` package; `ProviderType`, `ProviderRequest`, `ProviderResponse`, `LLMProvider(ABC)`.

---

## v2.7.0 — Patient Record as First-Class Entity & Session Persistence ✅ Completed

---

### v2.7.4 — Patient List Panel ✅ Completed

- [x] Two-tab Notebook sidebar; patient filter; "New Patient" form.

---

### v2.7.3 — Session History Panel ✅ Completed

- [x] `SessionHistoryView`; session index observable; `load_session()`; `new_session()`.

---

### v2.7.2 — Wire `AppDatabase` into `DSClinicViewModel` ✅ Completed

- [x] `_persist_report()`, `_persist_session()` wired.

---

### v2.7.1 — `PatientRecord` Model & `AppDatabase` Extension ✅ Completed

- [x] `PatientRecord`; `patients` collection in `AppDatabase`.

---

## v2.6.0 — Secure Credential Management & `settings.ini` Elimination ✅ Completed

### v2.6.7 — Rotate Keys, Delete `settings.ini`, Final Cleanup ✅ Completed

- [x] Keys rotated; `settings.ini` deleted; app verified.

---

### v2.6.6 — Runtime Key Consumption ✅ Completed

- [x] `ClaudeAnalyzerClient` wired; startup guards on both clients.

---

### v2.6.5 — Settings UI: Masked Key Entry Fields ✅ Completed

- [x] `_credential_field()` helper; three credential fields.

---

### v2.6.4 — `SettingsViewModel`: Keyring Read/Write ✅ Completed

- [x] Three credential `tk.StringVar` vars; read from keyring; write via `set_credential()`.

---

### v2.6.3 — `AppSettings`: Remove All Secret Fields ✅ Completed

- [x] `google_api_key`, `anthropic_api_key` removed; `configparser` removed.

---

### v2.6.2 — `keyring_manager.py` ✅ Completed

- [x] `get_credential()`, `set_credential()`, `delete_credential()`.

---

### v2.6.1 — `pyproject.toml` as Single Source of Truth ✅ Completed

- [x] `importlib.metadata` for `app_name`/`app_version`.

---

## v2.5.0 — MVVM Strict Compliance & Defensive Error Handling Audit ✅ Completed

### v2.5.4 — `pyproject.toml` + `uv` Migration & README Rewrite ✅ Completed

- [x] Full `pyproject.toml` migration; `README.md` rewrite; `mypy.ini` deleted.

---

### v2.5.3 — Type Hints Audit (`mypy --strict`) ✅ Completed

- [x] 0 errors across 26 checked files.

---

### v2.5.2 — Defensive Error Handling Audit ✅ Completed

- [x] All bare `except:` eliminated; all I/O wrapped; all thread failures → `TaskStatus.FAILED`.

---

### v2.5.1 — MVVM Boundary Audit ✅ Completed

- [x] Zero tkinter imports in ViewModels; delegate pattern enforced.

---

## v2.4.0 — Unified Configuration, MVVM Schema & High-Privacy Alignment ✅ Completed

- [x] `src/models/` package; `AppSettings`; unified `load_unified` / `save_unified`.

---

## v2.1.10 — UI & Layout Refinement ✅ Completed

- [x] Centered section headers; nested-tuple serialization fix; token-optimization filters.
