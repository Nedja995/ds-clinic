# DSClinic — Medical AI Analysis & Report Platform

Enterprise-grade B2B desktop application for clinical document analysis and structured medical report generation. Built with Python, Tkinter/ttk, Pydantic v2, and a pluggable multi-provider AI inference pipeline (Gemini, Claude, Groq, Together AI, HuggingFace, Ollama).

> **Status:** Active development — v2.5.x MVVM audit & type-safety pass complete. See [CHANGELOG.md](CHANGELOG.md) and [TODO.md](TODO.md) for the full roadmap.

---

## Requirements

- Python 3.12 (exact — `requires-python = ">=3.12,<3.13"`)
- [uv](https://docs.astral.sh/uv/) — package manager and virtual environment tool
- Windows 10/11 (primary target); Linux/macOS supported for development

---

## Developer Setup

All commands use `uv`. It manages the virtual environment and lockfile automatically — no manual `python -m venv` or `pip install` needed.

### 1. Install uv

```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Create the virtual environment and install dependencies

```bash
# Install runtime deps + dev tools (mypy, pytest, pyinstaller)
uv sync --group dev

# Also install the Claude backend (optional — needed if using ClaudeProvider)
uv sync --group dev --extra claude

# Also install local Ollama inference support (optional)
uv sync --group dev --extra local

# Install all extras at once
uv sync --group dev --extra claude --extra local --extra providers
```

`uv sync` reads `pyproject.toml`, resolves the full dependency graph, writes `uv.lock`, and creates `.venv/` — all in one step. Re-run whenever `pyproject.toml` changes.

### 3. Download spaCy language models

The PII anonymization pipeline (Presidio + spaCy) requires a spaCy NER model at runtime:

```bash
uv run python -m spacy download en_core_web_sm
```

### 4. Set API credentials

Credentials are stored in the OS keyring — never in any file on disk. Enter them via **Settings → AI** in the running application, or set them directly from a Python shell:

```python
from models.keyring_manager import set_credential
set_credential("gemini", "your-google-api-key")
set_credential("anthropic", "your-anthropic-api-key")  # optional
```

---

## Running the Application

```bash
# GUI application (primary entry point)
uv run python src/dsclinic_gui/dsclinic_gui_app.py

# CLI entry point (batch/headless analysis)
uv run python src/dsclinic_cli.py
```

---

## Development Workflows

### Type checking

```bash
uv run mypy src/
```

mypy configuration lives in `[tool.mypy]` inside `pyproject.toml`. Strict mode is enabled. A curated exclude list covers View-layer files and untyped third-party wrappers deferred to their rewrite milestones.

### Running tests

```bash
uv run pytest
```

Test configuration lives in `[tool.pytest.ini_options]` inside `pyproject.toml`. Test suite location: `tests/`. See [TODO.md](TODO.md) v2.13.0 for the full planned coverage matrix.

### Adding a dependency

```bash
# Runtime dependency
uv add some-package

# Dev-only dependency
uv add --group dev some-tool

# Optional extra
uv add --optional claude anthropic
```

Commit both `pyproject.toml` and `uv.lock` after any dependency change.

---

## Building a Release (Windows Executable)

The application is distributed as a standalone `.exe` compiled with PyInstaller. No Python installation is required on the end-user machine.

```bash
# Standard windowed release (no console window)
uv run pyinstaller \
    --noconfirm \
    --onefile \
    --windowed \
    --name "MedAI Assistant - ViTec" \
    --paths "src" \
    src/dsclinic_gui/dsclinic_gui_app.py

# With application icon
uv run pyinstaller \
    --noconfirm \
    --onefile \
    --windowed \
    --name "MedAI Assistant - ViTec" \
    --icon "src/assets/icon.ico" \
    --add-data "src/assets/icon.ico;." \
    --paths "src" \
    src/dsclinic_gui/dsclinic_gui_app.py

# CLI build (console window, for headless/batch use)
uv run pyinstaller \
    --noconfirm \
    --onefile \
    --console \
    --name "DSClinic-CLI" \
    --paths "src" \
    src/dsclinic_cli.py
```

Output lands in `dist/`. Distribute the `.exe` alongside `config.json` and (for white-label builds) `brand.json` + the clinic logo asset.

---

## Project Structure

```
ds-clinic/
├── src/
│   ├── api_gemini/          # Gemini SDK wrapper (raw client layer)
│   ├── api_claude/          # Anthropic SDK wrapper (raw client layer)
│   ├── db/                  # JsonCollection[T] local document store
│   ├── models/              # Pydantic models, AppSettings, keyring_manager
│   ├── dsclinic_gui/        # Tkinter/ttk MVVM GUI (Views + ViewModels)
│   │   ├── settings/        # Settings window (View + ViewModel)
│   │   └── widgets/         # Shared widget components
│   ├── npy/                 # Shared utility library
│   └── dsclinic.py          # Core business logic (DSClinic class)
├── docs/
│   ├── architecture.md      # Architecture Decision Records (AD-01 – AD-21)
│   └── session_handoff.md   # AI session continuity document
├── .dev_profile/
│   └── developer_profile.md # Standing development conventions
├── pyproject.toml           # Single source of truth: metadata, deps, tool config
├── uv.lock                  # Pinned dependency lockfile (commit this)
├── mypy.ini                 # DELETED — config moved to [tool.mypy] in pyproject.toml
├── CHANGELOG.md
└── TODO.md
```

---

## Architecture Overview

DSClinic is built around a **Split-Horizon Hybrid Inference Pipeline**:

```
Input (PDF / Lab Images / DICOM)
        │
        ▼
┌─────────────────────────────────┐
│  Layer 1 — Privacy & Extraction │  ← Local: Presidio + spaCy + EasyOCR
│  PII scrubbed before any upload │    Optional: Ollama (Llama 3.2 Vision,
└───────────────┬─────────────────┘    MedGemma 7B @ 4-bit quantization)
                │ Anonymized structured JSON only
                ▼
┌─────────────────────────────────┐
│  Layer 2 — Reasoning & Synthesis│  ← Cloud: Gemini Pro / Claude
│  Receives zero PII              │    or: Groq / Together / HuggingFace
└───────────────┬─────────────────┘
                │
                ▼
        Structured MedicalReport
        + PDF export + Session history
```

Key architectural decisions are documented in [`docs/architecture.md`](docs/architecture.md) (AD-01 through AD-21).

---

## Gemini CLI (AI-assisted development)

```bash
# Install
npm install -g @google/gemini-cli

# Set API key (Windows PowerShell)
[System.Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "your-key-here", "User")

# Set API key (macOS / Linux — add to ~/.zshrc or ~/.bashrc)
export GEMINI_API_KEY="your-key-here"
```

---

## Translations

```bash
uv run pybabel compile -d resources/locale -D app
```
