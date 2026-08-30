# TODO — DSClinic Roadmap

> [!NOTE]
> **Task Management Rule (GASSI Standard):** This document is maintained in **strict descending version order**. The current active focus and upcoming planned versions must always be placed at the top, while completed releases move down into the historical archive at the bottom. Always update this list and session handoffs on every single code change.
>
> **Sub-version Rule:** Every parent milestone (e.g. v2.6.0) is broken into numbered sub-tasks (v2.6.1, v2.6.2, ...). Each sub-version is a self-contained, committable unit of work. Sub-versions are completed in order; the parent is marked done only when all sub-versions are complete.
>
> **TODO Archiving Rule:** Completed versions are never collapsed or summarised. Every completed sub-version and its full task list remains fully expanded with `[x]` checkboxes indefinitely.

---

## v2.5.0 — Chat Session View & Pluggable Multi-Provider Pipeline 🚀 Active

### Tasks

- [ ] **Implement full Chat Session View (`chat_session_view.py` rewrite, `styles.py` additions, and `main_container.py` wiring):**
  - [ ] Fix streaming bubble bug: track `_current_bot_bubble: Optional[MarkdownLabel]`; update in-place via `update_text()`.
  - [ ] Add `update_text(new_text: str)` to `MarkdownLabel`.
  - [ ] Fix `ChatUser.TFrame/TLabel` colors (`ACCENT` blue + `WHITE` text).
  - [ ] Non-blocking streaming via `queue.Queue` + `root.after` polling.
  - [ ] Auto-scroll on each chunk. Disable input while in-flight.
  - [ ] Wire `ChatSessionView` and `ChatSessionViewModel` inside `main_container.py`.
- [ ] **Build Unified `LLMProvider` Abstraction & Hybrid Pipeline:**
  - [ ] Design a generic, decoupled `LLMProvider` interface.
  - [ ] Integrate Gemini, Claude, Groq, Together, HuggingFace, Ollama under this interface.
- [ ] **Establish PII Anonymization Layer & Local Preprocessors:**
  - [ ] Presidio-based local PII scrubbing.
  - [ ] MONAI stubs for MRI slice selection; YOLOv8/ViT hooks for microscopy blood smears.
- [ ] **Rigorous Unit Testing (`pytest`):**
  - [ ] Tests for parsing, anonymization, provider fallback logic.

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
