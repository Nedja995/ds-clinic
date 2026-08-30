# TODO — DSClinic Roadmap

> [!NOTE]
> **Task Management Rule (GASSI Standard):** This document is maintained in **strict descending version order**. The current active focus and upcoming planned versions must always be placed at the top, while completed releases move down into the historical archive at the bottom. Always update this list and session handoffs on every single code change.
>
> **Sub-version Rule:** Every parent milestone (e.g. v2.6.0) is broken into numbered sub-tasks (v2.6.1, v2.6.2, ...). Each sub-version is a self-contained, committable unit of work. Sub-versions are completed in order; the parent is marked done only when all sub-versions are complete.

---

## v2.6.0 — Secure Credential Management & `settings.ini` Elimination 🔐 Active

**Priority blocker.** `settings.ini` committed two live API keys and a Google Project ID to the public GitHub repository. This milestone fully eliminates `settings.ini` by migrating every field to its correct permanent home.

| Field | From | To | Status |
|---|---|---|---|
| `NAME` / `VERSION` | `settings.ini [APP]` | `pyproject.toml` via `importlib.metadata` | ✅ v2.6.1 |
| `GOOGLE_API_KEY` | `settings.ini [GOOGLE]` | OS keyring via `keyring_manager.py` | ✅ v2.6.2 |
| `ANTHROPIC_API_KEY` | `settings.ini [ANTHROPIC]` | OS keyring via `keyring_manager.py` | ✅ v2.6.2 |
| `GOOGLE_PROJECT_ID` | `settings.ini [GOOGLE]` | OS keyring via `keyring_manager.py` | ✅ v2.6.2 |
| `GOOGLE_PROJECT_LOCATION` | `settings.ini [GOOGLE]` | `config.json` (non-secret) | ✅ v2.6.3 |

---

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

### v2.6.6 — Full Audit: `api_gemini/` & `api_claude/` Clients

- [ ] `src/api_gemini/client.py`: verify no `app_settings.google_api_key` references remain.
- [ ] `src/api_claude/client.py`: verify no `app_settings.anthropic_api_key` references remain.
- [ ] Search entire `src/` for `app_settings.google_api_key` and `app_settings.anthropic_api_key` — must be zero hits.

---

### v2.6.7 — Rotate Keys, Delete `settings.ini`, Final Cleanup

- [ ] Revoke and regenerate `GOOGLE_API_KEY` in Google AI Studio.
- [ ] Revoke and regenerate `ANTHROPIC_API_KEY` in Anthropic Console.
- [ ] Enter new keys via Settings → AI → credential fields (writes to keyring).
- [ ] `git rm settings.ini` and commit.
- [ ] Verify `.gitignore` has `settings.ini` (already present).
- [ ] Search codebase for any remaining `configparser` / `settings.ini` references — must be zero.
- [ ] Update `GEMINI.md` architecture section.
- [ ] Update `CHANGELOG.md` with full v2.6.0 release entry.
- [ ] Update `docs/session_handoff.md` to v2.6.0 complete / v2.5.0 active.

---

## v2.5.0 — Chat Session View & Pluggable Multi-Provider Pipeline 🚀 Next

**Blocked on v2.6.0.**

### Tasks

- [ ] **Implement full Chat Session View (`chat_session_view.py` rewrite, `styles.py` additions, and `main_container.py` wiring):**
  - [ ] Complete the Tkinter widget layout inside `src/dsclinic_gui/chat_session_view.py` using standard `ttk` styled components.
  - [ ] Fix streaming bubble bug: track `_current_bot_bubble: Optional[MarkdownLabel]`; spawn one bubble per AI response, update it in-place via `update_text()` on subsequent chunks.
  - [ ] Add `update_text(new_text: str)` method to `MarkdownLabel` for in-place streaming updates.
  - [ ] Fix `ChatUser.TFrame/TLabel` colors in `styles.py` (solid `ACCENT` blue + `WHITE` text, not pale `ACCENT_LT`).
  - [ ] Support non-blocking, asynchronous text streaming via `queue.Queue` and `root.after` polling.
  - [ ] Style user and bot message bubbles using centralized definitions in `src/dsclinic_gui/styles.py`.
  - [ ] Wire `ChatSessionView` and `ChatSessionViewModel` inside `src/dsclinic_gui/main_container.py`.
  - [ ] Prevent user input / show loading indicator while an AI request is in-flight.
  - [ ] Handle auto-scrolling of the chat transcript as new text chunks stream in.
- [ ] **Build Unified `LLMProvider` Abstraction & Hybrid Pipeline:**
  - [ ] Design a generic, decoupled `LLMProvider` interface to prevent vendor lock-in.
  - [ ] Integrate Google Gemini API (`google-genai`) and Anthropic Claude API (`anthropic`) under this unified interface.
  - [ ] Add support for hosted open-weights providers (Groq API, Together AI, HuggingFace API).
  - [ ] Implement local Ollama support with 4-bit and 8-bit quantization.
- [ ] **Establish PII Anonymization Layer & Local Preprocessors:**
  - [ ] Build a robust local PII scrubbing mechanism (using RegEx and Presidio).
  - [ ] Incorporate local preprocessor stubs (MONAI for MRI slice selection; YOLOv8/Vision Transformer hooks for microscopy blood smears).
- [ ] **Rigorous Unit Testing (`pytest`):**
  - [ ] Install `pytest` and build automated test suites verifying medical data parsing, PII anonymization, and provider fallback logic.

---

## v2.4.0 — Unified Configuration, MVVM Schema & High-Privacy Alignment ✅ Completed

### Completed

- [x] **Consolidate Models into `src/models/` Package:**
  - [x] Created unified package folder.
  - [x] Migrated patient schemas into `src/models/patient.py` and diagnostic structures into `src/models/diagnostics.py`.
  - [x] Deleted legacy flat `src/models.py` and `src/models_new/` folders.
- [x] **Implement Future-Proof Unified `src/models/settings.py`:**
  - [x] Built the Pydantic-Settings `AppSettings` class as single source of truth for static configs and user customizations.
  - [x] Merged layered loading (`load_unified`) from default baselines and clinician overrides under `.config/medai_vitec/settings.json`.
  - [x] Supported atomic `save_unified` writes back to local folders.
  - [x] Deleted legacy `src/config.py` and `src/npy/core/settings_manager.py`.
- [x] **Codebase-Wide Import Refactoring:**
  - [x] Safely refactored all system files to import config settings via `from models.settings import app_settings`.
- [x] **Settings UI Migration:**
  - [x] Updated `SettingsViewModel` and `SettingsWindow` to bind directly to `app_settings`.
- [x] **Refactor Configuration Loader (`src/config.py`):**
  - [x] Implemented two-tiered loader reading `config.json` as read-only baseline layered with `settings.json`.

---

## v2.1.10 — UI & Layout Refinement ✅ Completed

### Completed

- [x] Centered section headers in main panel: Set `anchor="center"` on card titles inside the `_card` factory in `src/dsclinic_gui/report_view.py`.
- [x] Settings window layout restructuring: Reworked `_build_general_section` and created `_build_support_section` in `src/dsclinic_gui/settings/settings_view.py` to separate General and Support.
- [x] Resolved nested-tuple serialization bug on multiple settings saves in `src/dsclinic_gui/settings/settings_view_model.py`.
- [x] Token-optimized prompt transmission: Added automatic newline/whitespace cleaning inside `src/dsclinic.py` before passing templates to the Gemini API.
