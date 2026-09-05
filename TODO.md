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

- [ ] Split-Horizon Hybrid Inference pipeline diagram.
- [ ] MVVM layer diagram.
- [ ] `LLMProvider` class diagram.
- [ ] Patient data flow diagram.

---

### v2.15.3 — Final Doc Pass

- [ ] `GEMINI.md` final review.
- [ ] `docs/architecture.md` final cross-reference pass.
- [ ] `docs/session_handoff.md` final entry: mark project as portfolio-complete.

---

## v2.14.0 — PII Anonymization Improvements + Debug Panel 🔍 Planned

---

### v2.14.1 — Root Cause Analysis & Presidio Tuning

- [ ] Identify Presidio entity types causing false positives on clinical values.
- [ ] Tune `AnalyzerEngine` entity list and add allowlists.
- [ ] Run v2.13.2 test suite — all tests must pass before proceeding.

---

### v2.14.2 — PII Debug Panel (View)

- [ ] Toggle-able debug panel (hidden by default; enabled when `app_settings.app_debug_response` is `True`).
- [ ] Side-by-side diff of original vs anonymized text with entity list.
- [ ] Export debug report to `logs/pii_debug_{timestamp}.json`.

---

### v2.14.3 — Local Model Integration Stubs

- [ ] Llama 3.2 Vision second-pass PII checker stub.
- [ ] MONAI slice extraction stub for DICOM inputs.

---

## v2.13.0 — pytest Coverage 🧪 Planned

---

### v2.13.1 — pytest Infrastructure

- [ ] Add `pytest-asyncio`; create `tests/` with `conftest.py`.

---

### v2.13.2 — PII Scrubber Tests

- [ ] PII redaction tests; over-anonymization regression tests; Serbian Cyrillic/Latin.

---

### v2.13.3 — Medical Report Parser Tests

- [ ] `MedicalReportModel.model_validate_json()` tests.

---

### v2.13.4 — Provider Abstraction Tests

- [ ] `ProviderFactory`, `GeminiProvider`, `ClaudeProvider`, `OpenAICompatibleProvider`, `OllamaProvider` tests.

---

### v2.13.5 — `AppDatabase` / `JsonCollection` Tests

- [ ] Save/load/delete/rebuild round-trip tests.

---

### v2.13.6 — `AppSettings` / `load_unified` Tests

- [ ] Layered config, `BrandConfig` fallback tests.

---

## v2.12.0 — Chat Session View Rewrite + New Features 💬 Planned

---

### v2.12.3 — Reanalyze Command & Additional Prompt Input ✅ Completed

- [x] Add "Reanalyze" button in chat toolbar.
- [x] Reanalyze re-runs the initial analysis with an additional user prompt appended to system instructions.
- [x] Additional prompt entry field: `ttk.Entry` above the send button, pre-populated with current task description.
- [x] Reanalyze result spawns a new bubble with `[Reanalysis]` prefix label.

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

### v2.12.4 — Report Inclusion Checkboxes

- [ ] Add `include_in_report: bool = True` field to `ChatMessage` model in `src/models/ai.py`.
- [ ] Each bot response bubble has a checkbox (default checked).
- [ ] Unchecked responses are excluded from the final PDF export.
- [ ] `ChatSessionModel.chat_history` stores the updated `include_in_report` flag per message.
- [ ] `write_report_pdf()` filters `chat_responses` by `include_in_report` before rendering.

---

## v2.11.0 — Enterprise Multi-Brand / White-Label & Subscription Config 🏢 ✅ Completed

---

### v2.11.5 — Subscription Tier Enforcement Stubs ✅ Completed

- [x] `trial`: watermark + daily session limit. `standard`: no limits. `enterprise`: stub in ProviderFactory.

---

### v2.11.4 — Clinic Profile Settings Section ✅ Completed

- [x] "Clinic Profile" card; logo picker; `brand_config.save()` on save.

---

### v2.11.3 — Dynamic GUI Branding ✅ Completed

- [x] Window title + toolbar branding from `brand_config`.

---

### v2.11.2 — Dynamic PDF Report Branding ✅ Completed

- [x] `pdf_maker.py` fully branded; trial watermark; logo optional.

---

### v2.11.1 — `BrandConfig` Model & Loader ✅ Completed

- [x] `BrandConfig`, `brand_config` singleton, `brand.json`.

---

## v2.10.0 — Local Ollama Provider (16GB VRAM Optimized) 🖥️ ✅ Completed

---

### v2.10.4 ✅ — v2.10.3 ✅ — v2.10.2 ✅ — v2.10.1 ✅

- [x] `OllamaProvider` fully implemented; VRAM guard; config infra.

---

## v2.9.0 — Groq + Together AI + HuggingFace Cloud Providers ☁️ ✅ Completed

---

### v2.9.4 ✅ — v2.9.3 ✅ — v2.9.2 ✅ — v2.9.1 ✅

- [x] All three providers implemented; `OpenAICompatibleProvider` base; credential infra.

---

## v2.8.0 — `src/providers/` LLMProvider Abstraction ✅ Completed

---

### v2.8.4 ✅ — v2.8.3 ✅ — v2.8.2 ✅ — v2.8.1 ✅

- [x] `LLMProvider` ABC; `ProviderFactory`; `GeminiProvider`; `ClaudeProvider`; `dsclinic.py` refactored.

---

## v2.7.0 — Patient Record as First-Class Entity & Session Persistence ✅ Completed

---

### v2.7.4 ✅ — v2.7.3 ✅ — v2.7.2 ✅ — v2.7.1 ✅

- [x] `PatientRecord`; `AppDatabase`; session/patient sidebars; `_persist_report()`; `_persist_session()`.

---

## v2.6.0 — Secure Credential Management & `settings.ini` Elimination ✅ Completed

### v2.6.7 ✅ — v2.6.6 ✅ — v2.6.5 ✅ — v2.6.4 ✅ — v2.6.3 ✅ — v2.6.2 ✅ — v2.6.1 ✅

- [x] Keys rotated; `settings.ini` deleted; OS keyring; `keyring_manager.py`.

---

## v2.5.0 — MVVM Strict Compliance & Defensive Error Handling Audit ✅ Completed

### v2.5.4 ✅ — v2.5.3 ✅ — v2.5.2 ✅ — v2.5.1 ✅

- [x] `pyproject.toml` + `uv` migration; mypy strict 0 errors; error handling audit; MVVM boundary audit.

---

## v2.4.0 — Unified Configuration ✅ Completed

- [x] `src/models/` package; `AppSettings`; unified `load_unified` / `save_unified`.

---

## v2.1.10 — UI & Layout Refinement ✅ Completed

- [x] Centered headers; nested-tuple serialization fix; token-optimization filters.
