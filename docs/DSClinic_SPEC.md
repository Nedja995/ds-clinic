# DSClinic — Project Specification

**Version:** 0.1-draft  
**Date:** 2026-03-28  
**Based on:** `ds-clinic_03_04_2026` (current), `dc-clinic2` (reference origin)  
**Stack:** Python 3.12+, Tkinter/ttk, FPDF2, Pydantic v2, Google GenAI SDK, Anthropic SDK

---

## 1. Purpose & Domain

DSClinic is a **Windows-first desktop application** for holistic medical clinics. It automates the analysis of patient medical documents (lab results, holistic device scans, reports) using AI (Google Gemini or Anthropic Claude), and produces a structured, branded PDF report for the patient.

The primary user is a **medical therapist / clinic operator** — not a developer. The app must be distributable as a single `.exe`, require no Python installation, and support Serbian Unicode text throughout.

---

## 2. Evolution Overview

| Version | Folder | Key Characteristics |
|---|---|---|
| v0.1 — Prototype | `dc-clinic2` | Single file Tkinter, raw text I/O, Gemini only, no structured output, basic PDF |
| v0.9 — Refactor | `ds-clinic-refactoring-v0_9` | MVC split started, Gemini streaming, FPDF2 PDF |
| v1.x — Stable | `ds-clinic` | CLI + GUI, Gemini streaming JSON, MVVM in GUI |
| v2.x — Current | `ds-clinic_03_04_2026` | Dual AI (Gemini + Claude), MVVM, ttk styling, `config.json` driven |

---

## 3. High-Level Architecture

```
[Entry Points]
  dsclinic_cli.py          — CLI, batch mode, no GUI
  dsclinic_gui_app.py      — GUI entry point (Tkinter)

[Core Logic]
  dsclinic.py              — Orchestration: load docs → call AI → return MedicalReport
  pdf_maker.py             — FPDF2 PDF rendering

[AI Services]
  api_gemini/client.py     — Google GenAI streaming client
  api_claude/client.py     — Anthropic streaming client

[Data / Models]
  models.py                — All Pydantic models (domain + AI config + status)
  config.py                — Config loader (JSON + INI + TOML)
  config.json              — Runtime config (AI models, tasks, flags)
  settings.ini             — Secrets (API keys, app version)

[GUI — MVVM]
  dsclinic_gui/
    dsclinic_gui_app.py    — App shell (tk.Tk subclass), wires VM ↔ View
    report_view_models.py  — ViewModel: observables, threading, worker queue
    report_view.py         — View: ttk widgets, styles, layout
    chat_session_view.py   — (Partial) Chat follow-up panel

[Utilities]
  npy/core/utils.py        — Base/resource/input/output path resolution (PyInstaller-safe)
  npy/core/fileutils.py    — Document discovery, file I/O, debug dump
  npy/core/logger.py       — Logging setup
  gui_widgets/dialogs.py   — Shared dialog helpers
```

**Pattern:** MVVM strictly in the GUI layer. No UI imports in `dsclinic.py`, `models.py`, or API clients. Worker threads → `queue.Queue` → `root.after()` polling → ViewModel updates → View reacts to `tk.StringVar` / `tk.BooleanVar` / `tk.DoubleVar` observables.

---

## 4. Data Models (`models.py`)

All models use **Pydantic v2** (`BaseModel`). Used for runtime validation, JSON serialization, and as API response schemas.

### 4.1 Domain Models

```python
MedicalCriticalFindingModel
  expertsko_misljenje: str      # Expert opinion + diagnosis
  parametar_and_value: str      # Raw parameter + value (e.g. "Glucose 7.8 mmol/L")

MedicalReportModel
  patient_name: str
  recommended_therapy_and_advice: str
  critical_findings: list[MedicalCriticalFindingModel]

MedicalReport
  report_id: str                # uuid hex, auto-generated
  report_date: str              # datetime string "%Y-%m-%d_%H-%M"
  content: MedicalReportModel
```

### 4.2 AI Config Models

```python
GeminiModelConfig
  model_name: str
  temperature: float
  top_p: float
  max_output_tokens: int
  thinking_level: str           # "HIGH" | "MEDIUM" | "LOW"
  system_instruction: tuple

ClaudeModelConfig
  model_name: str
  temperature: float
  top_p: float
  max_output_tokens: int
  thinking_budget_tokens: int   # 0 = disabled; >0 enables extended thinking
  system_instruction: tuple

AIServiceConfig                 # Gemini wrapper
  api_key: str
  model_settings: GeminiModelConfig
  chat_history: ChatSessionModel

ClaudeAIServiceConfig           # Anthropic wrapper
  api_key: str
  model_settings: ClaudeModelConfig
```

