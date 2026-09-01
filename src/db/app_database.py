"""
AppDatabase — single access point for all JSON file-based collections.

Directory layout (relative to project root app_data/):
    app_data/
    ├── patients/
    │   ├── _index.json             [{id, patient_id, full_name, created_at}]
    │   └── {patient_id}.json       full PatientRecord
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

    # patients (AD-18)
    db.patients.save(patient.patient_id, patient)
    patient = db.patients.load(patient_id)
    entries  = db.patients.list_index()   # fast — no full records loaded

    # sessions
    db.sessions.save(session.session_id, session)
    session = db.sessions.load(session_id)

    # reports
    db.reports.save(report.report_id, report)
"""
from __future__ import annotations

from pathlib import Path

from models import (
    ChatSessionModel,
    ClaudeModelConfig,
    GeminiModelConfig,
    MedicalReport,
    PatientRecord,
)
from npy.core.utils import get_base_dir_path

from .json_collection import JsonCollection


class AppDatabase:
    """Central access point for all persistent JSON collections."""

    def __init__(self, base_dir: Path | None = None) -> None:
        _root = base_dir or (Path(get_base_dir_path()) / "app_data")

        # Patients are the top-level entity (AD-18); stored before sessions/reports
        # so the directory layout reflects the data hierarchy.
        self.patients: JsonCollection[PatientRecord] = JsonCollection(
            dir_path=_root / "patients",
            model_class=PatientRecord,
            index_fields=["patient_id", "full_name", "created_at"],
        )

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
