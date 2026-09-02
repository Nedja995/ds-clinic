"""keyring_manager.py — Secure OS credential store access for DSClinic.

All API keys and sensitive project identifiers are stored exclusively in
the OS-native credential store (Windows Credential Manager, macOS Keychain,
libsecret on Linux) via the `keyring` library.

Nothing secret is ever written to any file on disk. All other modules call
get_credential / set_credential / delete_credential — nothing imports
`keyring` directly outside this module.

Service name : "dsclinic"
Credential keys (logical name → keyring username):
    "gemini"            → "gemini_api_key"
    "anthropic"         → "anthropic_api_key"
    "google_project_id" → "google_project_id"
    "groq"              → "groq_api_key"
    "together"          → "together_api_key"
    "huggingface"       → "huggingface_api_key"

See: docs/architecture.md AD-11
"""

import logging

import keyring
import keyring.errors

logger = logging.getLogger(__name__)

_KEYRING_SERVICE = "dsclinic"

_CREDENTIAL_KEYS: dict[str, str] = {
    "gemini":            "gemini_api_key",
    "anthropic":         "anthropic_api_key",
    "google_project_id": "google_project_id",
    # v2.9.1 — OpenAI-compatible cloud providers (text-only, Split-Horizon Layer 1/2)
    "groq":              "groq_api_key",
    "together":          "together_api_key",
    "huggingface":       "huggingface_api_key",
}


def get_credential(name: str) -> str | None:
    """Read a credential from the OS keyring.

    Returns the stored string, or None if the credential is not set, the
    name is unknown, or the keyring backend is unavailable. Callers must
    handle the None case (e.g. show a warning in the UI before attempting
    an API call).
    """
    _username = _CREDENTIAL_KEYS.get(name)
    if _username is None:
        logger.warning("get_credential: unknown credential name %r", name)
        return None
    try:
        _value = keyring.get_password(_KEYRING_SERVICE, _username)
    except keyring.errors.KeyringError as e:
        logger.error("get_credential: keyring unavailable for %r: %s", name, e, exc_info=True)
        return None
    if not _value:
        logger.warning("Credential %r is not set in OS keyring.", name)
    return _value or None


def set_credential(name: str, value: str) -> None:
    """Write a credential to the OS keyring.

    Silently skips empty or whitespace-only values — never writes a blank
    entry that would shadow a previously stored key. Logs an error and
    returns without raising if the keyring backend is unavailable.
    """
    _username = _CREDENTIAL_KEYS.get(name)
    if _username is None:
        logger.warning("set_credential: unknown credential name %r", name)
        return
    _clean = value.strip()
    if not _clean:
        logger.warning("set_credential: empty value for %r — skipping.", name)
        return
    try:
        keyring.set_password(_KEYRING_SERVICE, _username, _clean)
        logger.info("Credential %r saved to OS keyring.", name)
    except keyring.errors.KeyringError as e:
        logger.error("set_credential: keyring unavailable for %r: %s", name, e, exc_info=True)


def delete_credential(name: str) -> None:
    """Remove a credential from the OS keyring.

    Safe to call even if the credential was never set — logs a warning and
    returns silently rather than raising.
    """
    _username = _CREDENTIAL_KEYS.get(name)
    if _username is None:
        logger.warning("delete_credential: unknown credential name %r", name)
        return
    try:
        keyring.delete_password(_KEYRING_SERVICE, _username)
        logger.info("Credential %r deleted from OS keyring.", name)
    except keyring.errors.PasswordDeleteError:
        logger.warning("delete_credential: %r was not set — nothing to delete.", name)
    except keyring.errors.KeyringError as e:
        logger.error("delete_credential: keyring unavailable for %r: %s", name, e, exc_info=True)
