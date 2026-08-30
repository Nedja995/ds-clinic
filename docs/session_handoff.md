# Session Handoff — DSClinic Secure Credential Management & `settings.ini` Elimination

This handoff is prepared to allow any incoming development AI assistant (including Gemini CLI and Claude) to immediately continue development.

> [!IMPORTANT]
> **Handoff & TODO Update Rule (GASSI Standard):** On *every single code modification or task completion*, the active AI assistant MUST immediately update both `TODO.md` (maintaining descending version order) and `docs/session_handoff.md`. This maintains perfect workspace continuity across different development platforms and resets, avoiding duplicate work and context waste.

---

## Version & Commit Discipline (GASSI Standard — mandatory for every sub-version)

Every sub-version is one commit. Code + docs always travel together.

```bash
# Stage only files changed in this sub-version — NEVER `git add .`
git add <changed source files> CHANGELOG.md TODO.md pyproject.toml docs/session_handoff.md

git commit -m "v2.6.X: <imperative short description>"
git push
```

**Commit message format:** `v{MAJOR}.{MINOR}.{PATCH}: <what changed>`

**Every commit must include:**

| File | Update |
|---|---|
| `CHANGELOG.md` | New `## [X.Y.Z]` entry (Added / Fixed / Changed) |
| `TODO.md` | Mark completed tasks `[x]` |
| `pyproject.toml` | Bump `version = "X.Y.Z"` |
| `docs/session_handoff.md` | Update current status to next sub-version |
| `GEMINI.md` | Only if architectural rules changed |

Full rule reference: `.dev_profile/developer_profile.md` § 5.

---

## Current Status: v2.6.0 Active — Next sub-version: v2.6.1

**Active milestone:** v2.6.0 — Secure Credential Management & `settings.ini` Elimination.
**Blocked milestone:** v2.5.0 (Chat Session View) — blocked until v2.6.7 is complete.

The exposed keys in `settings.ini` remain live intentionally until v2.6.7. The app continues to boot normally with `settings.ini` present during v2.6.1–v2.6.6 development. Once v2.6.6 is confirmed working via keyring, v2.6.7 handles key rotation and file deletion in one atomic commit.

---

## Field Migration Map

| Field | From | To |
|---|---|---|
| `NAME` | `settings.ini [APP]` | `pyproject.toml [project] → name`, read via `importlib.metadata` |
| `VERSION` | `settings.ini [APP]` | `pyproject.toml [project] → version`, read via `importlib.metadata` |
| `GOOGLE_API_KEY` | `settings.ini [GOOGLE]` | `keyring("dsclinic", "gemini_api_key")` |
| `ANTHROPIC_API_KEY` | `settings.ini [ANTHROPIC]` | `keyring("dsclinic", "anthropic_api_key")` |
| `GOOGLE_PROJECT_ID` | `settings.ini [GOOGLE]` | `keyring("dsclinic", "google_project_id")` |
| `GOOGLE_PROJECT_LOCATION` | `settings.ini [GOOGLE]` | `config.json ["google"]["project_location"]` (non-secret) |

---

## Sub-version Execution Order

| Sub-version | Scope | Notes |
|---|---|---|
| v2.6.1 | `importlib.metadata` → `app_name`/`app_version` from `pyproject.toml` | Code-only |
| v2.6.2 | New `src/models/keyring_manager.py` | Code-only |
| v2.6.3 | Purge secret fields from `AppSettings` + `load_unified()` | Code-only |
| v2.6.4 | `SettingsViewModel` reads/writes via keyring | Code-only |
| v2.6.5 | Settings UI masked entry fields + hint labels | Code-only |
| v2.6.6 | Runtime key consumption in `dsclinic.py`, `api_gemini/`, `api_claude/` | Code-only |
| v2.6.7 | Rotate keys, `git rm settings.ini`, final audit | Manual + code |

---

## Reference Architecture: GASSI Keyring Pattern