### 4.3 Session / Chat Models

```python
ChatMessage
  content: str
  timestamp: datetime

ChatSessionModel
  session_id: str               # uuid hex
  model_settings: GeminiModelConfig
  report: MedicalReport
  chat_history: list[ChatMessage]
```

### 4.4 Worker Status Enum

```python
class WorkerStatus(str, Enum):
  RUNNING  = "running"
  PROGRESS = "progress"
  FINISHED = "finished"
  CANCELED = "cancelled"
  FAILED   = "failed"
```

---

## 5. Configuration System (`config.py`)

Three-tier config loaded at startup:

| File | Format | Contains |
|---|---|---|
| `settings.ini` | INI | `APP_VERSION`, `APP_NAME`, API keys (`GOOGLE_API_KEY`, `ANTHROPIC_API_KEY`) |
| `config.json` | JSON | AI model names, task descriptions, debug flags, supported models list |
| `pyproject.toml` | TOML | Project version (secondary source) |

### 5.1 `config.json` Structure (current)

```json
{
  "app": {
    "log_level": "DEBUG",
    "debug_export_response": true,
    "debug_response": false
  },
  "ai_system_instructions": [...],
  "ai_initial_model_config": { "name": "...", "temperature": ..., "top_p": ..., "top_k": ... },
  "ai_initial_task_key": "TASK_1",
  "ai_task_descriptions": {
    "TASK_1": { "name": "...", "description": [...] }
  },
  "ai_supported_models": { "model-key": "model-api-id", ... },
  "claude_initial_model_config": { "name": "...", "temperature": ..., ... },
  "claude_supported_models": { "model-key": "model-api-id", ... },
  "SUPPORTED_EXTENSIONS": { "mime/type": ".ext", ... }
}
```

### 5.2 Resolved Config Properties (in `config.py`)

| Property | Source | Description |
|---|---|---|
| `APP_VERSION` | `settings.ini[APP]` | App version string |
| `GOOGLE_API_KEY` | `settings.ini[GOOGLE]` | Google API key |
| `ANTHROPIC_API_KEY` | `settings.ini[ANTHROPIC]` | Anthropic API key |
| `AI_MODEL_NAME` | `config.json.ai_initial_model_config.name` | Active Gemini model |
| `AI_TASK_DESCRIPTION` | `config.json.ai_task_descriptions[ai_initial_task_key]` | Initial prompt |
| `AI_SUPPORTED_MODELS` | `config.json.ai_supported_models` | Model picker list |
| `CLAUDE_MODEL_NAME` | `config.json.claude_initial_model_config.name` | Active Claude model |
| `AI_SUPPORTED_INPUT_FILETYPES` | `config.py` (hardcoded dict) | Accepted MIME → ext |

---

## 6. File System Layout (Runtime)

```
<app_root>/              ← get_base_dir_path() — PyInstaller-safe
  config.json
  settings.ini
  pyproject.toml
  resources/
    logo.png
    fonts/
      Arial-Unicode-Regular.ttf
      Arial-Unicode-Bold.ttf
      Arial-Unicode-Italic.ttf
      Arial-Unicode-Bold-Italic.ttf
  ULAZ/                   ← input documents (PDF, images, TXT, CSV…)
  IZVESTAJI/              ← output PDF reports
    DEBUG/                ← debug JSON dumps (when debug_export_response=true)
      sample_response.json   (debug fixture)
  logs/                   ← log files
```

Path resolution uses `npy/core/utils.py::get_base_dir_path()` — handles both `python script.py` (walks up from `__file__`) and frozen PyInstaller `.exe` (`sys.executable` dir).

---

## 7. AI Service Layer

### 7.1 Gemini Client (`api_gemini/client.py`)

- Uses `google-genai` native SDK (`genai.Client`, `chats.create()`)
- **Stateful chat session** (`ChatSession`) — client-side abstraction; full context sent on every request
- Streaming via `chat_session.send_message_stream()`
- **Structured output:** `response_schema=MedicalReportModel` + `response_mime_type="application/json"` in `GenerateContentConfig`
- Tools: `GoogleSearch` enabled in base config; overridden to strict JSON for initial analysis call
- Safety settings: all 4 harm categories set to `OFF` (medical domain)
- Thinking config: `ThinkingConfig(thinking_level=...)` from model config

**Initial analysis flow:**
1. Load documents as `genai_types.Part` list (via `api_gemini/utils.py`)
2. Build message: `[intro_text, ...doc_parts, question_text]`
3. Stream with overridden JSON config → accumulate → `MedicalReportModel.model_validate_json()`

