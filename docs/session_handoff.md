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

**Read all these at session start**
This handoff doc is designed to be self-contained for starting work.

- `TODO.md` — only if planning the next milestone or checking roadmap ordering
- `CHANGELOG.md` — only if debugging a regression or checking what changed in a specific version
- `docs/architecture.md` — only if making a non-obvious design decision (check if an AD already covers it). **Last updated by developer: AD-12 through AD-17 added covering hybrid inference, VRAM constraints, multimodal preprocessing, PII pipeline, defensive threading, and pytest strategy.**
- `GEMINI.md` — DSClinic Development Guidelines & Project Context
- `.dev_profile/developer_profile.md` — standing workflow rules and commit discipline

**Source files:** read only the specific files the task touches. Never edit from memory.

---

## AI Coding Assistant System Directives (Strict Execution Rules)

Every AI assistant (Claude/Gemini) handling a programming task for DSClinic must implicitly wrap all code generation under these strict engineering rules:

1. **Defensive Error Handling (Desktop Resiliency):**
   - **No Bare Excepts:** Python code must never use `except:`. Always catch specific exceptions (e.g., `except FileNotFoundError`, `except APIError`).
   - **Graceful Failure UI:** If an operation fails in a background thread or service, it must write a structured error payload to the communication queue. The main thread must handle this to prevent app hangs or silent failures.
   - **File & Network I/O Protection:** Wrap all local file database accesses (`src/db/`), OS keyring interactions, and remote API calls in explicit `try...except...finally` blocks with logging.
   - **No raise on missing API key at init time:** Both `MedicalAnalyzerClient` and `ClaudeAnalyzerClient` log a warning and return early if the key is absent. They raise `RuntimeError` at call time with a clear Settings navigation hint.

2. **Absolute Privacy Enforcement (GDPR Alignment):**
   - **PII Leakage Prevention:** Any new service or backend module processing patient inputs must pass raw text through the Presidio/spaCy anonymization layer *prior* to external transmission.
   - **Key Protection:** Under no circumstances should an AI assistant write code containing hardcoded API keys or fall back to checking text files for credentials. Only use `keyring_manager.py`.

3. **MVVM Integrity & Typing Rules:**
   - **Zero UI Imports in Logic:** No `tkinter` or `ttk` imports inside `src/models/`, `src/db/`, or any ViewModel.
   - **Strict Type Hinting:** All newly written functions must include complete Python type annotations.

4. **Multi-Brand Code Decoupling:**
   - Never hardcode paths to client logos, company text, or localization overrides directly into layout code.
   - View templates must fetch strings from translation blocks and resolve branding via `settings.json`.

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
**Completed versions are never collapsed or summarised.** Every completed sub-version and its full task list remains fully expanded with `[x]` checkboxes in `TODO.md` indefinitely. Never remove task detail, never replace a completed section with a one-liner stub.

Full rule reference: `.dev_profile/developer_profile.md` § 5.

---

## Current Status: v2.6.0 Active — Next sub-version: v2.6.7 (manual)

**v2.6.6 complete:** Both `MedicalAnalyzerClient` and `ClaudeAnalyzerClient` now use startup guards — log warning + early return when key absent, raise `RuntimeError` at call time. `ClaudeAnalyzerClient` wired to keyring in `dsclinic.py`. Full audit: zero `app_settings.*_api_key` accesses anywhere in `src/`.

**`docs/architecture.md` updated by developer:** AD-12 through AD-17 added covering Split-Horizon Hybrid Inference, 16GB VRAM Edge Optimization, Multimodal Preprocessing, Zero-Trust PII Scrubbing, Defensive Desktop Error Isolation, and Continuous Quality Verification via pytest.

**Active milestone:** v2.6.0 — Secure Credential Management & `settings.ini` Elimination.
**Blocked milestone:** v2.5.0 (Chat Session View) — blocked until v2.6.7 is complete.

---

## Sub-version Execution Order

| Sub-version | Scope | Status |
|---|---|---|
| v2.6.1 | `importlib.metadata` → `app_name`/`app_version` | ✅ Done |
| v2.6.2 | New `src/models/keyring_manager.py` | ✅ Done |
| v2.6.3 | Purge secret fields from `AppSettings` + `load_unified()` | ✅ Done |
| v2.6.4 | `SettingsViewModel` reads/writes via keyring | ✅ Done |
| v2.6.5 | Settings UI masked credential fields + hint labels | ✅ Done |
| v2.6.6 | Both clients startup-guarded; Claude wired to keyring; full audit | ✅ Done |
| v2.6.7 | Rotate keys, `git rm settings.ini`, final audit | ▶ Next (manual) |

---

## v2.6.7 Steps (manual + code)

1. Revoke and regenerate `GOOGLE_API_KEY` in Google AI Studio.
2. Revoke and regenerate `ANTHROPIC_API_KEY` in Anthropic Console.
3. Launch app → Settings → AI → enter new keys → Save (writes to keyring).
4. Verify app starts and Gemini analysis runs correctly with keyring-sourced key.
5. Run: `git rm settings.ini`
6. Update `GEMINI.md` architecture section (credentials keyring-only, `settings.ini` deleted).
7. Commit as v2.6.7, then advance handoff to v2.5.0 active.

---

## Previously Active Milestone (blocked): v2.5.0 Chat Session View

**Streaming bug summary:** Trace on `var_response` calls `add_message()` on every write. Fix: track `self._current_bot_bubble: Optional[MarkdownLabel]`; on first chunk create one bubble; on subsequent chunks call `_current_bot_bubble.update_text(full_text)` in-place; clear reference when `var_is_analyzing` → `False`.
