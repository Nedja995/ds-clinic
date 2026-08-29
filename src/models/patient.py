import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from npy.core.utils import get_input_data_dirpath

class MedicalCriticalFindingModel(BaseModel):
    """Model representing a critical finding in a medical report, including the finding description, expert opinion, and original parameter values."""
    expertsko_misljenje: str = Field(default="", description="Expert opinion, diagnosis, explanation of the problem, and its cause. Highlight severity if applicable.")
    parametar_and_value: str = Field(default="", description="The specific medical parameter and its measured value (e.g., 'Glucose 7.8 mmol/L' or 'D=0.004').")


class MedicalReportModel(BaseModel):
    """Model representing the structured content of a medical report, including patient information, recommended therapy, and critical findings."""
    patient_name: str = Field(default="", description="Full name of patient.")
    recommended_therapy_and_advice: str = Field(default="", description="Comprehensive summary including: root cause analysis, diagnosis summary, recommended therapy, lifestyle advice, and next steps.")
    critical_findings: list[MedicalCriticalFindingModel] = Field(default=[], description="List of all critical or notable medical findings with expert opinions and raw parameter values.")


class MedicalTherapyModel(BaseModel):
    """Model representing a recommended therapy for a medical report, including the Medical Articles and Using Instructions."""
    article: str = Field(default="", description="Name of the medical article supporting the recommended therapy.")
    using_instructions: str = Field(default="", description="Instructions on how to use the recommended therapy, based on the medical article.")


class MedicalReport(BaseModel):
    """
    Model representing a complete medical report, including metadata such as report ID and date,
    the structured content of the report, and any chat responses from the AI analysis.
    """
    report_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    report_date: str = Field(description="Datum izveštaja.", default_factory=lambda: datetime.now().strftime('%d.%m.%Y.'))
    input_dir: str = Field(description="Input directory path.", default_factory=get_input_data_dirpath)
    content: MedicalReportModel = Field(default_factory=MedicalReportModel)
    therapies: list[MedicalTherapyModel] = Field(default_factory=list)
    chat_responses: list[str] = Field(default_factory=list)