### 7.2 Claude Client (`api_claude/client.py`)

- Uses `anthropic` native SDK (`anthropic.Anthropic`, `messages.stream()`)
- **Stateless API** — `chat_history: list[dict]` maintained manually, sent on every call
- System prompt includes **embedded JSON schema** (`_build_system_prompt()`) because Claude has no `response_schema` param
- Streaming via `client.messages.stream()` → `stream.text_stream`
- Markdown fence stripping on response (```` ```json ``` ```` guard)
- Documents sent only on first call; follow-up calls use text-only history → cost optimized

**Cost note:** JSON schema embedded in system prompt ≈ 600–900 extra tokens/request. Both providers transmit full context per request — no real statefulness difference between them.

### 7.3 Document Loading

- `api_gemini/utils.py`: reads file → `genai_types.Part` (base64 inline data with MIME type)
- `api_claude/utils.py`: reads file → Anthropic content block dict `{"type": "document", "source": {...}}`
- Supported types: `pdf`, `txt`, `xml`, `csv`, `rtf`, `jpeg`, `png`, `bmp`, `webp`, `json`, `html`

---

## 8. PDF Generation (`pdf_maker.py`)

Uses **FPDF2** with custom Unicode fonts (Arial Unicode MS family).

**Class `HolisticReport(FPDF)`** — A4 portrait, mm units:

| Method | Renders |
|---|---|
| `draw_header()` | Clinic title (centered), logo (left), horizontal rule |
| `draw_patient_info(name, date)` | Patient name (left) + date (right) on same row |
| `draw_table(data)` | Dynamic-height two-column table: Mišljenje / Parametar; auto page-break |
| `draw_footer_section(text)` | Therapy text, consent note, legal disclaimer, therapist signature line |

**`export_medical_report_pdf(report, output_filename)`** — public entry point, wraps `generate_report_pdf()`.

**`generate_report_pdf_bytes(report)`** — returns PDF as bytes (for in-memory use / future API endpoint).

---

## 9. GUI Layer — MVVM

### 9.1 `DSClinicAppGUI` (App Shell, `dsclinic_gui_app.py`)

- Subclass of `tk.Tk`
- Wires `MedicalReport` → `DSClinicViewModel` → `DSClinicView`
- Entry point validates / constructs `MedicalReport` from dict or object

### 9.2 `DSClinicViewModel` (`report_view_models.py`)

**Observables (tk vars, bound directly to View widgets):**

| Variable | Type | Purpose |
|---|---|---|
| `patient_name` | `tk.StringVar` | Patient name field |
| `report_date` | `tk.StringVar` | Date field |
| `therapy_text_content` | `str` | Manual sync (ScrolledText has no StringVar) |
| `findings` | `list[MedicalCriticalFindingModel]` | Manual sync (complex widget list) |
| `status_title` | `tk.StringVar` | Footer left label |
| `status_detail` | `tk.StringVar` | Footer right label |
| `progress_value` | `tk.DoubleVar` | Progressbar |
| `is_analyzing` | `tk.BooleanVar` | Analysis active flag |
| `btn_analyze_text` | `tk.StringVar` | Toggle button label |

**Threading:**
- `_start_analysis()` → `threading.Thread(target=_run_task_initial_analyzis, daemon=True)`
- Worker writes `{"status": "...", "result": ...}` to `queue.Queue`
- `_check_queue_loop()` polls via `root.after(QUEUE_POLL_INTERVAL_MS)` (1000ms)
- Status messages: `"complete"` | `"failed"` | `"cancelled"` | `"processing"`

> **Known Bug:** `"processing"` status incorrectly sets `status_title` to `"Failed"` instead of `"Processing..."` in `_check_queue_loop`.

**Commands:**
- `toggle_analysis()` — start / cancel worker
- `add_finding()` — append blank `MedicalCriticalFindingModel`
- `remove_finding(index)` — pop from findings list
- `save_report()` — sync VM → model → `filedialog.asksaveasfilename` → `export_medical_report_pdf()`

### 9.3 `DSClinicView` (`report_view.py`)

**Theme:** `ttk` / `clam` theme throughout. Three documented `tk.*` exceptions:
- `tk.Canvas` — scrollable container (no ttk equivalent)
- `scrolledtext.ScrolledText` — rich text areas
- `tk.StringVar` / `tk.BooleanVar` / `tk.DoubleVar` — always tk

