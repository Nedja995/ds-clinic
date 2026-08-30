# TODO — DSClinic Roadmap

> [!NOTE]
> **Task Management Rule (GASSI Standard):** This document is maintained in **strict descending version order**. The current active focus and upcoming planned versions must always be placed at the top, while completed releases move down into the historical archive at the bottom. Always update this list and session handoffs on every single code change.
>
> **Sub-version Rule:** Every parent milestone (e.g. v2.6.0) is broken into numbered sub-tasks (v2.6.1, v2.6.2, ...). Each sub-version is a self-contained, committable unit of work. Sub-versions are completed in order; the parent is marked done only when all sub-versions are complete.

---

## v2.6.0 — Secure Credential Management & `settings.ini` Elimination 🔐 Active

**Priority blocker.** `settings.ini` currently commits two live API keys and a Google Project ID to the public GitHub repository. This milestone fully eliminates `settings.ini` by migrating every field to its correct permanent home.

| Field | From | To |
|---|---|---|
| `NAME` / `VERSION` | `settings.ini [APP]` | `pyproject.toml` via `importlib.metadata` ✅ |
| `GOOGLE_API_KEY` | `settings.ini [GOOGLE]` | OS keyring via `keyring_manager.py` |
| `ANTHROPIC_API_KEY` | `settings.ini [ANTHROPIC]` | OS keyring via `keyring_manager.py` |
| `GOOGLE_PROJECT_ID` | `settings.ini [GOOGLE]` | OS keyring via `keyring_manager.py` |
| `GOOGLE_PROJECT_LOCATION` | `settings.ini [GOOGLE]` | `config.json` (non-secret) |

---

### v2.6.1 — `pyproject.toml`: App Name & Version as Single Source of Truth ✅ Completed

- [x] `importlib.metadata.metadata("dsclinic")` reads `app_name` and `app_version` in `load_unified()` as step A0.
- [x] `[APP]` NAME/VERSION block removed from `settings.ini` INI parsing.
- [x] `app_name` and `app_version` added to `exclude_fields` in `save_unified()`.
- [x] `pyproject.toml` is now the single source of truth for both fields.

---

### v2.6.2 — `keyring_manager.py`: Secure Credential Store Module

Create the single module that owns all keyring access. Architecture mirrors `gassi/core/ai/factory.py → get_api_key()`.

- [ ] Create `src/models/keyring_manager.py` with:
  - [ ] `_KEYRING_SERVICE = "dsclinic"` constant.
  - [ ] `_CREDENTIAL_KEYS: dict[str, str]` mapping:
    - `"gemini"` → `"gemini_api_key"`
    - `"anthropic"` → `"anthropic_api_key"`
    - `"google_project_id"` → `"google_project_id"`
  - [ ] `get_credential(name: str) -> str | None`
  - [ ] `set_credential(name: str, value: str) -> None`
  - [ ] `delete_credential(name: str) -> None`
- [ ] Export all three functions from `src/models/__init__.py`.
- [ ] Verify `keyring` is in `pyproject.toml` dependencies (already added).

---

### v2.6.3 — `AppSettings`: Remove All Secret Fields

- [ ] Remove `google_api_key: str = ""` and `anthropic_api_key: str = ""` from `AppSettings`.
- [ ] Remove the entire `configparser` / `settings.ini` INI block from `load_unified()` (step A1).
- [ ] Remove `configparser` import.
- [ ] Add `"google"` block to `config.json`: `{"project_location": "us-central1"}`.
- [ ] Add `google_project_location: str = "us-central1"` field to `AppSettings`.
- [ ] Read `google_project_location` from `config.json` in `load_unified()`.
- [ ] Add `"google_api_key"` and `"anthropic_api_key"` to `exclude_fields` in `save_unified()` (defensive).

---

### v2.6.4 — `SettingsViewModel`: Read & Write Credentials via Keyring

- [ ] Replace `tk.StringVar(value=app_settings.google_api_key)` with `tk.StringVar(value=get_credential("gemini") or "")`.
- [ ] Add `var_anthropic_api_key = tk.StringVar(value=get_credential("anthropic") or "")`.
- [ ] Add `var_google_project_id = tk.StringVar(value=get_credential("google_project_id") or "")`.
- [ ] In `update_from_config()`: mirror same keyring reads for all three vars.
- [ ] In `save_to_config()`: call `set_credential(...)` for all three; do **not** write via `save_unified()`.

