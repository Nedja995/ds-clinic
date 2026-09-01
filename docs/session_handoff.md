# DSClinic — Master Session Handoff & AI Entry Point

Read this before starting any work. It captures everything needed to continue development without going through previous chat history.

---

> [!IMPORTANT]
> **CRITICAL AI SYSTEM DIRECTIVES (MANDATORY):**
> Before writing, proposing, or refactoring any code for this session, you MUST read, cross-reference, and strictly adhere to **Section 3.G (AI Coding Assistant System Directives)** inside `GEMINI.md`.

---

## Key Docs — Read On Demand, Not Upfront

- `TODO.md` — roadmap and task status
- `CHANGELOG.md` — version history
- `docs/architecture.md` — AD-01 through AD-21
- `GEMINI.md` — project-wide coding guidelines
- `.dev_profile/developer_profile.md` — standing workflow and commenting rules

---

## AI Coding Assistant Directives

1. **Defensive Error Handling:** No bare `except:`. All thread failures → `TaskStatus.FAILED` queue. All `src/db/` and keyring calls wrapped.
2. **GDPR:** All patient data through Presidio before external transmission. Credentials via `keyring_manager.py` only.
3. **MVVM:** Zero `tkinter`/`ttk` imports in ViewModels. Complete type annotations on all new code.
4. **Commenting:** Follow `.dev_profile/developer_profile.md` §6. Explain *why*, not *what*. Module/class docstrings on all new files.
5. **Toolchain:** `uv` + `pyproject.toml` (AD-21). `uv sync --group dev`, `uv run mypy src/`, `uv run pytest`, `uv run pyinstaller ...`.
6. **Multi-Brand:** All identity/commercial config via `BrandConfig` (v2.11.0). Never hardcode clinic names.

---

## Version & Commit Discipline

```bash
git add <exact files changed>
git commit -m "vX.Y.Z: <imperative description>"
git push
```

| File | When |
|---|---|
| `CHANGELOG.md` | Every sub-version |
| `TODO.md` | Every sub-version |
| `pyproject.toml` version | Every sub-version |
| `docs/session_handoff.md` | Every sub-version |
| `docs/architecture.md` | Any design decision |
| `.dev_profile/developer_profile.md` | Any standing rule change |

---

## Current Status: v2.5.0 ✅ Complete — Next: v2.7.0

| Version | Scope | Status |
|---|---|---|
| v2.5.1 | MVVM boundary audit | ✅ Done |
| v2.5.2 | Defensive error handling audit | ✅ Done |
| v2.5.3 | `mypy --strict` type hints audit | ✅ Done |
| v2.5.4 | `pyproject.toml` + `uv` migration, README | ✅ Done |
| v2.7.0 | Patient records + session persistence | ▶ Next |
| v2.8.0 | `src/providers/` LLMProvider abstraction | Planned |
| v2.9.0 | Groq + Together + HuggingFace providers | Planned |
| v2.10.0 | Local Ollama provider | Planned |
| v2.11.0 | BrandConfig + white-label + subscription | Planned |
| v2.12.0 | Chat Session View rewrite | Planned |
| v2.13.0 | pytest coverage | Planned |
| v2.14.0 | PII improvements + debug panel | Planned |
| v2.15.0 | README case study + architecture diagrams | Planned |

---

## v2.5.4 Changes (completed 2026-09-01)

- `pyproject.toml` — single source of truth for all tool config: `[tool.mypy]`, `[tool.pytest.ini_options]`, `[tool.autopep8]`, `[dependency-groups] dev`, `[project.optional-dependencies]` (`claude`, `local`, `providers` extras), full runtime dep set with version pins, `requires-python`, `authors`, `readme`, `license`.
- `mypy.ini` — **deleted** (manually: `git rm mypy.ini`). Config moved to `[tool.mypy]` in `pyproject.toml`.
- `README.md` — full rewrite: `uv` workflow, keyring setup, run/mypy/pytest/pyinstaller commands, project structure, architecture overview.

**Manual action required:**
```powershell
git rm mypy.ini
```

---

## v2.7.0 Implementation Notes

Files to read before starting:
- `src/db/app_database.py` — add `patients: JsonCollection[PatientRecord]` collection here.
- `src/models/patient.py` — add `PatientRecord(BaseModel)` here.
- `src/models/__init__.py` — export `PatientRecord`.
- `src/dsclinic_gui/report_view_models.py` — wire `AppDatabase` as `self._db`.

---

## Key Existing Code Context

- `src/db/app_database.py` — implemented, not yet wired to ViewModel (v2.7.0).
- `src/db/json_collection.py` — `JsonCollection[T]`, fully typed and guarded.
- `src/models/ai.py` — `ChatSessionModel`, `GeminiModelConfig`, `ClaudeModelConfig`.
- `src/models/patient.py` — `MedicalReport` exists; `PatientRecord` added in v2.7.1.
- PII anonymization — working, over-anonymizes clinical values; fix in v2.14.0.

---

## Previously Completed

- **v2.6.0** ✅ — Credentials to OS keyring, `settings.ini` deleted.
- **v2.5.0** ✅ — MVVM audit, error handling, `mypy --strict` clean, `uv` migration.
