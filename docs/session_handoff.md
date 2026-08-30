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

### TODO Archiving Rule
**Completed versions are never collapsed or summarised.** Every completed sub-version and its full task list remains fully expanded with `[x]` checkboxes in `TODO.md` indefinitely. The only change on completion is marking tasks `[x]` and adding ✅ to the section heading. Never remove task detail, never replace a completed section with a one-liner stub.

Full rule reference: `.dev_profile/developer_profile.md` § 5.

---

## Current Status: v2.6.0 Active — Next sub-version: v2.6.6

**v2.6.5 complete:** New `_credential_field` helper renders masked `ttk.Entry` + keyring hint label. Three credential fields added to Settings UI: Google API Key, Anthropic API Key, Google Project ID. `_HEIGHT` bumped to 860px.

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
| v2.6.6 | Full audit: `api_gemini/`, `api_claude/` | ▶ Next |
| v2.6.7 | Rotate keys, `git rm settings.ini`, final audit | — |

---

## v2.6.6 Implementation Notes

Grep the entire `src/` for `app_settings.google_api_key` and `app_settings.anthropic_api_key` — both must be zero hits after this sub-version. Files most likely to contain them:
- `src/api_gemini/client.py`
- `src/api_claude/client.py`

---

## Previously Active Milestone (blocked): v2.5.0 Chat Session View

**Streaming bug summary:** Trace on `var_response` calls `add_message()` on every write. Fix: track `self._current_bot_bubble: Optional[MarkdownLabel]`; on first chunk create one bubble; on subsequent chunks call `_current_bot_bubble.update_text(full_text)` in-place; clear reference when `var_is_analyzing` → `False`.
