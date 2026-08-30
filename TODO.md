# TODO — DSClinic Roadmap

> [!NOTE]
> **Task Management Rule (GASSI Standard):** This document is maintained in **strict descending version order**. The current active focus and upcoming planned versions must always be placed at the top, while completed releases move down into the historical archive at the bottom. Always update this list and session handoffs on every single code change.
>
> **Sub-version Rule:** Every parent milestone (e.g. v2.6.0) is broken into numbered sub-tasks (v2.6.1, v2.6.2, ...). Each sub-version is a self-contained, committable unit of work. Sub-versions are completed in order; the parent is marked done only when all sub-versions are complete.

---

## v2.6.0 — Secure Credential Management & `settings.ini` Elimination 🔐 Active

| Field | From | To | Status |
|---|---|---|---|
| `NAME` / `VERSION` | `settings.ini [APP]` | `pyproject.toml` via `importlib.metadata` | ✅ v2.6.1 |
| `GOOGLE_API_KEY` | `settings.ini [GOOGLE]` | OS keyring via `keyring_manager.py` | ✅ v2.6.2 |
| `ANTHROPIC_API_KEY` | `settings.ini [ANTHROPIC]` | OS keyring via `keyring_manager.py` | ✅ v2.6.2 |
| `GOOGLE_PROJECT_ID` | `settings.ini [GOOGLE]` | OS keyring via `keyring_manager.py` | ✅ v2.6.2 |
| `GOOGLE_PROJECT_LOCATION` | `settings.ini [GOOGLE]` | `config.json` (non-secret) | ✅ v2.6.3 |

---

### v2.6.1 ✅ Completed
- [x] `importlib.metadata` reads `app_name`/`app_version` in `load_unified()`.
- [x] `[APP]` INI block removed. Both fields excluded from `save_unified()`.

### v2.6.2 ✅ Completed
- [x] `src/models/keyring_manager.py` created with `get_credential`, `set_credential`, `delete_credential`.
- [x] All three exported from `src/models/__init__.py`.

### v2.6.3 ✅ Completed
- [x] `google_api_key` and `anthropic_api_key` fields removed from `AppSettings`.
- [x] Entire `configparser` / `settings.ini` INI block removed from `load_unified()`.
- [x] `configparser` import removed.
- [x] `"google": {"project_location": "us-central1"}` block added to `config.json`.
- [x] `google_project_location: str = "us-central1"` field added to `AppSettings`.
- [x] `google_project_location` read from `config.json` in `load_unified()`.
- [x] `"google_api_key"` and `"anthropic_api_key"` added to `exclude_fields` in `save_unified()`.

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
- [ ] In `src/api_gemini/client.py`: replace any `app_settings.google_api_key` reads with `get_credential("gemini")`.
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

- [ ] Fix streaming bubble bug: track `_current_bot_bubble: Optional[MarkdownLabel]`; update in-place via `update_text()`.
- [ ] Add `update_text(new_text: str)` to `MarkdownLabel`.
- [ ] Fix `ChatUser.TFrame/TLabel` colors (`ACCENT` blue + `WHITE` text).
- [ ] Non-blocking streaming via `queue.Queue` + `root.after` polling.
- [ ] Auto-scroll on each chunk. Disable input while in-flight.
- [ ] `LLMProvider` abstraction: Gemini, Claude, Groq, Together, HuggingFace, Ollama.
- [ ] PII Anonymization Layer: Presidio-based local scrubbing.
- [ ] `pytest` coverage: parsing, anonymization, provider fallback.

---

## v2.4.0 ✅ Completed
## v2.1.10 ✅ Completed