**Layout:**
```
root (tk.Tk)
  PanedWindow (horizontal)
    left_pane
      Toolbar.TFrame      [Analyze | Export | Details | Settings]
      Shadow.TFrame       (2px drop shadow)
      Canvas (scrollable)
        scrollable_frame
          Card: "Podaci o pacijentu"   [Ime | Datum]
          Card: "Preporučena terapija" [ScrolledText 9 rows]
          Card: "Nalazi"               [THead row | Rows container | + Dodaj nalaz btn]
      Footer.TFrame       [ProgressBar | StatusKey | StatusDetail]
    # right_pane (ChatSessionView) — commented out, not yet active
```

**Color Palette** (all centralized as module-level constants):
```
BG=#F0F4F8  PANEL=#FFFFFF  TOOLBAR=#1E2D3D  ACCENT=#1A6FA8
TEXT=#1C2B3A  DANGER=#C62828  THEAD_BG=#DCE8F0  ROW_A/B alternating
```

**Key methods:**
- `_build_styles()` — single source of truth for all ttk.Style definitions
- `_render_finding_row(index, finding)` — builds one row in `nalazi_container`
- `refresh_view_from_vm()` — tears down and rebuilds findings rows from VM state
- `sync_view_to_vm()` — reads ScrolledText content → updates VM (must be called before any VM command that needs current text)

### 9.4 `ChatSessionView` (`chat_session_view.py`)

Currently stubbed — layout built but `Ask` button has no command connected. Planned right pane for the `PanedWindow`.

---

## 10. Persistence & Storage (Specification — Required Design)

Currently the app uses only `config.json` (read-only at runtime) and flat file I/O for PDFs. The following JSON-based local storage system is **required** for the next major version:

### 10.1 Storage Files

All stored under `<app_root>/data/` (created on first run):

```
data/
  app_state.json          # Last used paths, window geometry, last model selection
  sessions/
    <session_id>.json     # Full session record (see §10.3)
  sessions_index.json     # Lightweight index of all sessions (for history list)
```

### 10.2 `app_state.json` Schema

```json
{
  "last_input_dir": "...",
  "last_output_dir": "...",
  "last_active_provider": "gemini",       // "gemini" | "claude"
  "last_model_gemini": "gemini-2.5-flash",
  "last_model_claude": "claude-3-5-sonnet-20241022",
  "last_task_key": "TASK_1",
  "window": { "width": 620, "height": 700, "x": null, "y": null },
  "ui": { "theme": "clam", "language": "sr" }
}
```

### 10.3 Session Record `sessions/<session_id>.json`

```json
{
  "session_id": "uuid-hex",
  "created_at": "ISO-8601",
  "updated_at": "ISO-8601",
  "provider": "gemini",
  "model_config": {
    "model_name": "gemini-2.5-flash",
    "temperature": 1.0,
    "top_p": 0.95,
    "max_output_tokens": 65535
  },
  "task_key": "TASK_1",
  "input_documents": ["filename1.pdf", "filename2.pdf"],
  "report": { /* MedicalReport.model_dump() */ },
  "chat_history": [
    { "role": "user",      "content": "...", "timestamp": "ISO-8601" },
    { "role": "assistant", "content": "...", "timestamp": "ISO-8601" }
  ],
  "tokens_used": { "input": 0, "output": 0 },
  "exported_pdf_path": null
}
```

### 10.4 `sessions_index.json`

```json
[
  {
    "session_id": "uuid-hex",
    "created_at": "ISO-8601",
    "patient_name": "Marko Marković",
    "provider": "gemini",
    "model_name": "gemini-2.5-flash",
    "exported_pdf_path": "/path/to/report.pdf"
  }
]
```

### 10.5 AI Config Data (`config.json` extensions needed)

The `config.json` should be extended to be the single source of supported models metadata:

```json
{
  "ai_providers": {
    "gemini": {
      "display_name": "Google Gemini",
      "api_key_ini_key": "GOOGLE_API_KEY",
      "supported_models": [
        {
          "id": "gemini-2.5-flash",
          "display_name": "Gemini 2.5 Flash",
          "supports_thinking": true,
          "max_output_tokens": 65535
        }
      ]
    },
    "claude": {
      "display_name": "Anthropic Claude",
      "api_key_ini_key": "ANTHROPIC_API_KEY",
      "supported_models": [
        {
          "id": "claude-sonnet-4-5",
          "display_name": "Claude Sonnet 4.5",
          "supports_extended_thinking": false,
          "max_output_tokens": 8096
        }
      ]
    }
  }
}
```

---

## 11. CLI Mode (`dsclinic_cli.py`)

Batch/headless mode for scripting and testing. Entry point for the console `.exe` build.

Expected interface (based on `dsclinic.py` core):

