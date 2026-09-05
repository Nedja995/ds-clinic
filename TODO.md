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

---

### v2.15.1 — `README.md` Full Rewrite

- [ ] Problem statement, "MVP to Scale" narrative, architecture overview, GDPR section, provider abstraction, VRAM optimization, multi-brand, tech stack, CV pitch block.

---

### v2.15.2 — Architecture Diagrams (`docs/diagrams/`)

- [ ] Split-Horizon pipeline, MVVM layer, `LLMProvider` class, patient data flow diagrams.

---

### v2.15.3 — Final Doc Pass

- [ ] `GEMINI.md`, `docs/architecture.md`, `docs/session_handoff.md` final reviews.

---

## v2.14.0 — PII Anonymization Improvements + Debug Panel 🔍 Planned

---

### v2.14.1 — Root Cause Analysis & Presidio Tuning

- [ ] Identify false-positive entity types; tune `AnalyzerEngine`; add lab value and Serbian allowlists.

---

### v2.14.2 — PII Debug Panel (View)

- [ ] Toggle-able side-by-side diff panel; entity list; debug report export.

---

### v2.14.3 — Local Model Integration Stubs

- [ ] Llama 3.2 Vision second-pass PII checker stub; MONAI DICOM slice stub.

---

## v2.13.0 — pytest Coverage 🧪 Planned

---

### v2.13.1 — pytest Infrastructure

- [ ] Add `pytest-asyncio`; create `tests/conftest.py`.

---

### v2.13.2 — PII Scrubber Tests

- [ ] PII redaction, over-anonymization regression, Cyrillic/Latin, PDF redaction tests.

---

### v2.13.3 — Medical Report Parser Tests

- [ ] `MedicalReportModel.model_validate_json()` good/bad fixtures; empty report defaults.

---

### v2.13.4 — Provider Abstraction Tests

- [ ] `ProviderFactory`, all six providers, `DSClinic.set_active_provider()`, streaming.

---

### v2.13.5 — `AppDatabase` / `JsonCollection` Tests

- [ ] Save/load/delete/rebuild round-trip; `list_index()`; `count()`.

---

### v2.13.6 — `AppSettings` / `load_unified` Tests

- [ ] Layered config; `PackageNotFoundError` fallback; `BrandConfig` fallback.

---

## v2.12.0 — Chat Session View Rewrite + New Features 💬 ✅ Completed

**v2.12.1–v2.12.4 all complete.**

---

### v2.12.4 — Report Inclusion Checkboxes ✅ Completed

- [x] Add `include_in_report: bool = True` field to `ChatMessage` model in `src/models/ai.py`.
- [x] Each bot response bubble has a checkbox (default checked).
- [x] Unchecked responses are excluded from the final PDF export.
- [x] `ChatSessionModel.chat_history` stores the updated `include_in_report` flag per message.
- [x] `_rebuild_chat_responses()` filters `chat_history` bot turns by `include_in_report` to build `_model.chat_responses`.

---

### v2.12.3 — Reanalyze Command & Additional Prompt Input ✅ Completed

- [x] Add "Reanalyze" button in chat toolbar.
- [x] Reanalyze re-runs the initial analysis with an additional user prompt appended to system instructions.
- [x] Additional prompt entry field: `ttk.Entry` above the send button, pre-populated with current task description.
- [x] Reanalyze result spawns a new bubble with `[Reanalysis]` prefix label.

---

### v2.12.2 — Style Fixes & Provider Selector ✅ Completed

- [x] Fix `ChatUser.TFrame/TLabel` colors in `styles.py`: solid `ACCENT` blue + `WHITE` text.
- [x] Add provider selector dropdown in chat toolbar: lists `ProviderFactory.available_providers()`.
- [x] Selecting a provider calls `DSClinic.set_active_provider(ProviderType)` immediately.
- [x] Disable input area while `var_is_analyzing` is `True`.

---

### v2.12.1 — Streaming Bubble Fix & `MarkdownLabel.update_text()` ✅ Completed

- [x] `update_text(new_text: str)` added to `MarkdownLabel`.
- [x] `_current_bot_bubble: Optional[MarkdownLabel]` tracked in `ChatSessionView`.
- [x] First chunk spawns bubble; subsequent chunks call `update_text()` in-place.
- [x] Reference cleared when `var_is_analyzing` → `False`.
- [x] Auto-scroll to bottom on each chunk.

---

## v2.11.0 — Enterprise Multi-Brand / White-Label & Subscription Config 🏢 ✅ Completed

---

### v2.11.5 ✅ — v2.11.4 ✅ — v2.11.3 ✅ — v2.11.2 ✅ — v2.11.1 ✅

- [x] `BrandConfig`, `brand.json`, dynamic PDF/GUI branding, Clinic Profile settings, tier enforcement.

---

## v2.10.0 — Local Ollama Provider (16GB VRAM Optimized) 🖥️ ✅ Completed

### v2.10.4 ✅ — v2.10.3 ✅ — v2.10.2 ✅ — v2.10.1 ✅

- [x] `OllamaProvider` fully implemented; VRAM guard; config infra.

---

## v2.9.0 — Groq + Together AI + HuggingFace Cloud Providers ☁️ ✅ Completed

### v2.9.4 ✅ — v2.9.3 ✅ — v2.9.2 ✅ — v2.9.1 ✅

- [x] All three providers; `OpenAICompatibleProvider` base; credential infra.

---

## v2.8.0 — `src/providers/` LLMProvider Abstraction ✅ Completed

### v2.8.4 ✅ — v2.8.3 ✅ — v2.8.2 ✅ — v2.8.1 ✅

- [x] `LLMProvider` ABC; `ProviderFactory`; `GeminiProvider`; `ClaudeProvider`; `dsclinic.py` refactored.

---

## v2.7.0 — Patient Record as First-Class Entity & Session Persistence ✅ Completed

### v2.7.4 ✅ — v2.7.3 ✅ — v2.7.2 ✅ — v2.7.1 ✅

- [x] `PatientRecord`; `AppDatabase`; sidebars; persistence.

---

## v2.6.0 — Secure Credential Management & `settings.ini` Elimination ✅ Completed

### v2.6.7 ✅ through v2.6.1 ✅

- [x] Keys rotated; `settings.ini` deleted; OS keyring; `keyring_manager.py`.

---

## v2.5.0 — MVVM Strict Compliance & Defensive Error Handling Audit ✅ Completed

### v2.5.4 ✅ — v2.5.3 ✅ — v2.5.2 ✅ — v2.5.1 ✅

- [x] `pyproject.toml` + `uv` migration; mypy strict 0 errors; error handling; MVVM audit.

---

## v2.4.0 — Unified Configuration ✅ Completed

- [x] `src/models/` package; `AppSettings`; unified `load_unified` / `save_unified`.

---

## v2.1.10 — UI & Layout Refinement ✅ Completed

- [x] Centered headers; nested-tuple serialization fix; token-optimization filters.