---

### v2.6.5 — Settings UI: Masked Key Entry Fields

- [ ] Change `_entry_field("Google API Key", ...)` to pass `show="*"`.
- [ ] Add `_entry_field("Anthropic API Key", self.view_model.var_anthropic_api_key, show="*")`.
- [ ] Add `_entry_field("Google Project ID", self.view_model.var_google_project_id, show="*")`.
- [ ] Add hint `ttk.Label` under each: `"Stored securely in OS keyring — never written to disk."` (`SUBTLE` fg, `FS` font).
- [ ] Verify `_entry_field` helper accepts and passes `show` kwarg through to `ttk.Entry`.

---

### v2.6.6 — Runtime Key Consumption: `dsclinic.py` & API Clients

- [ ] In `src/dsclinic.py → DSClinic.__init__`: replace `api_key=app_settings.google_api_key` with `api_key=get_credential("gemini") or ""`.
- [ ] Add startup guard: if `get_credential("gemini")` is `None` or empty, log `WARNING` and surface message via status vars.
- [ ] In `src/api_gemini/client.py`: replace any remaining `app_settings.google_api_key` reads with `get_credential("gemini")`.
- [ ] In `src/api_claude/client.py`: replace any `app_settings.anthropic_api_key` reads with `get_credential("anthropic")`.

---

### v2.6.7 — Rotate Keys, Delete `settings.ini`, Final Cleanup

- [ ] Revoke and regenerate `GOOGLE_API_KEY` in Google AI Studio.
- [ ] Revoke and regenerate `ANTHROPIC_API_KEY` in Anthropic Console.
- [ ] Enter new keys via Settings → AI key fields (writes to keyring).
- [ ] `git rm settings.ini` and commit.
- [ ] Verify `.gitignore` has `settings.ini` (already present).
- [ ] Search codebase for any remaining `configparser` / `settings.ini` references — must be zero.
- [ ] Search for any remaining `app_settings.google_api_key` / `app_settings.anthropic_api_key` — must be zero.
- [ ] Update `GEMINI.md` architecture section.
- [ ] Update `CHANGELOG.md` with full v2.6.0 release entry.
- [ ] Update `docs/session_handoff.md` to v2.6.0 complete / v2.5.0 active.

---

## v2.5.0 — Chat Session View & Pluggable Multi-Provider Pipeline 🚀 Next

**Blocked on v2.6.0.**

### Tasks

- [ ] **Chat Session View (`chat_session_view.py` rewrite):**
  - [ ] Fix streaming bubble bug: track `_current_bot_bubble: Optional[MarkdownLabel]`; update in-place via `update_text()`.
  - [ ] Add `update_text(new_text: str)` to `MarkdownLabel`.
  - [ ] Fix `ChatUser.TFrame/TLabel` colors (`ACCENT` blue + `WHITE` text).
  - [ ] Non-blocking streaming via `queue.Queue` + `root.after` polling.
  - [ ] Auto-scroll on each chunk. Disable input while in-flight.
- [ ] **`LLMProvider` Abstraction:** Gemini, Claude, Groq, Together, HuggingFace, Ollama.
- [ ] **PII Anonymization Layer:** Presidio-based local scrubbing.
- [ ] **`pytest` Coverage:** Parsing, anonymization, provider fallback.

---

## v2.4.0 — Unified Configuration, MVVM Schema & High-Privacy Alignment ✅ Completed

- [x] Consolidate Models into `src/models/` Package.
- [x] Hybrid `AppSettings` with `load_unified` and atomic `save_unified`.
- [x] Codebase-wide import refactoring to `from models import app_settings`.
- [x] Settings UI migrated to `app_settings`.
- [x] Deleted legacy `src/config.py` and `src/npy/core/settings_manager.py`.

---

## v2.1.10 — UI & Layout Refinement ✅ Completed

- [x] Centered section headers in main panel.
- [x] Settings window layout restructuring.
- [x] Resolved nested-tuple serialization bug on multiple settings saves.
- [x] Token-optimized prompt transmission.
