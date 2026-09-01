# Changelog

All notable changes to DSClinic will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

See [TODO.md](TODO.md) for planned versions.

---

## [2.15.0] - Planned — README Engineering Case Study + Architecture Diagrams
## [2.14.0] - Planned — PII Anonymization Improvements + Debug Panel
## [2.13.0] - Planned — pytest Coverage
## [2.12.0] - Planned — Chat Session View Rewrite + New Features
## [2.11.0] - Planned — Enterprise Multi-Brand / White-Label & Subscription Config
## [2.10.0] - Planned — Local Ollama Provider (16GB VRAM Optimized)
## [2.9.0] - Planned — Groq + Together AI + HuggingFace Cloud Providers
## [2.8.0] - Planned — `src/providers/` LLMProvider Abstraction (Gemini + Claude)
## [2.7.0] - Planned — Patient Record as First-Class Entity & Session Persistence

---

## [2.5.4] - 2026-09-01

### Added
- `pyproject.toml` — migrated all tool configuration into `pyproject.toml` as single source of truth: `[tool.mypy]` (replaces `mypy.ini`), `[tool.pytest.ini_options]`, `[tool.autopep8]`.
- `pyproject.toml` — added `requires-python = ">=3.12,<3.13"`, `authors`, `readme`, `license` fields (mirrors GASSI `pyproject.toml` convention, see AD-21).
- `pyproject.toml` — added `[project.optional-dependencies]`: `claude`, `local`, `providers` extras for opt-in backends.
- `pyproject.toml` — added `[dependency-groups] dev` with `mypy`, `pytest`, `pytest-mock`, `pyinstaller` (install with `uv sync --group dev`).
- `pyproject.toml` — added full runtime dependency set with version pins: `fpdf2`, `presidio-analyzer`, `presidio-anonymizer`, `spacy`, `easyocr`, `Pillow`, `pdf2image`.
- `README.md` — full rewrite: `uv`-based setup (`uv sync`, extras, spaCy model download), keyring credential setup, run commands, mypy, pytest, PyInstaller release builds, project structure, architecture overview.

### Removed
- `mypy.ini` — deleted; all mypy configuration now lives in `[tool.mypy]` inside `pyproject.toml`.
- `README.md` — removed outdated `pip` / `requirements.txt` / Poetry workflow references.

### Changed
- `pyproject.toml` — `[autopep8]` section key renamed to `[tool.autopep8]` (correct TOML tool namespace).

---

## [2.5.3] - 2026-09-01

### Fixed — `mypy --strict src/` now passes with 0 errors across 26 checked files
- `db/json_collection.py` — all bare `dict` replaced with `dict[str, Any]`; `_load_raw_index` return type explicit; `_build_index_entry` node traversal typed correctly.
- `models/ai.py` — `tuple` → `tuple[str, ...]` on both `system_instruction` fields.
- `models/diagnostics.py` — `UserList[T]` parameterised; `ObservableList` fully annotated (`__init__`, `extend`, `__setitem__`, `__delitem__`, `__iter__`).
- `api_gemini/client.py` — `chat_session: Optional[Any]` (SDK has no stable public chat session type); `-> None` added to all methods; `SafetySetting` uses enum members; `system_instruction` passed as `str`.
- `api_gemini/utils.py` — return type `Optional[types.Part]`; `None` initialiser removed.
- `api_claude/client.py` — unused `MessageParam` import removed (type doesn't exist in SDK); `user_content: Any` cast eliminates TypedDict mismatch; all bare `dict` type-args filled; `# type: ignore` codes corrected.
- `api_claude/utils.py` — `dict[str, Any]` throughout; `frozenset[str]` constants typed.
- `dsclinic.py` — `__init__` annotated `-> None`; `ask_followup_question` uses explicit `result: str` assignment to suppress `no-any-return`.
- `dsclinic_gui/report_view_models.py` — `callable` → `Callable[..., Any]`; `mp_input_queue`/`mp_output_queue` annotated as `multiprocessing.Queue[Any]`; `_` calls suppressed with `# type: ignore[name-defined]`.
- `dsclinic_gui/chat_session_view.py` — full annotations on `MarkdownLabel`; `_wheel` parameter typed as `Any`; `anchor` typed as `Literal["e", "w"]`; unused `Optional` import removed; unused `# type: ignore` comments removed.

### Added
- `mypy.ini` — created with `[mypy]` strict config and exclude list for View-layer files deferred to rewrite milestones.

### Removed
- `src/test_guis/` — removed from git tracking via `git rm -r src/test_guis/`.

---

## [2.5.2] - 2026-08-31

### Fixed
- `db/json_collection.py` — all four unguarded I/O sites wrapped in `try/except OSError` / `ValidationError`.
- `models/keyring_manager.py` — `get_credential()` and `set_credential()` wrapped in `keyring.errors.KeyringError`; `delete_credential()` gets additional `KeyringError` branch.
- `dsclinic.py` — `get_initial_analysis_report()`: `None` check on `report_content` before constructing `MedicalReport`; raises `RuntimeError` with user-readable message.

---

## [2.5.1] - 2026-08-31

### Fixed
- `report_view_models.py` — added `append_chat_response(text: str) -> None`; View must never mutate `_model` directly.
- `chat_session_view.py` — replaced direct `_model` mutation with `view_model.append_chat_response(text)`.
- `report_view_models.py` — `execute_export()` wraps PDF generation in `try/except`; emits `on_show_error_message` on failure.

### Changed
- Added `-> None` return type annotations to all previously unannotated ViewModel methods.

---

## [2.6.7] - 2026-08-30

### Security
- `settings.ini` permanently deleted. Both API keys regenerated and written to OS keyring.

---

## [2.6.0] - 2026-08-30 — Secure Credential Management & `settings.ini` Elimination ✅

### Security
- All API keys moved to OS keyring via `keyring_manager.py`. `settings.ini` deleted.

### Changed
- `app_name`/`app_version` sourced from `pyproject.toml` via `importlib.metadata`.
- `GOOGLE_PROJECT_LOCATION` moved to `config.json`.

---

## [2.3.0] - 2026-08-29

### Added
- Unified `src/models/` package. `AppSettings` Pydantic model. Layered `load_unified` / `save_unified`.

### Removed
- Legacy `src/models.py`, `src/models_new/`, `src/config.py`, `src/npy/core/settings_manager.py`.

---

## [2.1.10] - 2026-08-28

### Added
- "SUPPORT" card section in Settings window. Token-optimization filters in `dsclinic.py`.

### Fixed
- Nested-tuple serialization bug on multiple settings saves in `config.json`.
