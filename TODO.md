# TODO — DSClinic Roadmap

> [!NOTE]
> **Task Management Rule (GASSI Standard):** This document is maintained in **strict descending version order**. The current active focus and upcoming planned versions must always be placed at the top, while completed releases move down into the historical archive at the bottom. Always update this list and session handoffs on every single code change.
>
> **Sub-version Rule:** Every parent milestone (e.g. v2.6.0) is broken into numbered sub-tasks (v2.6.1, v2.6.2, ...). Each sub-version is a self-contained, committable unit of work. Sub-versions are completed in order; the parent is marked done only when all sub-versions are complete.

---

## v2.6.0 — Secure Credential Management & `settings.ini` Elimination 🔐 Active

**Priority blocker.** `settings.ini` currently commits two live API keys (`GOOGLE_API_KEY`, `ANTHROPIC_API_KEY`) and a Google Project ID to the public GitHub repository. Additionally, `app_name` and `app_version` are duplicated across `settings.ini` and `pyproject.toml`. This milestone fully eliminates `settings.ini` from the project by migrating every field it contains to its correct permanent home:

| Field | Current location | New location |
|---|---|---|
| `NAME` (app name) | `settings.ini [APP]` | `pyproject.toml [project] → name`, read via `importlib.metadata` |
| `VERSION` (app version) | `settings.ini [APP]` | `pyproject.toml [project] → version`, read via `importlib.metadata` |
| `GOOGLE_API_KEY` | `settings.ini [GOOGLE]` | OS keyring via `keyring_manager.py` |
| `ANTHROPIC_API_KEY` | `settings.ini [ANTHROPIC]` | OS keyring via `keyring_manager.py` |
| `GOOGLE_PROJECT_ID` | `settings.ini [GOOGLE]` | OS keyring via `keyring_manager.py` |
| `GOOGLE_PROJECT_LOCATION` | `settings.ini [GOOGLE]` | `config.json` (non-secret, non-sensitive) |

After this milestone, `settings.ini` is deleted from the project entirely — not just gitignored.

---

### v2.6.1 — `pyproject.toml`: App Name & Version as Single Source of Truth

Move `app_name` and `app_version` out of `settings.ini` and into `pyproject.toml` so there is exactly one place to update them at release time.

- [ ] Confirm `pyproject.toml` `[project]` already has `name` and `version` fields (they do: `name = "dsclinic"`, `version = "2.6.0"`).
- [ ] Add `importlib.metadata` read in `AppSettings.load_unified()` to pull `app_name` and `app_version` from the installed package metadata at runtime:
  ```python
  from importlib.metadata import metadata, PackageNotFoundError
  try:
      _meta = metadata("dsclinic")
      merged_data["app_name"] = _meta["Name"]
      merged_data["app_version"] = _meta["Version"]
  except PackageNotFoundError:
      pass  # fallback to AppSettings field defaults
  ```
- [ ] Remove the `settings.ini` `[APP]` parsing block from `load_unified()`.
- [ ] Verify Settings UI `var_app_version` still reads from `app_settings.app_version` correctly.

---

### v2.6.2 — `keyring_manager.py`: Secure Credential Store Module

Create the single module that owns all keyring access. Architecture mirrors `gassi/core/ai/factory.py → get_api_key()`.

- [ ] Create `src/models/keyring_manager.py` with:
  - [ ] `_KEYRING_SERVICE = "dsclinic"` constant.
  - [ ] `_CREDENTIAL_KEYS: dict[str, str]` mapping logical names to keyring usernames:
    ```python
    _CREDENTIAL_KEYS = {
        "gemini":            "gemini_api_key",
        "anthropic":         "anthropic_api_key",
        "google_project_id": "google_project_id",
    }
    ```
  - [ ] `get_credential(name: str) -> str | None` — reads from keyring, returns `None` if not set.
  - [ ] `set_credential(name: str, value: str) -> None` — writes to keyring only if value is non-empty.
  - [ ] `delete_credential(name: str) -> None` — removes from keyring (for key rotation flows).
- [ ] Export all three functions from `src/models/__init__.py`.
- [ ] Add `keyring` to `pyproject.toml` `[project] dependencies` (already done — verify).

---

### v2.6.3 — `AppSettings`: Remove All Secret Fields

Purge every secret and `settings.ini`-sourced field from `AppSettings` and its loader.

- [ ] **Remove fields from `AppSettings` class (`src/models/settings.py`):**
  - [ ] Remove `google_api_key: str = ""`
  - [ ] Remove `anthropic_api_key: str = ""`
- [ ] **Remove from `load_unified()`:**
  - [ ] Remove the `[GOOGLE]` and `[ANTHROPIC]` key parsing from the `configparser` block.
  - [ ] Remove the `[APP]` NAME/VERSION parsing (covered by v2.6.1).
  - [ ] Remove the entire `configparser` import and block once all three sections are gone.
  - [ ] Add `GOOGLE_PROJECT_LOCATION` to `config.json` under a `"google"` key (non-secret).
  - [ ] Read `google_project_location` from `config.json` in `load_unified()` and store as a normal `AppSettings` field.
- [ ] **Remove from `save_unified()`:**
  - [ ] Add `"google_api_key"` and `"anthropic_api_key"` to the `exclude_fields` set (defensive — fields no longer exist but guard against regression).

---

