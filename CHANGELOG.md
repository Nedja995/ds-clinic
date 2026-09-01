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
## [2.7.0] - In Progress — Patient Record as First-Class Entity & Session Persistence

---

## [2.7.3] - 2026-09-01

### Added
- `src/dsclinic_gui/session_history_view.py` — new `SessionHistoryView(ttk.Frame)` sidebar widget. Subscribes to `on_sessions_changed`; rebuilds `tk.Listbox` from `var_sessions_index` on every update. Clicking a row calls `view_model.load_session(session_id)`. "New Session" button calls `view_model.new_session()`. Empty-state label shown when no sessions exist yet.
- `src/dsclinic_gui/report_view_models.py` — `var_sessions_index: list[dict]` attribute, populated from `_db.sessions.list_index()` on init and refreshed after every `_persist_session()` call.
- `src/dsclinic_gui/report_view_models.py` — `on_sessions_changed: EventEmitter` — fired whenever `var_sessions_index` is refreshed.
- `src/dsclinic_gui/report_view_models.py` — `_refresh_sessions_index()`: reloads index from disk and emits `on_sessions_changed`.
- `src/dsclinic_gui/report_view_models.py` — `load_session(session_id: str)`: loads `ChatSessionModel` from DB, replaces `_model` and `_session`, emits `on_vm_data_changed`.
- `src/dsclinic_gui/report_view_models.py` — `new_session()`: resets all model/session/observable state to defaults, emits `on_vm_data_changed`.
- `src/dsclinic_gui/styles.py` — `SIDEBAR_BG`, `SIDEBAR_STRIP` palette constants; `SidebarPanel.TFrame`, `SidebarStrip.TFrame`, `SidebarTitle.TLabel`, `SidebarEmpty.TLabel` style definitions.

### Changed
- `src/dsclinic_gui/main_container.py` — three-pane layout: `SessionHistoryView` (weight=2) added as leftmost pane; `MedicalReportView` weight reduced from 8 to 6 to preserve proportional feel. Module and class docstrings added.
- `src/dsclinic_gui/report_view_models.py` — `_persist_session()` now calls `_refresh_sessions_index()` after every save so the sidebar stays current.
- `pyproject.toml` — `session_history_view.py` and `main_container.py` added to `[tool.mypy]` exclude list (View-layer files, deferred to rewrite milestones).

---

## [2.7.2] - 2026-09-01

### Added
- `dsclinic_gui/report_view_models.py` — `self._db: AppDatabase` instantiated once in `DSClinicViewModel.__init__`.
- `dsclinic_gui/report_view_models.py` — `self._session: ChatSessionModel` tracks the active session wrapping the current report and chat history.
- `dsclinic_gui/report_view_models.py` — `self._pending_question: str` stashes the submitted question text so the `FINISHED` handler can build the `ChatMessage` pair without re-reading the (already-cleared) `StringVar`.
- `dsclinic_gui/report_view_models.py` — `_persist_report()`: saves `MedicalReport` to `_db.reports` on analysis completion. Failures logged and swallowed — never propagate to UI.
- `dsclinic_gui/report_view_models.py` — `_persist_session()`: re-saves `ChatSessionModel` to `_db.sessions` after analysis completion and after each Q&A exchange. Syncs `session.report` to current model state before writing.
- `dsclinic_gui/report_view_models.py` — `_apply_progress_event` `FINISHED/MedicalReport` branch: calls `_persist_report` + creates fresh `ChatSessionModel` + calls `_persist_session` immediately after analysis.
- `dsclinic_gui/report_view_models.py` — `_apply_progress_event` `FINISHED/str` branch: appends question + answer `ChatMessage` pair to `_session.chat_history`, clears `_pending_question`, calls `_persist_session`.

### Changed
- `dsclinic_gui/report_view_models.py` — `followup_question_submit()`: stashes question into `self._pending_question` before clearing `var_initial_question`.

---

## [2.7.1] - 2026-09-01

### Added
- `src/models/patient.py` — `PatientRecord(BaseModel)` with fields: `patient_id` (uuid4 hex), `full_name`, `date_of_birth`, `created_at`, `session_ids: list[str]`. First-class persistent entity per AD-18.
- `src/db/app_database.py` — `patients: JsonCollection[PatientRecord]` collection at `app_data/patients/`. Index fields: `patient_id`, `full_name`, `created_at`.
- `src/models/__init__.py` — `PatientRecord` exported from the models package.

### Changed
- `src/models/patient.py` — added module-level docstring explaining ownership boundary and AD-18 join key contract.
- `src/db/app_database.py` — updated module docstring to include `patients/` in directory layout and usage examples.

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
