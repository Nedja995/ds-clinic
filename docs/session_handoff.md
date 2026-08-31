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
- `docs/architecture.md` — AD-01 through AD-20. Read before any design decision. **AD-18 (PatientRecord), AD-19 (LLMProvider), AD-20 (BrandConfig) added this session.**
- `GEMINI.md` — DSClinic Development Guidelines & Project Context
- `.dev_profile/developer_profile.md` — standing workflow rules and commit discipline

**Source files:** read only the specific files the task touches. Never edit from memory.

---

## AI Coding Assistant System Directives (Strict Execution Rules)

1. **Defensive Error Handling:** No bare `except:`. All background thread failures write structured `TaskStatus.FAILED` queue payloads. All `src/db/`, keyring, and API calls wrapped in `try/except/finally` with logging. No `raise` at client `__init__` time — warn + return early, raise `RuntimeError` at call time only.
2. **Absolute Privacy (GDPR):** All patient inputs through Presidio/spaCy before external transmission. Only `keyring_manager.py` for credentials. `settings.ini` no longer exists.
3. **MVVM Integrity:** Zero `tkinter`/`ttk` widget imports in `src/models/`, `src/db/`, or any ViewModel. Complete type annotations on all new functions.
4. **Multi-Brand Decoupling:** All identity and commercial config through `BrandConfig` (v2.11.0). Never hardcode clinic names or logos in layout code.

---

## Version & Commit Discipline (GASSI Standard)

```bash
git add <exact files changed in this task>
git commit -m "vX.Y.Z: <imperative short description>"
git push
```

Exact `git add` command provided at end of every completed task. Never pre-written.

### Mandatory doc checklist:

| File | Update | When |
|---|---|---|
| `CHANGELOG.md` | New `## [X.Y.Z]` entry | Every sub-version |
| `TODO.md` | Mark completed tasks `[x]` | Every sub-version |
| `pyproject.toml` | Bump `version = "X.Y.Z"` | Every sub-version |
| `docs/session_handoff.md` | Advance current status | Every sub-version |
| `docs/architecture.md` | Add `AD-XX` for design decisions | Any time a design choice is made |
| `GEMINI.md` | Update project-wide rules | Any time project-wide rules change |
| `.dev_profile/developer_profile.md` | Update workflow conventions | Any time a standing rule changes |

**TODO Archiving Rule:** Completed versions never collapsed. Full task lists stay expanded with `[x]` checkboxes indefinitely.

**File Edit Discipline:** Never use `str_replace` on dev docs. Always `write_file` with complete file content.

Full rule reference: `.dev_profile/developer_profile.md` § 5.

---

## Current Status: v2.5.0 Active — Next sub-version: v2.5.1

**Roadmap restructured this session:** Each major feature is now its own MINOR version with PATCH sub-versions.

| Version | Scope | Status |
|---|---|---|
| v2.5.0 | MVVM strict compliance + defensive error handling audit | ▶ Active |
| v2.7.0 | Patient records + session persistence | Planned |
| v2.8.0 | `src/providers/` LLMProvider abstraction | Planned |
| v2.9.0 | Groq + Together + HuggingFace providers | Planned |
| v2.10.0 | Local Ollama provider | Planned |
| v2.11.0 | BrandConfig + white-label + subscription | Planned |
| v2.12.0 | Chat Session View rewrite + new features | Planned |
| v2.13.0 | pytest coverage | Planned |
| v2.14.0 | PII improvements + debug panel | Planned |
| v2.15.0 | README case study + architecture diagrams | Planned |

---

## v2.5.0 Implementation Notes

Files most likely to contain MVVM violations and type hint gaps:
- `src/dsclinic_gui/report_view_models.py` — main ViewModel, check for any widget imports or dialog calls
- `src/dsclinic_gui/settings/settings_view_model.py` — settings ViewModel
- `src/dsclinic.py` — business logic, check return type annotations

Files to check for bare `except:` and missing I/O guards:
- `src/db/json_collection.py` — all file reads/writes
- `src/db/app_database.py` — collection init
- `src/models/keyring_manager.py` — keyring calls
- `src/api_gemini/client.py`, `src/api_claude/client.py` — API calls

---

## Key Existing Code Context for Upcoming Milestones

- **`src/db/app_database.py`** — fully implemented, never wired to any ViewModel (v2.7.0)
- **`src/db/json_collection.py`** — generic `JsonCollection[T]` engine, complete
- **`src/models/ai.py`** — `ChatSessionModel`, `GeminiModelConfig`, `ClaudeModelConfig` exist
- **`src/models/patient.py`** — `MedicalReport` exists; `PatientRecord` to be added in v2.7.1
- **PII anonymization** — implemented in commit `5d5b2f4`, working, over-anonymizes clinical values. Improvement in v2.14.0 driven by v2.13.2 test failures.

---

## Previously Completed: v2.6.0 ✅

All credentials migrated to OS keyring. `settings.ini` permanently deleted. Keys rotated and verified working.
