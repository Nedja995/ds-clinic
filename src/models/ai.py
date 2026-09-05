"""
src/models/ai.py — AI session and configuration models.

Owns: ChatMessage, ChatSessionModel, GeminiModelConfig, ClaudeModelConfig,
      AIServiceConfig, ClaudeAIServiceConfig.

ChatMessage.include_in_report controls whether a bot response is included in
the PDF export (v2.12.4). Default True so existing sessions are unaffected.

Does NOT own: patient data, report content, or provider routing.
"""
import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from models.patient import MedicalReport


class ChatMessage(BaseModel):
    """A single message in the chat history for a clinical session.

    include_in_report controls whether this bot response is rendered in the
    PDF export's "DODATNA ANALIZA" section. User messages (role="user") are
    never included in the PDF regardless of this flag — filtering is applied
    by the ViewModel's _rebuild_chat_responses() which reads only bot turns.
    """
    content: str = Field(description="The content of the message.")
    timestamp: datetime = Field(default_factory=datetime.now)
    # Default True preserves backward-compatibility with sessions persisted
    # before v2.12.4 — all previously saved responses remain included.
    include_in_report: bool = Field(
        default=True,
        description="When False, this response is excluded from the PDF export.",
    )


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
