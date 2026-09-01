import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from models.patient import MedicalReport


class ChatMessage(BaseModel):
    content: str = Field(description="The content of the message.")
    timestamp: datetime = Field(default_factory=datetime.now)


class GeminiModelConfig(BaseModel):
    model_name: str = Field(default="gemini-3-pro-preview")
    temperature: float = Field(default=1.0)
    top_p: float = Field(default=0.95)
    max_output_tokens: int = Field(default=65535)
    thinking_level: str = Field(default="HIGH")
    system_instruction: tuple[str, ...] = Field(default=(
        "You are an expert medical data analyst using equally both holistic and traditional medical data.",
        "Always highlight severe abnormalities."
    ))


class ChatSessionModel(BaseModel):
    session_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    model_settings: GeminiModelConfig = Field(default_factory=GeminiModelConfig)
    report: MedicalReport = Field(default_factory=MedicalReport)
    chat_history: list[ChatMessage] = Field(default_factory=list)


class AIServiceConfig(BaseModel):
    api_key: str = Field(default="")
    model_settings: GeminiModelConfig = Field(default_factory=GeminiModelConfig)
    chat_history: ChatSessionModel = Field(default_factory=ChatSessionModel)


class ClaudeModelConfig(BaseModel):
    model_name: str = Field(default="claude-3-5-sonnet-20241022")
    temperature: float = Field(default=1.0)
    top_p: float = Field(default=0.95)
    max_output_tokens: int = Field(default=8096)
    thinking_budget_tokens: int = Field(default=0)
    system_instruction: tuple[str, ...] = Field(default=(
        "You are an expert medical data analyst using equally both holistic and traditional medical data.",
        "Always highlight severe abnormalities."
    ))


class ClaudeAIServiceConfig(BaseModel):
    api_key: str = Field(default="")
    model_settings: ClaudeModelConfig = Field(default_factory=ClaudeModelConfig)
