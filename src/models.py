from pydantic import BaseModel, Field
import uuid
from datetime import datetime


class GeminiModelConfig(BaseModel):
    model_name: str = Field(default="gemini-3-pro-preview")
    temperature: float = Field(default=1.0)
    top_p: float = Field(default=0.95)
    top_k: int = Field(default=40)
    max_output_tokens: int = Field(default=65535)
    thinking_level: str = Field(default="HIGH")
    system_instruction: tuple = Field(default=(
        "You are an expert medical data analyst using equally both holistic and traditional medical data.",
        "Always highlight severe abnormalities."))


class AIServiceConfig(BaseModel):
    """Gemini service config — kept for backward compatibility with dsclinic.py."""
    api_key: str = Field(default="")
    model_settings: GeminiModelConfig = Field(default_factory=GeminiModelConfig)


class MedicalCriticalFindingModel(BaseModel):
    expertsko_misljenje: str = Field(default="",description="Expert opinion, diagnosis, explanation of the problem, and its cause. Highlight severity if applicable.")
    parametar_and_value: str = Field(default="",description="The specific medical parameter and its measured value (e.g., 'Glucose 7.8 mmol/L' or 'D=0.004')."
    )

class MedicalReportModel(BaseModel):
    patient_name: str = Field(
        default="",
        description="Full name of the patient extracted from the documents."
    )
    recommended_therapy_and_advice: str = Field(default="",description="Comprehensive summary including: root cause analysis, diagnosis summary, recommended therapy, lifestyle advice, and next steps.")
    critical_findings: list[MedicalCriticalFindingModel] = Field(default=[],description="List of all critical or notable medical findings with expert opinions and raw parameter values.")

class MedicalReport(BaseModel):
    report_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    report_date: str = Field(description="Datum izveštaja.", default_factory=lambda: datetime.now().strftime("%Y-%m-%d_%H-%M"))
    content: MedicalReportModel = Field(default=MedicalReportModel)

class ChatMessage(BaseModel):
    content: str = Field(description="The content of the message.")
    timestamp: datetime = Field(default_factory=datetime.now)

class ChatSessionModel(BaseModel):
    session_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    model_settings: GeminiModelConfig = Field(default=GeminiModelConfig)
    report: MedicalReport = Field(default=MedicalReport)
    chat_history: list[ChatMessage] = Field(default=[])


# ---------------------------------------------------------------------------
# Claude (Anthropic) model config — mirrors GeminiModelConfig
# Note: Claude has no top_k or thinking_level params.
#       Extended thinking is opt-in via thinking_budget_tokens > 0.
# ---------------------------------------------------------------------------
class ClaudeModelConfig(BaseModel):
    model_name: str = Field(default="claude-3-5-sonnet-20241022")
    temperature: float = Field(default=1.0)
    top_p: float = Field(default=0.95)
    max_output_tokens: int = Field(default=8096)
    # Extended thinking: set > 0 to enable (requires compatible model, e.g. claude-3-7-sonnet)
    thinking_budget_tokens: int = Field(default=0)
    system_instruction: tuple = Field(default=(
        "You are an expert medical data analyst using equally both holistic and traditional medical data.",
        "Always highlight severe abnormalities."))


class ClaudeAIServiceConfig(BaseModel):
    """Anthropic-specific service config. Mirrors AIServiceConfig for Gemini."""
    api_key: str = Field(default="")
    model_settings: ClaudeModelConfig = Field(default_factory=ClaudeModelConfig)


