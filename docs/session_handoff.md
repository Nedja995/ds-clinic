# Session Handoff — DSClinic Secure Credential Management & `settings.ini` Elimination

This handoff is prepared to allow any incoming development AI assistant (including Gemini CLI and Claude) to immediately continue development.

> [!IMPORTANT]
> **Handoff & TODO Update Rule (GASSI Standard):** On *every single code modification or task completion*, the active AI assistant MUST immediately update **all applicable dev docs** and `docs/session_handoff.md`. Skipping any applicable file without explicit reason is an error.

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

Full rule reference: `.dev_profile/developer_profile.md` § 5.

---

## Current Status: v2.6.0 Active — Next sub-version: v2.6.5

**v2.6.4 complete:** `SettingsViewModel` reads all three credentials from keyring on init and `update_from_config()`. Writes all three via `set_credential()` in `save_to_config()`. No `app_settings.*_api_key` access anywhere in the file.

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
| v2.6.5 | Settings UI masked entry fields + hint labels | ▶ Next |
| v2.6.6 | Full audit: `api_gemini/`, `api_claude/` | — |
| v2.6.7 | Rotate keys, `git rm settings.ini`, final audit | — |

---

## v2.6.5 Implementation Notes

File to touch: `src/dsclinic_gui/settings/settings_view.py`

- `_entry_field` helper needs `show` kwarg passed to `ttk.Entry` — check if it already accepts `**kwargs` or needs explicit `show` param.
- Add `show="*"` to existing Google API Key field.
- Add two new `_entry_field` calls for Anthropic API Key and Google Project ID.
- Add `ttk.Label` hint under each: `"Stored securely in OS keyring — never written to disk."` using `SUBTLE` fg and `FS` font.

---

## Previously Active Milestone (blocked): v2.5.0 Chat Session View

**Streaming bug summary:** Trace on `var_response` calls `add_message()` on every write. Fix: track `self._current_bot_bubble: Optional[MarkdownLabel]`; on first chunk create one bubble; on subsequent chunks call `_current_bot_bubble.update_text(full_text)` in-place; clear reference when `var_is_analyzing` → `False`.
