# DSClinic Development Guidelines & Project Context (GEMINI.md)

Welcome to the **DSClinic** project workspace. This file serves as the definitive reference for team-shared architecture, conventions, workflows, and guidelines for developer and AI-driven contributions. 

All development must rigorously adhere to the specifications and patterns described below.

---

## 1. Project Overview & Scope

**DSClinic** is a medical document analysis application designed for holistic medical clinics.
* **Core Functionality:** Analyzes patient documents (laboratory results, medical records, and holistic software exports like MetaHunter) using advanced AI models. It processes initial inquiries, generates structured clinical analyses, allows interactive chat with AI for refinement, and compiles the final clinical findings into polished PDF reports.
* **Evolution:** 
  * **v1.0 (CLI):** Fully operational command-line interface.
  * **v2.0 (GUI):** A Windows-first, cross-platform (Windows & macOS) desktop application built with Python and Tkinter, introducing a rich, responsive, and intuitive graphical user interface.
  * **Migration:** Actively transitioning from an MVC architecture to a robust, strict **MVVM (Model-View-ViewModel)** architecture to support interactive features like real-time streaming chat and dual-panel views.

---

## 2. Technical Stack

* **Language:** Python 3 (developed primarily on Windows 10/11, compatible with macOS).
* **UI Framework:** Standard `tkinter` and `tkinter.ttk` (themed Tkinter).
* **AI Service SDKs:** Native integration with **Google Gemini (`google-genai`)** and **Anthropic Claude (`anthropic`)** SDKs. Proxy/wrapper layers (such as liteLLM) are intentionally avoided to minimize overhead and allow direct tuning of model-specific parameters.
* **PDF Engine:** `FPDF2` for high-quality, structured document rendering.
* **Data Validation:** `Pydantic v2` for all core models, app state, settings, and structured JSON serialization.
* **Storage:** Local file-based JSON collection engine (`src/db/`) acting as a structured document database under `app_data/`.
* **Packaging & Builds:** Virtual environment managed by standard `venv` or `poetry`, linting/formatting via `ruff`, type-checking via `mypy --strict`, testing via `pytest`, and desktop distribution using `PyInstaller`.

---

## 3. Core Architectural Rules

To maintain high maintainability and prevent regressions, all code must follow these core principles:

### A. Strict MVVM (Model-View-ViewModel) Pattern
* **The View Layer (`src/dsclinic_gui/*_view.py`):**
  * Responsible *only* for layout, visual presentation, and direct event bindings.
  * Translates raw events into ViewModel actions.
  * Strictly uses `ttk` themed widgets for uniform styling, with only three documented exceptions for standard `tk` widgets:
    1. `tk.Canvas` (for drawing / custom graphics)
    2. `scrolledtext.ScrolledText` (for multi-line text input/output)
    3. `tk.StringVar` / `tk.IntVar` / `tk.BooleanVar` (for UI reactive state)
  * View classes must never perform business logic, validation, direct file operations, or background processing.
* **The ViewModel Layer (`src/dsclinic_gui/*_view_models.py`):**
  * Exposes state cleanly using `tk.StringVar`/`IntVar`/`BooleanVar` properties for reactive bindings with the View.
  * Owns the complete lifecycle of background tasks.
  * **Zero Widget Imports:** ViewModel classes must **never** import or interact with Tkinter *widgets* (e.g., `Label`, `Button`, `Frame`).
  * **No Dialog Ownership:** ViewModels must never open dialogs, files, or message boxes directly (e.g., calling `filedialog.askopenfilename` or `messagebox.showinfo`). Instead, use a callback/delegate pattern: define a two-step prepare/execute operation, or pass a delegate function from the View layer.
  * The only Tkinter coupling allowed is injecting `root.after()` or a scheduling helper (`schedule_poll_fn`) to coordinate polling loops on the main thread.
* **The Model Layer (`src/models.py`, `src/models_new/`):**
  * Fully decoupled domain schemas using Pydantic v2.
  * Defines the shape of patient data, clinic settings, session state, and diagnostic findings.

### B. Threading & Non-Blocking GUI Discipline
* Any long-running operation (AI calls, complex file processing, PDF generation) **must run on a background thread** (`threading.Thread`).
* **Main Thread Only for UI:** Worker threads must **never** touch Tkinter UI components or update widget properties directly.
* **Queue-Based Communication:** 
  * Background workers must communicate status/progress back to the main thread *exclusively* by writing structured statuses (`running`, `progress`, `canceled`, `finished`, `failed`) into a `queue.Queue`.
  * **Do Not Generate Events:** Background threads must never call `event_generate()` on Tkinter widgets, as this can crash the UI loop or cause race conditions.
  * **Main Thread Polling:** The View or ViewModel on the main thread must poll the queue regularly using `root.after(ms, poll_method)`.

### C. JSON Database Layer
* **Location:** `src/db/`
* **Implementation:** Built as a generic `JsonCollection[T]` engine mapped to a typed `AppDatabase` class.
* **Behavior:** Stores records under `app_data/` in per-record JSON files with a central `_index.json` tracker for performance-efficient listings.
* Operations include: `save()`, `load()`, `delete()`, `exists()`, `list_index()`, `list_all()`, `count()`, and index rebuilding options.

### D. Coding Conventions & Quality Standards
* **Edits Prefer Pattern-Matching:** Targeted, surgical edits that match local code style are strongly preferred over large-scale, unprompted visual/logical refactorings.
* **Warnings & Strict Typing:** Never bypass the type system or disable warnings. Use explicit type hints. `mypy --strict` compliance is expected.
* **Language/Locale:** Standard application labels, diagnostics, and reports are rendered in Serbian (`sr`). 
* **Localization Updates:** After modifying strings, compile them using:
  ```cmd
  pybabel compile -d resources/locale -D app
  ```

