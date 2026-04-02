"""
AppDatabase — single access point for all JSON file-based collections.

Directory layout (relative to project root app_data/):
    app_data/
    ├── sessions/
    │   ├── _index.json             [{id, session_id, report_date, patient_name}]
    │   └── {session_id}.json       full ChatSessionModel
    ├── reports/
    │   ├── _index.json             [{id, report_id, report_date, patient_name}]
    │   └── {report_id}.json        full MedicalReport
    └── ai_profiles/
        ├── gemini/
        │   ├── _index.json         [{id, model_name}]
        │   └── {name}.json         GeminiModelConfig
        └── claude/
            ├── _index.json         [{id, model_name}]
            └── {name}.json         ClaudeModelConfig

Usage:
    from db import AppDatabase

    db = AppDatabase()

    # sessions
    db.sessions.save(session.session_id, session)
    session = db.sessions.load(session_id)
    entries  = db.sessions.list_index()   # fast — no full records loaded

    # reports
    db.reports.save(report.report_id, report)

    # AI profiles
    db.gemini_profiles.save("default", gemini_cfg)
    db.claude_profiles.save("default", claude_cfg)
"""
from __future__ import annotations

from pathlib import Path

from models import (
    ChatSessionModel,
    ClaudeModelConfig,
    GeminiModelConfig,
    MedicalReport,
)
from npy.core.utils import get_base_dir_path

from .json_collection import JsonCollection


class AppDatabase:
    """Central access point for all persistent JSON collections."""

    def __init__(self, base_dir: Path | None = None) -> None:
        _root = base_dir or (Path(get_base_dir_path()) / "app_data")

        self.sessions: JsonCollection[ChatSessionModel] = JsonCollection(
            dir_path=_root / "sessions",
            model_class=ChatSessionModel,
            index_fields=["session_id", "report.report_date", "report.content.patient_name"],
        )

        self.reports: JsonCollection[MedicalReport] = JsonCollection(
            dir_path=_root / "reports",
            model_class=MedicalReport,
            index_fields=["report_id", "report_date", "content.patient_name"],
        )

        self.gemini_profiles: JsonCollection[GeminiModelConfig] = JsonCollection(
            dir_path=_root / "ai_profiles" / "gemini",
            model_class=GeminiModelConfig,
            index_fields=["model_name"],
        )

        self.claude_profiles: JsonCollection[ClaudeModelConfig] = JsonCollection(
            dir_path=_root / "ai_profiles" / "claude",
            model_class=ClaudeModelConfig,
            index_fields=["model_name"],
        )