### v2.6.4 — `SettingsViewModel`: Read & Write Credentials via Keyring

- [ ] In `__init__`: replace `tk.StringVar(value=app_settings.google_api_key)` with `tk.StringVar(value=get_credential("gemini") or "")`.
- [ ] Add `var_anthropic_api_key = tk.StringVar(value=get_credential("anthropic") or "")`.
- [ ] Add `var_google_project_id = tk.StringVar(value=get_credential("google_project_id") or "")`.
- [ ] In `update_from_config()`: mirror the same keyring reads for all three vars.
- [ ] In `save_to_config()`: replace `app_settings.google_api_key = ...` with `set_credential("gemini", self.var_google_api_key.get().strip())`. Add equivalent calls for `anthropic` and `google_project_id`. **Do not write these values via `save_unified()`.**

---

### v2.6.5 — Settings UI: Masked Key Entry Fields

- [ ] In `_build_analyze_instructions_panel()` (`settings_view.py`):
  - [ ] Change the existing `_entry_field("Google API Key", ...)` call to pass `show="*"`.
  - [ ] Add `_entry_field("Anthropic API Key", self.view_model.var_anthropic_api_key, show="*")`.
  - [ ] Add `_entry_field("Google Project ID", self.view_model.var_google_project_id, show="*")`.
  - [ ] Add a `ttk.Label` hint under each key field: `"Stored securely in OS keyring — never written to disk."` using `SUBTLE` foreground and `FS` font.
- [ ] Verify the `_entry_field` helper accepts and passes through a `show` kwarg to `ttk.Entry`.

---

### v2.6.6 — Runtime Key Consumption: `dsclinic.py` & API Clients

- [ ] In `src/dsclinic.py` → `DSClinic.__init__`:
  - [ ] Import `from models.keyring_manager import get_credential`.
  - [ ] Replace `api_key=app_settings.google_api_key` with `api_key=get_credential("gemini") or ""`.
  - [ ] Add startup guard: if `get_credential("gemini")` is `None` or empty, log `WARNING` and surface the message to the user via the ViewModel status vars.
- [ ] In `src/api_gemini/` — replace any remaining `app_settings.google_api_key` reads with `get_credential("gemini")`.
- [ ] In `src/api_claude/` — replace any `app_settings.anthropic_api_key` reads with `get_credential("anthropic")`.
- [ ] Check for any `GOOGLE_PROJECT_ID` / `GOOGLE_PROJECT_LOCATION` usage and update accordingly.

---

### v2.6.7 — Delete `settings.ini`, Key Rotation & Final Cleanup

This is the final commit of the milestone. Only after v2.6.2–v2.6.6 are merged and the app is confirmed working via keyring does this step run.

- [ ] **Rotate all exposed credentials** (app no longer reads from `settings.ini` so rotation is now safe to defer to here):
  - [ ] Revoke and regenerate `GOOGLE_API_KEY` in Google AI Studio.
  - [ ] Revoke and regenerate `ANTHROPIC_API_KEY` in Anthropic Console.
  - [ ] Enter the new keys into the app via Settings → AI → key fields (writes to keyring).
- [ ] **Remove `settings.ini` from git tracking and delete it:**
  ```bash
  git rm settings.ini
  git commit -m "security: delete settings.ini — all credentials migrated to OS keyring"
  git push
  ```
- [ ] Confirm `.gitignore` has `settings.ini` on its own line (already present — verify it is committed).
- [ ] Search entire codebase for any remaining `configparser` / `settings.ini` references — must be zero.
- [ ] Search for any remaining `app_settings.google_api_key` or `app_settings.anthropic_api_key` attribute accesses — must be zero.
- [ ] Update `GEMINI.md`: document that credentials are keyring-only, `settings.ini` no longer exists, and `app_name`/`app_version` come from `pyproject.toml` via `importlib.metadata`.
- [ ] Update `CHANGELOG.md` with the full v2.6.0 release entry.
- [ ] Update `docs/session_handoff.md` to v2.6.0 completion / v2.5.0 active status.

---

## v2.5.0 — Chat Session View & Pluggable Multi-Provider Pipeline 🚀 Next

**Blocked on v2.6.0.** No live API key available for integration testing until the keyring is wired and v2.6.7 key rotation is done. Full streaming bug fix and multi-provider pipeline work resumes after v2.6.7 is committed.

### Tasks

- [ ] **Implement full Chat Session View (`chat_session_view.py` rewrite, `styles.py` additions, and `main_container.py` wiring):**
  - [ ] Complete the Tkinter widget layout inside `src/dsclinic_gui/chat_session_view.py` using standard `ttk` styled components.
  - [ ] Fix the streaming bubble bug: track `_current_bot_bubble: Optional[MarkdownLabel]` in the View; spawn one bubble per AI response, update it in-place via `update_text()` on subsequent chunks.
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

- [x] Consolidate Models into `src/models/` Package.
- [x] Implement Future-Proof Unified `src/models/settings.py`.
- [x] Codebase-Wide Import Refactoring.
- [x] Settings UI Migration.
- [x] Refactor Configuration Loader (`src/config.py`).

---

## v2.1.10 — UI & Layout Refinement ✅ Completed

### Completed

- [x] Centered section headers in main panel.
- [x] Settings window layout restructuring.
- [x] Resolved nested-tuple serialization bug on multiple settings saves.
- [x] Token-optimized prompt transmission.