---

## 4. MVVM Implementation Template (Reference)

When writing a new feature with dual panels, streaming, or background tasks, use this standard pattern:

### A. Model Schema (Pydantic v2)
```python
from pydantic import BaseModel, Field
from typing import List, Optional

class FindingItem(BaseModel):
    parameter: str
    value: str
    status: str
    explanation: Optional[str] = None

class PatientReport(BaseModel):
    patient_name: str
    diagnosis: str
    findings: List[FindingItem] = Field(default_factory=list)
```

### B. ViewModel Layer (Non-blocking, Queue + Polling)
```python
import queue
import threading
from typing import Callable, Dict, Any
import tkinter as tk

class AnalysisViewModel:
    def __init__(self, database: Any, schedule_poll_fn: Callable[[int, Callable[[], None]], None]):
        self.db = database
        self.schedule_poll = schedule_poll_fn
        
        # Reactive UI state variables
        self.patient_name_var = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="Ready")
        self.progress_var = tk.DoubleVar(value=0.0)
        
        # Communication queue
        self.queue: queue.Queue[Dict[str, Any]] = queue.Queue()
        self.is_running = False

    def start_analysis(self, doc_path: str) -> None:
        if self.is_running:
            return
        self.is_running = True
        self.status_var.set("Analyzing...")
        self.progress_var.set(10.0)
        
        # Start background worker
        thread = threading.Thread(target=self._worker_run, args=(doc_path,), daemon=True)
        thread.start()
        
        # Schedule main-thread polling
        self.schedule_poll(100, self._poll_queue)

    def _worker_run(self, doc_path: str) -> None:
        try:
            # Simulate or execute AI analysis using direct SDK
            # Write progress back to the main thread safely
            self.queue.put({"status": "progress", "value": 50.0, "message": "Analyzing lab values..."})
            
            # Simulated result
            self.queue.put({
                "status": "finished",
                "patient_name": "Kristina Cakić",
                "message": "Analysis completed successfully."
            })
        except Exception as e:
            self.queue.put({"status": "failed", "error": str(e)})

    def _poll_queue(self) -> None:
        try:
            while True:
                msg = self.queue.get_nowait()
                status = msg.get("status")
                
                if status == "progress":
                    self.progress_var.set(msg["value"])
                    self.status_var.set(msg["message"])
                elif status == "finished":
                    self.patient_name_var.set(msg["patient_name"])
                    self.status_var.set(msg["message"])
                    self.progress_var.set(100.0)
                    self.is_running = False
                elif status == "failed":
                    self.status_var.set(f"Error: {msg['error']}")
                    self.progress_var.set(0.0)
                    self.is_running = False
                
                self.queue.task_done()
        except queue.Empty:
            pass
            
        # Continue polling if background operation is still active
        if self.is_running:
            self.schedule_poll(100, self._poll_queue)
```

### C. View Layer (Themed Widgets & Bindings)
```python
import tkinter as tk
from tkinter import ttk
from typing import Any

class AnalysisView(ttk.Frame):
    def __init__(self, parent: tk.Widget, view_model: Any):
        super().__init__(parent)
        self.vm = view_model
        self.create_widgets()
        self.bind_view_model()

    def create_widgets(self) -> None:
        # Parent layout / Container Frame
        container = ttk.LabelFrame(self, text=" Patient Document Analysis ")
        container.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Label bound to StringVar
        self.name_label = ttk.Label(container, text="Patient:")
        self.name_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.name_display = ttk.Label(container, textvariable=self.vm.patient_name_var, font=("Arial", 11, "bold"))
        self.name_display.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        # Progress elements
        self.status_lbl = ttk.Label(container, textvariable=self.vm.status_var)
        self.status_lbl.grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)

        self.progress_bar = ttk.Progressbar(container, variable=self.vm.progress_var, maximum=100)
        self.progress_bar.grid(row=2, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=5)

        # Action Buttons
        self.analyze_btn = ttk.Button(container, text="Run Analysis", command=self.on_run_analysis)
        self.analyze_btn.grid(row=3, column=0, columnspan=2, pady=10)

    def bind_view_model(self) -> None:
        # Additional reactive bindings or style changes can be handled here.
        pass

    def on_run_analysis(self) -> None:
        # Retrieve context from View elements if needed, then invoke VM action
        target_doc = "ULAZ/KRISTINA CAKIC.pdf"
        self.vm.start_analysis(target_doc)
```

---

## 5. Development & Build Commands

### Environment Setup
Create and activate the virtual environment:
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate.bat

# macOS/Linux
python -m venv .venv
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### PyInstaller Compilation Rules
Windows distribution executable binaries are built using these exact PyInstaller CLI directives. Maintainers must match these CLI definitions:

```bash
# Compile CLI executable:
pyinstaller --noconfirm --onefile --console --name "DSClinic_v2_0_1" --paths "src" src/dsclinic_cli.py

# Compile Windows GUI App executable:
pyinstaller --noconfirm --onefile --windowed --name "MedAI Assistant - ViTec" --paths "src" src/dsclinic_gui/dsclinic_gui_app.py

# Compile GUI App executable with custom asset files and icons:
pyinstaller --noconfirm --onefile --windowed --name "Holisticki Centar Dar Prirode - Izvestaji" --icon "src/assets/icon.ico" --add-data "src/assets/icon.ico;." --paths "src" src/dsclinic_gui/dsclinic_gui_app.py
```

---

*Note: This GEMINI.md file is a core project file and should be modified with care to reflect updated team agreements and architectural evolutions.*
