from typing import TypeVar, Generic, Callable
import uuid
from datetime import datetime
from enum import Enum
from collections import UserList
from pydantic import BaseModel, Field
import config


######################### Medical Report Models #########################
##
# Structured Service response models
#
class MedicalCriticalFindingModel(BaseModel):
    """Model representing a critical finding in a medical report, including the finding description, expert opinion, and original parameter values."""
    expertsko_misljenje: str                             = Field(default="",    description=config.AI_RESPONSE_CRITICAL_FINDING_EXPERTS_OPINION)
    parametar_and_value: str                             = Field(default="",    description=config.AI_RESPONSE_CRITICAL_FINDING_PARAM_AND_VALUE)

class MedicalReportModel(BaseModel):
    """Model representing the structured content of a medical report, including patient information, recommended therapy, and critical findings."""
    patient_name: str                                    = Field(default="",    description="Full name of patient.")
    recommended_therapy_and_advice: str                  = Field(default="",    description=config.AI_RESPONSE_RECOMMENDED_THERAPY_AND_ADVICE)
    critical_findings: list[MedicalCriticalFindingModel] = Field(default=[],    description=config.AI_RESPONSE_CRITICAL_FINDINGS)


######################### Additional report data #########################
##
class MedicalTherapyModel(BaseModel):
    """Model representing a recommended therapy for a medical report, including the Medical Articles and Using Instructions."""
    article:                str                             = Field(default="",    description="Name of the medical article supporting the recommended therapy.")
    using_instructions:     str                             = Field(default="",    description="Instructions on how to use the recommended therapy, based on the medical article.")


######################### FINAL REPORT MODEL #############################
#
class MedicalReport(BaseModel):
    """
    Model representing a complete medical report, including metadata such as report ID and date,
    the structured content of the report, and any chat responses from the AI analysis.
    """
    report_id:      str                       = Field(default_factory = lambda: uuid.uuid4().hex)
    report_date:    str                       = Field(description     = "Datum izveštaja.", default_factory = lambda: datetime.now().strftime('%d.%m.%Y.'))
    content:        MedicalReportModel        = Field(default         = MedicalReportModel)
    therapies:      list[MedicalTherapyModel] = Field(default         = [])
    chat_responses: list[str]                 = Field(default         = [])


####### AI Models

## Chat models
#
class ChatMessage(BaseModel):
    content:    str         = Field(description="The content of the message.")
    timestamp:  datetime    = Field(default_factory = datetime.now)

## AI Models Config
#
class GeminiModelConfig(BaseModel):
    model_name:         str     = Field(default = "gemini-3-pro-preview")
    temperature:        float   = Field(default = 1.0)
    top_p:              float   = Field(default = 0.95)
    #top_k:             int     = Field(default = 40)
    max_output_tokens:  int     = Field(default = 65535)
    thinking_level:     str     = Field(default = "HIGH")
    system_instruction: tuple   = Field(default = (
        "You are an expert medical data analyst using equally both holistic and traditional medical data.",
        "Always highlight severe abnormalities."
        )
    )


class ChatSessionModel(BaseModel):
    session_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    model_settings: GeminiModelConfig = Field(default=GeminiModelConfig)
    report: MedicalReport = Field(default=MedicalReport)
    chat_history: list[ChatMessage] = Field(default=[])



# This class likely represents a configuration model for an AI service.
class AIServiceConfig(BaseModel):
    """AI service config"""
    api_key: str = Field(default="")
    model_settings: GeminiModelConfig = Field(default_factory=GeminiModelConfig)
    chat_history: ChatSessionModel = Field(default_factory=ChatSessionModel)




# ── Domain models ─────────────────────────────────────────────────────────────

class TaskStatus(str, Enum):
    RUNNING  = "running"
    PROGRESS = "progress"
    FINISHED = "finished"
    CANCELED = "canceled"
    FAILED   = "failed"


class ProgressEvent(BaseModel):
    status: TaskStatus
    elapsed_seconds: int = Field(default=0, ge=0)
    message: str = ""
    result: MedicalReport | str | None = None


T = TypeVar('T')

# --- 1. OBSERVABLE LIST (Reusable Utility) ---
class ObservableList(UserList, Generic[T]):
    """An observable list that notifies subscribers on mutation."""
    def __init__(self, initlist=None):
        super().__init__(initlist)
        self._callbacks: list[Callable[[list[T]], None]] = []

    def bind(self, callback: Callable[[list[T]], None]) -> None:
        self._callbacks.append(callback)

    def _notify(self) -> None:
        for callback in self._callbacks:
            callback(self.data)

    # Intercept mutating methods to trigger notifications
    def append(self, item: T) -> None:
        super().append(item)
        self._notify()

    def remove(self, item: T) -> None:
        super().remove(item)
        self._notify()

    def extend(self, other) -> None:
        super().extend(other)
        self._notify()

    def clear(self) -> None:
        super().clear()
        self._notify()

    def __setitem__(self, i, item) -> None:
        super().__setitem__(i, item)
        self._notify()

    def __delitem__(self, i) -> None:
        super().__delitem__(i)
        self._notify()
        
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