```
dsclinic_cli.exe [--input <dir>] [--output <dir>] [--model <name>] [--provider gemini|claude]
```

Uses `get_initial_analysis_report()` → `write_report_pdf()` directly, no GUI.

---

## 12. Build & Distribution

### 12.1 PyInstaller Builds

```bash
# CLI (console window)
pyinstaller --noconfirm --onefile --console --name "DSClinic_v2_0_1" \
  --paths "src" src/dsclinic_cli.py

# GUI (no console)
pyinstaller --noconfirm --onefile --windowed --name "DSClinicGUI2" \
  --paths "src" src/dsclinic_gui/dsclinic_gui_app.py
```

PyInstaller spec files: `DSClinic_v2_0_1.spec`, `DSClinicGUI2.spec`

**Required data bundled in spec:**
- `resources/` (fonts + logo)
- `config.json`, `settings.ini`

### 12.2 Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

### 12.3 Key Dependencies

| Package | Use |
|---|---|
| `google-genai` | Gemini API |
| `anthropic` | Claude API |
| `fpdf2` | PDF generation |
| `pydantic` | Data models + validation |
| `tkinter` | GUI (stdlib) |
| `pyinstaller` | Distribution builds |

---

## 13. Known Issues / Technical Debt

| ID | Location | Description | Severity |
|---|---|---|---|
| BUG-01 | `report_view_models.py` `_check_queue_loop()` | `"processing"` status sets `status_title` to `"Failed"` instead of `"Processing..."` | Medium |
| BUG-02 | `report_view_models.py` `add_finding()` | `_update_vm_from_model` called without `()` — no-op reference | Low |
| DEBT-01 | `dsclinic.py` | Only Gemini provider wired in `get_initial_analysis_report()`; Claude path not yet switchable via `config.json` | High |
| DEBT-02 | `chat_session_view.py` | `Ask` button has no command; `ChatSessionView` not added to `PanedWindow` | Medium |
| DEBT-03 | `config.json` | Supported models stored as flat `dict[str, str]`; lacks metadata (max tokens, thinking support, display name) | Low |
| DEBT-04 | Storage | No session persistence — all analysis history lost on app close | High |
| DEBT-05 | Settings UI | No settings dialog; API keys and model selection require manual `settings.ini` / `config.json` edit | Medium |
| DEBT-06 | `models.py` | `AIServiceConfig.chat_history` is `ChatSessionModel` (not `list[ChatMessage]`) — inconsistent naming vs usage | Low |
| DEBT-07 | `report_view_models.py` `_update_view()` | Contains dead code with list-wrapped booleans (`is_analyzing = [True if ...]`) — never called from main path | Low |

---

## 14. Planned Features / Roadmap

### v2.1 — Storage & Sessions
- Implement `data/app_state.json` read/write (window geometry, last model, last dirs)
- Implement `data/sessions/<id>.json` per-session save
- Implement `data/sessions_index.json` index
- Session history list in UI (load previous analysis)

### v2.2 — Settings UI
- Settings dialog: API key entry (masked), provider switch, model picker (from `config.json`)
- Task description picker (from `ai_task_descriptions`)
- Save to `settings.ini` / `config.json` at runtime

### v2.3 — Chat Panel
- Wire `ChatSessionView` to the right pane of `PanedWindow`
- Connect `Ask` button → `vm.ask_followup(question)` → worker thread → append to chat history
- Stream response tokens to `txt_response` in real time

### v2.4 — Multi-Provider Switch
- Runtime provider toggle: Gemini ↔ Claude
- Shared interface via `AnalyzerClientProtocol` (structural subtyping)
- Route `get_initial_analysis_report()` based on selected provider

### v2.5 — Input Management
- Drag-and-drop document input
- File list UI (show loaded documents, allow remove before analysis)
- Multi-patient batch mode via CLI

### v3.0 — Optional Web UI
- FastAPI backend wrapping `dsclinic.py` core
- React/Vite frontend (reference: `googleai-react` in project tree)
- Session history via REST, PDF download endpoint

---

## 15. Serbian Unicode Requirements

- All UI labels in Serbian (Latin script): `Podaci o pacijentu`, `Nalazi`, `Mišljenje`, etc.
- PDF uses **Arial Unicode MS** family (4 variants) for full diacritic support: `š`, `č`, `ć`, `ž`, `đ`
- AI responses always requested in Serbian via system instruction
- `json.dump(..., ensure_ascii=False)` enforced for all file writes
- `ttk` / `clam` theme respects foreground/background overrides cross-platform and renders Cyrillic/Latin correctly

---

*End of specification — DSClinic v2.x*
