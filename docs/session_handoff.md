# Session Handoff — DSClinic Secure Credential Management & `settings.ini` Elimination

This handoff is prepared to allow any incoming development AI assistant (including Gemini CLI and Claude) to immediately continue development.

> [!IMPORTANT]
> **Handoff & TODO Update Rule (GASSI Standard):** On *every single code modification or task completion*, the active AI assistant MUST immediately update **all applicable dev docs** and `docs/session_handoff.md`. Skipping any applicable file without explicit reason is an error.

---

## Version & Commit Discipline (GASSI Standard — mandatory for every sub-version)

Every sub-version is one commit. Code + all applicable docs travel together.

```bash
# Stage only files changed in this sub-version — NEVER `git add .`
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

Full rule reference: `.dev_profile/developer_profile.md` § 5.

---

## Current Status: v2.6.0 Active — Next sub-version: v2.6.3

**v2.6.2 complete:** `src/models/keyring_manager.py` created with `get_credential`, `set_credential`, `delete_credential`. All three exported from `src/models/__init__.py`.

**v2.6.1 complete:** `app_name`/`app_version` sourced from `pyproject.toml` via `importlib.metadata`. AD-11 added.

**Active milestone:** v2.6.0 — Secure Credential Management & `settings.ini` Elimination.
**Blocked milestone:** v2.5.0 (Chat Session View) — blocked until v2.6.7 is complete.

---

## Field Migration Map

| Field | From | To | Status |
|---|---|---|---|
| `NAME` / `VERSION` | `settings.ini [APP]` | `pyproject.toml` via `importlib.metadata` | ✅ v2.6.1 |
| `GOOGLE_API_KEY` | `settings.ini [GOOGLE]` | `keyring("dsclinic", "gemini_api_key")` | ✅ v2.6.2 |
| `ANTHROPIC_API_KEY` | `settings.ini [ANTHROPIC]` | `keyring("dsclinic", "anthropic_api_key")` | ✅ v2.6.2 |
| `GOOGLE_PROJECT_ID` | `settings.ini [GOOGLE]` | `keyring("dsclinic", "google_project_id")` | ✅ v2.6.2 |
| `GOOGLE_PROJECT_LOCATION` | `settings.ini [GOOGLE]` | `config.json ["google"]["project_location"]` | v2.6.3 |

---

## Sub-version Execution Order

| Sub-version | Scope | Status |
|---|---|---|
| v2.6.1 | `importlib.metadata` → `app_name`/`app_version` | ✅ Done |
| v2.6.2 | New `src/models/keyring_manager.py` | ✅ Done |
| v2.6.3 | Purge secret fields from `AppSettings` + `load_unified()` | ▶ Next |
| v2.6.4 | `SettingsViewModel` reads/writes via keyring | — |
| v2.6.5 | Settings UI masked entry fields + hint labels | — |
| v2.6.6 | Runtime key consumption in `dsclinic.py`, `api_gemini/`, `api_claude/` | — |
| v2.6.7 | Rotate keys, `git rm settings.ini`, final audit | — |

---

## v2.6.3 Implementation Notes

Files to touch:
- `src/models/settings.py` — remove `google_api_key`/`anthropic_api_key` fields; remove `configparser` block (step A1); add `google_project_location` field; read it from `config.json`.
- `config.json` — add `"google": {"project_location": "us-central1"}` block.

---

## Reference Architecture: GASSI Keyring Pattern

- `proj_gassi2/src/gassi/core/ai/factory.py` — `_KEYRING_SERVICE`, `_PROVIDER_KEYRING_USERNAME`, `get_api_key()`
- `proj_gassi2/src/gassi/views/settings_dialog.py` — keyring read/write pattern

---

## Previously Active Milestone (blocked): v2.5.0 Chat Session View

**Streaming bug summary:** Trace on `var_response` calls `add_message()` on every write. Fix: track `self._current_bot_bubble: Optional[MarkdownLabel]`; on first chunk create one bubble; on subsequent chunks call `_current_bot_bubble.update_text(full_text)` in-place; clear reference when `var_is_analyzing` → `False`.
