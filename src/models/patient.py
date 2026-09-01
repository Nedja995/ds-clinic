"""
Patient domain models.

Owns: MedicalReportModel, MedicalCriticalFindingModel, MedicalTherapyModel,
      MedicalReport, PatientRecord.

PatientRecord is a first-class persistent entity (AD-18). A patient recurs
across multiple visits; a MedicalReport is the output of a single session.
The two are joined via ChatSessionModel.session_id stored in
PatientRecord.session_ids.

Does NOT own: session state, AI config, settings — those live in ai.py /
settings.py.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from npy.core.utils import get_input_data_dirpath


class MedicalCriticalFindingModel(BaseModel):
    """A single critical or notable finding extracted from the report."""

    expertsko_misljenje: str = Field(
        default="",
        description=(
            "Expert opinion, diagnosis, explanation of the problem, and its cause. "
            "Highlight severity if applicable."
        ),
    )
    parametar_and_value: str = Field(
        default="",
        description=(
            "The specific medical parameter and its measured value "
            "(e.g., 'Glucose 7.8 mmol/L' or 'D=0.004')."
        ),
    )


class MedicalReportModel(BaseModel):
    """Structured content of a single medical report returned by the AI layer."""

    patient_name: str = Field(default="", description="Full name of patient.")
    recommended_therapy_and_advice: str = Field(
        default="",
        description=(
            "Comprehensive summary including: root cause analysis, diagnosis summary, "
            "recommended therapy, lifestyle advice, and next steps."
        ),
    )
    critical_findings: list[MedicalCriticalFindingModel] = Field(
        default_factory=list,
        description="List of all critical or notable medical findings with expert opinions and raw parameter values.",
    )


class MedicalTherapyModel(BaseModel):
    """A single therapy recommendation attached to a report."""

    article: str = Field(
        default="",
        description="Name of the medical article supporting the recommended therapy.",
    )
    using_instructions: str = Field(
        default="",
        description="Instructions on how to use the recommended therapy, based on the medical article.",
    )


class MedicalReport(BaseModel):
    """
    Complete medical report: metadata + structured AI content + chat history.

    report_id is the primary key used by JsonCollection[MedicalReport].
    """

    report_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    report_date: str = Field(
        description="Datum izveštaja.",
        default_factory=lambda: datetime.now().strftime("%d.%m.%Y."),
    )
    input_dir: str = Field(
        description="Input directory path.",
        default_factory=get_input_data_dirpath,
    )
    content: MedicalReportModel = Field(default_factory=MedicalReportModel)
    therapies: list[MedicalTherapyModel] = Field(default_factory=list)
    chat_responses: list[str] = Field(default_factory=list)


class PatientRecord(BaseModel):
    """
    First-class persistent entity representing a recurring clinic patient (AD-18).

    A patient may have many visits. Each visit produces a ChatSessionModel
    (keyed by session_id) and a MedicalReport (keyed by report_id).
    session_ids is the join list linking this patient to the sessions collection
    in AppDatabase.

    patient_id is the primary key used by JsonCollection[PatientRecord].
    """

    patient_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    full_name: str = Field(default="", description="Patient full name.")
    date_of_birth: str = Field(default="", description="Date of birth (DD.MM.YYYY.).")
    created_at: str = Field(
        default_factory=lambda: datetime.now().strftime("%d.%m.%Y."),
    )
    # Session IDs from AppDatabase.sessions — ordered newest-first by convention.
    session_ids: list[str] = Field(default_factory=list)
