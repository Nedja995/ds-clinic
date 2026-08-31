# DSClinic — Master Session Handoff & AI Entry Point

Read this before starting any work. It captures everything needed to continue development without going through previous chat history.

---

> [!IMPORTANT]
> **CRITICAL AI SYSTEM DIRECTIVES (MANDATORY):**
> Before writing, proposing, or refactoring any code for this session, you MUST read, cross-reference, and strictly adhere to **Section 3.G (AI Coding Assistant System Directives)** inside `GEMINI.md`.
> Skipping this step or breaking its core principles (Defensive Error Handling, Absolute GDPR Privacy/Anonymization, strict MVVM decoupled boundaries, and complete Type Hinting) will result in a failed session task.

---

# Session Handoff

Read this before starting any work. It captures everything needed to continue development without going through previous chat history.
This handoff is prepared to allow any incoming development AI assistant (including Gemini CLI and Claude) to immediately continue development.

> [!IMPORTANT]
> **Handoff & TODO Update Rule (GASSI Standard):** On *every single code modification or task completion*, the active AI assistant MUST immediately update **all applicable dev docs** and `docs/session_handoff.md`. Skipping any applicable file without explicit reason is an error.

---

## Key Docs — Read On Demand, Not Upfront

- `TODO.md` — only if planning the next milestone or checking roadmap ordering
- `CHANGELOG.md` — only if debugging a regression or checking what changed in a specific version
- `docs/architecture.md` — **AD-18, AD-19, AD-20 added in this session** — read before v2.5.2, v2.5.3, v2.5.6 work
- `GEMINI.md` — DSClinic Development Guidelines & Project Context
- `.dev_profile/developer_profile.md` — standing workflow rules and commit discipline

**Source files:** read only the specific files the task touches. Never edit from memory.

---

## AI Coding Assistant System Directives (Strict Execution Rules)

Every AI assistant (Claude/Gemini) handling a programming task for DSClinic must implicitly wrap all code generation under these strict engineering rules:

1. **Defensive Error Handling (Desktop Resiliency):**
   - **No Bare Excepts:** Python code must never use `except:`. Always catch specific exceptions.
   - **Graceful Failure UI:** Operations failing in background threads must write structured error payloads to the queue.
   - **File & Network I/O Protection:** Wrap all `src/db/`, keyring, and API calls in explicit `try/except/finally` with logging.
   - **No raise on missing API key at init time:** Both clients log warning + early return. `RuntimeError` raised at call time only.

2. **Absolute Privacy Enforcement (GDPR Alignment):**
   - **PII Leakage Prevention:** All patient inputs pass through Presidio/spaCy before external transmission.
   - **Key Protection:** Only `keyring_manager.py`. Never hardcode or read from files. `settings.ini` no longer exists.

3. **MVVM Integrity & Typing Rules:**
   - **Zero UI Imports in Logic:** No `tkinter`/`ttk` imports in `src/models/`, `src/db/`, or any ViewModel.
   - **Strict Type Hinting:** All new functions must include complete Python type annotations.

4. **Multi-Brand Code Decoupling:**
   - Never hardcode clinic names, logos, or branding in layout code.
   - All identity and commercial config flows through `BrandConfig` (v2.5.6).

---

## Version & Commit Discipline (GASSI Standard — mandatory for every sub-version)

Every sub-version is one commit. Code + all applicable docs travel together.

```bash
git add <exact files changed in this task>
git commit -m "vX.Y.Z: <imperative short description>"
git push
```

The AI assistant provides the exact `git add` command with real filenames **at the end of every completed task**. Never pre-written in advance.

### Mandatory doc checklist — verify every one before committing:

| File | Update | When |
|---|---|---|
| `CHANGELOG.md` | New `## [X.Y.Z]` entry | Every sub-version |
| `TODO.md` | Mark completed tasks `[x]` | Every sub-version |
| `pyproject.toml` | Bump `version = "X.Y.Z"` | Every sub-version |
| `docs/session_handoff.md` | Advance current status to next sub-version | Every sub-version |
| `docs/architecture.md` | Add `AD-XX` for any design/structural decision | Any time a design choice is made |
| `GEMINI.md` | Update project-wide architectural or workflow rules | Any time project-wide rules change |
| `.dev_profile/developer_profile.md` | Update standing workflow conventions | Any time a standing rule is added or changed |

### TODO Archiving Rule
**Completed versions are never collapsed or summarised.** Full task lists stay expanded with `[x]` checkboxes indefinitely.

### File Edit Discipline
Never use `str_replace` on dev docs. Always use `write_file` with the complete file content.

Full rule reference: `.dev_profile/developer_profile.md` § 5.

---

## Current Status: v2.5.0 Active — Next sub-version: v2.5.1

**v2.6.0 fully complete.** v2.5.0 plan finalised this session. All 10 sub-versions planned and documented in `TODO.md`. AD-18 (PatientRecord), AD-19 (LLMProvider abstraction), AD-20 (BrandConfig / dual delivery) added to `docs/architecture.md`.

**Active milestone:** v2.5.0 — Enterprise MedTech Platform: Core Architecture & Feature Pipeline.

---

## v2.5.0 Sub-version Map

| Sub-version | Scope | Priority rationale |
|---|---|---|
| v2.5.1 | MVVM strict compliance + defensive error handling audit | Foundation — everything built on top must be correct |
| v2.5.2 | PatientRecord model + AppDatabase wired to ViewModel + session persistence UI | Data foundation all other features depend on |
| v2.5.3 | `src/providers/` LLMProvider abstraction — Gemini + Claude | Core architectural showpiece |
| v2.5.4 | Groq + Together AI + HuggingFace cloud providers | Extends v2.5.3 |
| v2.5.5 | Local Ollama provider — 16GB VRAM optimized, load-on-demand | Most complex provider |
| v2.5.6 | BrandConfig + white-label + subscription tier | Enterprise commercial layer |
| v2.5.7 | Chat Session View rewrite + new features (reanalyze, checkboxes, provider selector) | UX — depends on sessions + providers |
| v2.5.8 | pytest coverage | Quality gate — tests solid codebase |
| v2.5.9 | PII anonymization improvements + debug panel | Polish — driven by test failures |
| v2.5.10 | README engineering case study + architecture diagrams | Portfolio presentation layer |

---

## Key Existing Code to Read Before v2.5.1

- `src/dsclinic_gui/report_view_models.py` — main ViewModel, check for MVVM violations
- `src/dsclinic_gui/settings/settings_view_model.py` — settings ViewModel
- `src/dsclinic.py` — business logic layer
- `src/db/app_database.py` — already complete, not yet wired
- `src/db/json_collection.py` — generic collection engine
- `src/models/ai.py` — `ChatSessionModel`, `GeminiModelConfig`, `ClaudeModelConfig`
- `src/models/patient.py` — `MedicalReport`, `MedicalReportModel`, `PatientRecord` (to be added in v2.5.2)

---

## PII Anonymization — Already Implemented

Commit `5d5b2f4` (Gemini CLI). Working but over-anonymizes clinical numeric values. Improvement + debug panel planned in v2.5.9, driven by pytest failures from v2.5.8.

---

## Previously Active Milestone: v2.6.0 ✅ Complete

All credentials migrated to OS keyring. `settings.ini` permanently deleted. Keys rotated and verified.
