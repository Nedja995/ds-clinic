"""
state_manager.py
----------------
Pydantic v2 settings + session state with JSON persistence.

Two separate files:
  - settings.json      → AppSettings  (API keys, paths, UI prefs)
  - session_state.json → SessionState (current report, chat history)

Usage:
    from state_manager import StateManager

    sm = StateManager()

    # Settings
    sm.settings.gemini_api_key = "..."
    sm.save_settings()

    # Session
    sm.session.patient_name = "Jane Doe"
    sm.session.chat_history.append(ChatMessage(role="user", content="Analyze this"))
    sm.save_session()

    # Reset session between analyses
    sm.reset_session()
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _app_data_dir() -> Path:
    """
    Resolve a cross-platform user data directory for storing JSON files.

    Windows : %APPDATA%/MedicalAnalyzer
    macOS   : ~/Library/Application Support/MedicalAnalyzer
    Linux   : ~/.local/share/MedicalAnalyzer  (fallback)
    """
    import sys
    if sys.platform == "win32":
        base = Path.home() / "AppData" / "Roaming"
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".local" / "share"

    directory = base / "MedicalAnalyzer"
    directory.mkdir(parents=True, exist_ok=True)
    return directory


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class GeminiModel(str, Enum):
    FLASH   = "gemini-2.0-flash"
    PRO     = "gemini-1.5-pro"
    FLASH_8B = "gemini-1.5-flash-8b"


class Theme(str, Enum):
    LIGHT  = "light"
    DARK   = "dark"
    SYSTEM = "system"


class MessageRole(str, Enum):
    USER      = "user"
    ASSISTANT = "assistant"
    SYSTEM    = "system"


# ---------------------------------------------------------------------------
# Sub-models shared between settings and session
# ---------------------------------------------------------------------------

class WindowGeometry(BaseModel):
    width:  int = 1100
    height: int = 750
    x:      int = 100
    y:      int = 100

    def as_tk_geometry(self) -> str:
        return f"{self.width}x{self.height}+{self.x}+{self.y}"

    @classmethod
    def from_tk_geometry(cls, geometry_str: str) -> "WindowGeometry":
        """Parse Tk geometry string like '1100x750+100+100'."""
        try:
            size, x, y = geometry_str.replace("+", "x").split("x")
            w, h = size.split("x") if "x" in size else (size, size)
            # geometry_str format: WxH+X+Y
            parts = geometry_str.split("+")
            w, h  = parts[0].split("x")
            return cls(width=int(w), height=int(h), x=int(parts[1]), y=int(parts[2]))
        except Exception:
            return cls()


# ---------------------------------------------------------------------------
# APP SETTINGS  →  settings.json
# ---------------------------------------------------------------------------

class AppSettings(BaseModel):
    """
    Persistent application configuration.
    Stored at: <app_data_dir>/settings.json
    """

    # --- API ---
    gemini_api_key: str = ""
    gemini_model:   GeminiModel = GeminiModel.FLASH
    gemini_temperature: float = Field(default=0.3, ge=0.0, le=2.0)

    # --- Paths ---
    last_input_dir:  str = ""   # last directory used when opening input docs
    last_output_dir: str = ""   # last directory used when saving PDF reports
    pdf_output_dir:  str = ""   # default PDF export directory (empty = ask each time)

    # --- UI ---
    theme:          Theme          = Theme.SYSTEM
    font_size:      int            = Field(default=11, ge=8, le=24)
    window_geometry: WindowGeometry = Field(default_factory=WindowGeometry)

    # --- Behaviour ---
    auto_save_session:   bool = True    # auto-save session state after each analysis step
    confirm_on_reset:    bool = True    # ask confirmation before clearing session
    max_chat_history:    int  = Field(default=50, ge=5, le=200)

    # --- Internal ---
    settings_version: int = 1

    @field_validator("gemini_api_key")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()

    @field_validator("last_input_dir", "last_output_dir", "pdf_output_dir")
    @classmethod
    def validate_path_exists_if_set(cls, v: str) -> str:
        if v and not Path(v).exists():
            logger.warning("Configured path no longer exists, clearing: %s", v)
            return ""
        return v


# ---------------------------------------------------------------------------
# SESSION STATE  →  session_state.json
# ---------------------------------------------------------------------------

class CriticalFinding(BaseModel):
    """One critical finding entry from the AI structured response."""
    description: str          # what is bad / why it matters
    parameter:   str          # e.g. "Glucose  7.8 mmol/L"


class AnalysisReport(BaseModel):
    """Structured AI response mapped from Gemini output."""
    patient_name:    str = ""
    summary:         str = ""   # expert analyse summary + recommendations
    critical_findings: list[CriticalFinding] = Field(default_factory=list)

    # Editable by the user before PDF export
    user_notes: str = ""

    @property
    def is_empty(self) -> bool:
        return not self.patient_name and not self.summary


class ChatMessage(BaseModel):
    role:      MessageRole
    content:   str
    timestamp: datetime = Field(default_factory=datetime.now)

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}


class InputDocument(BaseModel):
    """Tracks a file that was loaded for the current analysis."""
    path:        str
    filename:    str
    loaded_at:   datetime = Field(default_factory=datetime.now)
    file_type:   str = ""   # e.g. "pdf", "txt", "png"

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}


class SessionState(BaseModel):
    """
    Transient per-analysis state.
    Stored at: <app_data_dir>/session_state.json
    Reset between analyses.
    """

    # --- Source documents ---
    input_documents: list[InputDocument] = Field(default_factory=list)

    # --- AI conversation ---
    chat_history: list[ChatMessage] = Field(default_factory=list)

    # --- Report (draft, editable) ---
    report: AnalysisReport = Field(default_factory=AnalysisReport)

    # --- Status ---
    analysis_running: bool    = False
    last_error:       str     = ""
    session_started:  datetime | None = None
    last_saved:       datetime | None = None

    session_version: int = 1

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}

    @model_validator(mode="after")
    def trim_chat_history(self) -> "SessionState":
        """Enforce max_chat_history — called after load too."""
        # trimming is done by StateManager which knows the settings value
        return self

    @property
    def is_empty(self) -> bool:
        return not self.input_documents and self.report.is_empty and not self.chat_history

    def add_message(self, role: MessageRole, content: str) -> ChatMessage:
        msg = ChatMessage(role=role, content=content)
        self.chat_history.append(msg)
        return msg

    def add_input_document(self, path: str | Path) -> InputDocument:
        p = Path(path)
        doc = InputDocument(path=str(p), filename=p.name, file_type=p.suffix.lstrip(".").lower())
        self.input_documents.append(doc)
        return doc

    def apply_ai_response(self, raw: dict[str, Any]) -> None:
        """
        Merge a structured Gemini response dict into the report.
        Expected keys match your existing schema:
            patient_name, expert analyze summary..., critical_foundings
        """
        self.report.patient_name = raw.get("patient name", self.report.patient_name)
        self.report.summary      = raw.get(
            "expert analyze summary, recommendations", self.report.summary
        )
        findings_raw = raw.get("critical_foundings", [])   # note: keep your existing key name
        self.report.critical_findings = [
            CriticalFinding(
                description=list(f.keys())[0],
                parameter=list(f.values())[0],
            )
            for f in findings_raw if isinstance(f, dict) and f
        ]


# ---------------------------------------------------------------------------
# STATE MANAGER
# ---------------------------------------------------------------------------

class StateManager:
    """
    Central access point for settings and session state.

    Typical lifecycle:
        sm = StateManager()          # loads both files from disk
        sm.settings.gemini_api_key = "..."
        sm.save_settings()

        sm.session.add_message(MessageRole.USER, "Please analyse...")
        sm.save_session()

        sm.reset_session()           # wipe session, keep settings
    """

    SETTINGS_FILE = "settings.json"
    SESSION_FILE  = "session_state.json"

    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir: Path = data_dir or _app_data_dir()
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.settings: AppSettings = self._load(AppSettings, self.SETTINGS_FILE)
        self.session:  SessionState = self._load(SessionState, self.SESSION_FILE)

        logger.info("StateManager initialised. Data dir: %s", self.data_dir)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save_settings(self) -> None:
        self._save(self.settings, self.SETTINGS_FILE)

    def save_session(self) -> None:
        self._trim_chat_history()
        self.session.last_saved = datetime.now()
        self._save(self.session, self.SESSION_FILE)

    def save_all(self) -> None:
        self.save_settings()
        self.save_session()

    def reset_session(self) -> None:
        """Wipe session state and persist the empty state."""
        self.session = SessionState(session_started=datetime.now())
        self.save_session()
        logger.info("Session reset.")

    def start_session(self) -> None:
        """Call when the user begins a new analysis."""
        if not self.session.session_started:
            self.session.session_started = datetime.now()
        if self.settings.auto_save_session:
            self.save_session()

    @property
    def settings_path(self) -> Path:
        return self.data_dir / self.SETTINGS_FILE

    @property
    def session_path(self) -> Path:
        return self.data_dir / self.SESSION_FILE

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _load(self, model_cls: type[BaseModel], filename: str) -> BaseModel:
        path = self.data_dir / filename
        if path.exists():
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
                instance = model_cls.model_validate(raw)
                logger.debug("Loaded %s from %s", model_cls.__name__, path)
                return instance
            except Exception as exc:
                logger.warning(
                    "Could not load %s (%s). Using defaults. Backing up corrupt file.",
                    filename, exc
                )
                self._backup_corrupt(path)
        return model_cls()

    def _save(self, model: BaseModel, filename: str) -> None:
        path = self.data_dir / filename
        try:
            path.write_text(
                model.model_dump_json(indent=2),
                encoding="utf-8"
            )
            logger.debug("Saved %s to %s", type(model).__name__, path)
        except OSError as exc:
            logger.error("Failed to save %s: %s", filename, exc)

    def _trim_chat_history(self) -> None:
        max_msgs = self.settings.max_chat_history
        if len(self.session.chat_history) > max_msgs:
            self.session.chat_history = self.session.chat_history[-max_msgs:]

    @staticmethod
    def _backup_corrupt(path: Path) -> None:
        backup = path.with_suffix(f".corrupt{path.suffix}")
        try:
            path.rename(backup)
            logger.info("Corrupt file backed up to %s", backup)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Quick smoke test  (python state_manager.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    sm = StateManager()

    # Settings round-trip
    sm.settings.gemini_api_key = "test-key-123"
    sm.settings.gemini_model   = GeminiModel.PRO
    sm.save_settings()

    # Session round-trip
    sm.start_session()
    sm.session.add_input_document("/tmp/lab_results.pdf")
    sm.session.add_message(MessageRole.USER, "Please analyse the attached lab report.")
    sm.session.add_message(MessageRole.ASSISTANT, "Analysing...")
    sm.session.apply_ai_response({
        "patient name": "Jane Doe",
        "expert analyze summary, recommendations": "Patient shows elevated glucose...",
        "critical_foundings": [
            {"Elevated blood glucose above reference range": "Glucose 7.8 mmol/L"},
            {"Low haemoglobin indicating possible anaemia": "Hgb 10.2 g/dL"},
        ]
    })
    sm.save_session()

    # Reload and verify
    sm2 = StateManager()
    assert sm2.settings.gemini_api_key == "test-key-123"
    assert sm2.session.report.patient_name == "Jane Doe"
    assert len(sm2.session.report.critical_findings) == 2

    print("\n✓ All assertions passed.")
    print(f"  Settings : {sm2.settings_path}")
    print(f"  Session  : {sm2.session_path}")
    print(f"  Patient  : {sm2.session.report.patient_name}")
    print(f"  Findings : {len(sm2.session.report.critical_findings)}")