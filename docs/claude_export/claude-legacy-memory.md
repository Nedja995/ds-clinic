**Work context**

Ned is a software developer whose primary project is DSClinic, a medical document analysis application that uses Google Gemini models to analyze medical documents and produce structured, editable reports exportable as PDFs. He is currently building v2 as an "intuitive, readable, responsible GUI Tkinter app" where users can more easily review, edit, export, and use a new chat feature; v2 is moving from MVC to MVVM architecture. His development environment includes VS Code with the `sixth.sixth-ai` and "Gemini Code Assist" extensions, Desktop Commander MCP for filesystem access from Claude, and browser-based AI chat.

**Personal context**

Ned has hands-on familiarity with mobile hardware repair (terminology like test points, BROM, EDL, flat cable routing) and has an interest in mobile device servicing alongside his software development work.

**Top of mind**

Ned recently explored Claude Pro subscription mechanics in relation to Claude Code (CLI tool) and Claude for Desktop, understanding them as complementary tools. He was working through a workflow concern about context persistence across chats within a Claude Project, with `decisions.md` recommended as a carry-forward pattern — likely relevant to ongoing DSClinic v2 development under the project name DSClinic.

**Brief history**

*Recent months*

Ned worked on DSClinic v2 across several focused sessions. He requested and received a comprehensive Python project template (`dsclinic`) following 2026 best practices, with a `src/` layout, three integrated packages (`api_gemini`, `dsclinic_gui`, `dsclinic_cli`), full toolchain (`ruff`, `mypy --strict`, `pytest`, `hatchling`, PyInstaller), and cross-platform VSCode configuration. He also engaged in deep MVVM architecture work on the live codebase at `D:\__STORAGE\__DEV\__PROJECTS\DSKlinika\ds-clinic_03_04_2026`, including a Claude-assisted audit identifying ten MVVM violations and two refactoring sessions applying fixes via Desktop Commander: a two-step `prepare_export()`/`execute_export()` pattern delegating dialog ownership to the View, and elimination of a double-polling bug in the App class. He also explored a competitor analysis (for a product separate from DSClinic) but that conversation ended before the product was described. Ned prepared a phone listing on a Serbian marketplace (kupujemprodajem.com) and needed sensitive device identifiers blurred from screenshots — handled programmatically with PIL/Pillow.

*Earlier context*

Ned worked extensively on MVVM patterns for Python/Tkinter, building reference projects (`dsclinic2_example`, `dsclinic2_gui`) with established conventions: `tk.StringVar`/`IntVar`/`BooleanVar` for reactive state, `src/` layout, Pydantic v2 for all domain models, `threading` + `queue.Queue` for non-blocking background tasks with structured status reporting (`running`, `canceled`, `progress`, `finished`, `failed`), and `root.after()` injection to keep ViewModels free of direct Tkinter widget dependencies. He iterated on a complete five-element UI (Question input, Ask button, Answer field, Status label, progress bar) wired to a simulated 10-second background worker. A Pylance import resolution issue was resolved via `pyrightconfig.json`. He also worked on persistent JSON state management for DSClinic using Pydantic v2 (`AppSettings`, `SessionState`), with cross-platform data directory resolution and corrupt file backup handling. He caught and corrected a Pydantic v1 pattern (`json_encoders`) that had been included erroneously in generated code.

Ned confirmed his preference for Claude to "preserve my words verbatim where possible, especially for instructions and preferences," and prefers minimal, correctly scoped implementations that match exactly what was requested without added architectural layers.

*Long-term background*

Ned's earliest captured sessions involved DSClinic v1.0 — a CLI medical document analyzer that "went well" — and initial UI/UX wireframing for the Tkinter GUI, where he preferred sharing existing code directly for Claude to interpret rather than describing designs verbally. He explored embedding external applications in a technical project (details incomplete due to a missing screenshot) and asked foundational setup questions about Claude API keys and Claude Pro subscription tiers.

---

**Other instructions**

- "Preserve my words verbatim where possible, especially for instructions and preferences."
- DSClinic v1.0: "first cli app 1.0 that went well."
- DSClinic core feature: "main feature is google.genai Gemini models that are used to analyse medical docs (including holistic app exports) and give me structured report that i can edit and export in final medical pdf reports."
- DSClinic v2.0: "currently i am working on v2 of this app making intuitive, readable, responsible GUI Tkinter app user can easer review, edit, export and most import new feature chat should be implemented."
- DSClinic v2.0 architecture: "v2 are in mvc architecture but i must move to MVVC."
- UI/UX preference: prefers an "intuitive, readable, responsible GUI" for applications.