Study these two GASSI files before implementing:
- `proj_gassi2/src/gassi/core/ai/factory.py` — `_KEYRING_SERVICE`, `_PROVIDER_KEYRING_USERNAME`, `get_api_key()`
- `proj_gassi2/src/gassi/views/settings_dialog.py` — keyring read in `_refresh_provider_ui()`, keyring write in `_save()`

| GASSI | DSClinic |
|---|---|
| `_KEYRING_SERVICE = "gassi"` | `_KEYRING_SERVICE = "dsclinic"` |
| `get_api_key(provider: AiProvider)` | `get_credential(name: str)` |
| `keyring.get_password("gassi", "gemini_api_key")` | `keyring.get_password("dsclinic", "gemini_api_key")` |
| Settings reads key from keyring on open | `SettingsViewModel.__init__` reads from `get_credential(...)` |
| Settings writes key to keyring on save | `SettingsViewModel.save_to_config()` calls `set_credential(...)` |

---

## New File: `src/models/keyring_manager.py` (v2.6.2)

```python
"""keyring_manager.py — Secure OS credential store access for DSClinic.

All API keys and sensitive project identifiers are stored in the OS-native
credential store (Windows Credential Manager / macOS Keychain / libsecret).
Nothing secret is ever written to disk or committed to the repository.

Service name: "dsclinic"
"""
import logging
import keyring

logger = logging.getLogger(__name__)

_KEYRING_SERVICE = "dsclinic"

_CREDENTIAL_KEYS: dict[str, str] = {
    "gemini":            "gemini_api_key",
    "anthropic":         "anthropic_api_key",
    "google_project_id": "google_project_id",
}


def get_credential(name: str) -> str | None:
    username = _CREDENTIAL_KEYS.get(name)
    if not username:
        logger.warning("get_credential: unknown credential name %r", name)
        return None
    value = keyring.get_password(_KEYRING_SERVICE, username)
    if not value:
        logger.warning("Credential %r not set in OS keyring.", name)
    return value


def set_credential(name: str, value: str) -> None:
    username = _CREDENTIAL_KEYS.get(name)
    if not username:
        logger.warning("set_credential: unknown credential name %r", name)
        return
    if not value.strip():
        logger.warning("set_credential: empty value for %r — skipping.", name)
        return
    keyring.set_password(_KEYRING_SERVICE, username, value.strip())
    logger.info("Credential %r saved to OS keyring.", name)


def delete_credential(name: str) -> None:
    username = _CREDENTIAL_KEYS.get(name)
    if not username:
        return
    try:
        keyring.delete_password(_KEYRING_SERVICE, username)
        logger.info("Credential %r deleted from OS keyring.", name)
    except keyring.errors.PasswordDeleteError:
        logger.warning("Credential %r was not set — nothing to delete.", name)
```

---

## `AppSettings` Changes (v2.6.3)

Remove from the class body:
```python
# DELETE:
google_api_key: str = ""
anthropic_api_key: str = ""
```

Remove entire `configparser` block from `load_unified()`.

Add to `config.json`:
```json
"google": {
    "project_location": "us-central1"
}
```

Add normal field to `AppSettings` and read in `load_unified()`:
```python
google_project_location: str = "us-central1"
# In load_unified():
google_cfg = config_defaults.get("google", {})
merged_data["google_project_location"] = google_cfg.get("project_location", "us-central1")
```

---

## Previously Active Milestone (blocked): v2.5.0 Chat Session View

Full plan preserved in `TODO.md` under v2.5.0. Do not implement until v2.6.7 is committed.

**Streaming bug summary:** The trace on `var_response` in `ChatSessionView.__init__` calls `add_message()` on every write. Fix: track `self._current_bot_bubble: Optional[MarkdownLabel]`; on first chunk create one bubble and hold the reference; on subsequent chunks call `_current_bot_bubble.update_text(full_text)` in-place; clear the reference when `var_is_analyzing` transitions to `False`.
