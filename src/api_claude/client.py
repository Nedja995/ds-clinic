import json
import time
from enum import StrEnum
from typing import Iterator

import anthropic

from models import MedicalReportModel, ClaudeModelConfig, ClaudeAIServiceConfig
from npy.core.logger import setup_logger

logger = setup_logger()


# ---------------------------------------------------------------------------
# Model name constants  (mirrors api_gemini/client.py::Models)
# ---------------------------------------------------------------------------
class Models(StrEnum):
    """Claude model identifiers — see https://docs.anthropic.com/en/docs/models-overview"""
    CLAUDE_OPUS_4_5          = "claude-opus-4-5"
    CLAUDE_SONNET_4_5        = "claude-sonnet-4-5"
    CLAUDE_HAIKU_4_5         = "claude-haiku-4-5-20251001"
    CLAUDE_3_5_SONNET        = "claude-3-5-sonnet-20241022"
    CLAUDE_3_5_HAIKU         = "claude-3-5-haiku-20241022"
    CLAUDE_3_OPUS            = "claude-3-opus-20240229"


# ---------------------------------------------------------------------------
# System prompt helper — embeds MedicalReportModel JSON schema so Claude
# always returns valid structured JSON.  Mirrors Gemini's response_schema=.
# ---------------------------------------------------------------------------
def _build_system_prompt(base_instructions: tuple | list[str] | str, response_schema_model) -> str:
    """
    Combine system instructions with JSON schema enforcement.
    Claude has no native response_schema param, so we embed the schema in the
    system prompt — functionally equivalent to Gemini's response_schema kwarg.
    """
    if isinstance(base_instructions, (tuple, list)):
        instructions_text = " ".join(base_instructions)
    else:
        instructions_text = base_instructions or ""

    schema_json = json.dumps(response_schema_model.model_json_schema(), indent=2)
    return (
        f"{instructions_text}\n\n"
        "CRITICAL OUTPUT REQUIREMENT:\n"
        "You MUST respond with ONLY a valid JSON object — no markdown fences, no preamble, no commentary.\n"
        "The JSON MUST strictly conform to this schema:\n"
        f"{schema_json}"
    )


# ---------------------------------------------------------------------------
# ClaudeAnalyzerClient
# ---------------------------------------------------------------------------
class ClaudeAnalyzerClient:
    """
    Client for interacting with the Anthropic Claude API for medical report analysis.
    
    API surface mirrors api_gemini/client.py::MedicalAnalyzerClient so both clients
    are interchangeable in dsclinic.py.
    
    Key difference from Gemini:
      - Anthropic API is stateless: chat context is maintained manually as
        self.chat_history (list of role/content dicts) and sent on every call.
      - Documents are Anthropic content block dicts (from api_claude/utils.py)
        instead of genai_types.Part objects.
      - Structured JSON output is enforced via system prompt (no response_schema param).
    """

    client: anthropic.Anthropic = None
    chat_history: list[dict] = []   # Manually maintained — Anthropic is stateless
    system_prompt: str = ""

    def __init__(self, config: ClaudeAIServiceConfig = None):
        logger.info("[api_claude] Initializing ClaudeAnalyzerClient...")
        self.config = config or ClaudeAIServiceConfig()

        if not self.config.api_key:
            logger.error("[api_claude] ANTHROPIC_API_KEY is missing")
            raise ValueError("ANTHROPIC_API_KEY is missing.")

        logger.debug(f"[api_claude] Using model: {self.config.model_settings.model_name}")

        self._initialise_client()
        self._build_system_prompt_internal()
        self.initialize_chat_session()

        logger.info("[api_claude] ClaudeAnalyzerClient initialized successfully")

    # ------------------------------------------------------------------
    def _initialise_client(self):
        logger.debug("[api_claude]   Initializing Anthropic Client...")
        try:
            self.client = anthropic.Anthropic(api_key=self.config.api_key)
            logger.debug("[api_claude]     Anthropic Client initialized successfully")
        except Exception as e:
            logger.error(f"[api_claude] Failed to initialize Anthropic Client: {e}", exc_info=True)
            raise

    def _build_system_prompt_internal(self):
        """Build system prompt with embedded JSON schema for structured output."""
        self.system_prompt = _build_system_prompt(
            self.config.model_settings.system_instruction,
            MedicalReportModel
        )
        logger.debug("[api_claude]     System prompt built with MedicalReportModel JSON schema")

    def close(self):
        logger.debug("[api_claude] Closing ClaudeAnalyzerClient...")
        try:
            if hasattr(self.client, 'close'):
                self.client.close()
            logger.debug("[api_claude] ClaudeAnalyzerClient closed successfully")
        except Exception as e:
            logger.warning(f"[api_claude] Error while closing client: {e}", exc_info=True)

    def initialize_chat_session(self):
        """Reset chat history — equivalent to creating a new Gemini chat session."""
        logger.debug(f"[api_claude] Resetting chat history for model: {self.config.model_settings.model_name}")
        self.chat_history = []
        logger.debug("[api_claude] Chat session (history) initialized")

    # ------------------------------------------------------------------
    # Public API — mirrors MedicalAnalyzerClient exactly
    # ------------------------------------------------------------------

    def initial_analysis_report_from_chat_stream(
        self,
        documents: list[dict],
        question: str
    ) -> MedicalReportModel:
        """
        Run initial medical analysis. Streams JSON chunks, accumulates, parses.
        Mirrors api_gemini/client.py::initial_analysis_report_from_chat_stream().
        
        Args:
            documents: List of Anthropic content block dicts (from api_claude/utils.py)
            question:  Initial task/question string
        Returns:
            Parsed MedicalReportModel or None on parse failure
        """
        logger.info("[api_claude] Run initial medical analysis from chat stream (Streaming JSON).")
        start_time = time.time()
        parsed_report: MedicalReportModel = None
        accumulated_json: str = ""

        for chunk in self._initial_analysis_run_chat_stream(documents, question):
            accumulated_json += chunk

        elapsed_time = time.time() - start_time
        logger.info(f"[api_claude]   Completed in {elapsed_time:.2f}s.")
        logger.info(f"[api_claude]   Accumulated response size: {len(accumulated_json)} characters.")

        # Store exchange in history so follow-up questions have full context
        # (We store the full initial user message without document blobs to keep history lean)
        self.chat_history.append({
            "role": "assistant",
            "content": accumulated_json
        })

        logger.debug("[api_claude]   Formatting and validating structured data...")
        elapsed_time = time.time() - start_time
        try:
            # Strip possible markdown fences if model ignored the instruction
            clean_json = accumulated_json.strip()
            if clean_json.startswith("```"):
                clean_json = clean_json.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
            parsed_report = MedicalReportModel.model_validate_json(clean_json)
            logger.info(f"[api_claude]   Parsed and validated in {elapsed_time:.2f}s")
        except ValueError as e:
            logger.error(f"[api_claude] Validation error after {elapsed_time:.2f}s: {e}")
            logger.debug(f"[api_claude] Raw response (first 500 chars): {accumulated_json[:500]}...")
            logger.warning("[api_claude] Falling back to raw response output")
        except Exception as e:
            logger.error(f"[api_claude] Unexpected parse error after {elapsed_time:.2f}s: {e}", exc_info=True)
            logger.debug(f"[api_claude] Raw response (first 500 chars): {accumulated_json[:500]}...")

        return parsed_report

    def _initial_analysis_run_chat_stream(
        self,
        documents: list[dict],
        predefined_question: str
    ) -> Iterator[str]:
        """
        Build the initial user message with document blocks + question, stream response.
        Mirrors api_gemini/client.py::_initial_analysis_run_chat_stream().
        
        The user message content list follows Anthropic's multimodal format:
          [text_block, ...document_blocks, text_block(question)]
        """
        logger.debug("[api_claude] Run initial analysis chat stream")

        # Build content list: text intro + all document blocks + question
        user_content: list[dict] = [{"type": "text", "text": "Here are the input medical/lab documents:"}]
        user_content.extend(documents)
        user_content.append({"type": "text", "text": f"Question/Task: {predefined_question}"})

        # Initial user message — stored in history WITHOUT document blobs to keep tokens lean
        self.chat_history.append({
            "role": "user",
            "content": f"[Initial analysis with {len(documents)} document(s)] Question/Task: {predefined_question}"
        })

        logger.debug(f"[api_claude]   Sending {len(documents)} document(s) to Claude API...")
        try:
            # Use a one-shot messages list for the initial call (not chat_history) because
            # document blobs must only be in this first request for efficiency.
            with self.client.messages.stream(
                model=self.config.model_settings.model_name,
                max_tokens=self.config.model_settings.max_output_tokens,
                temperature=self.config.model_settings.temperature,
                top_p=self.config.model_settings.top_p,
                system=self.system_prompt,
                messages=[{"role": "user", "content": user_content}],
            ) as stream:
                logger.debug("[api_claude]     Streaming response received from API")
                chunk_count = 0
                for text_chunk in stream.text_stream:
                    if text_chunk:
                        chunk_count += 1
                        yield text_chunk
                logger.debug(f"[api_claude]   Streaming completed: {chunk_count} chunks")
        except anthropic.APIStatusError as e:
            logger.error(f"[api_claude] API status error: {e.status_code} – {e.message}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"[api_claude] Error during API call: {e}", exc_info=True)
            raise

    def ask_followup_stream(self, follow_up_question: str) -> Iterator[str]:
        """
        Send a follow-up question using accumulated chat history for context.
        Mirrors api_gemini/client.py::ask_followup_stream().
        
        Chat history includes all prior exchanges so Claude has full context.
        """
        logger.debug(f"[api_claude] Sending follow-up question: {follow_up_question[:100]}...")

        self.chat_history.append({"role": "user", "content": follow_up_question})

        accumulated_response = ""
        try:
            with self.client.messages.stream(
                model=self.config.model_settings.model_name,
                max_tokens=self.config.model_settings.max_output_tokens,
                temperature=self.config.model_settings.temperature,
                top_p=self.config.model_settings.top_p,
                system=self.system_prompt,
                messages=self.chat_history,
            ) as stream:
                logger.debug("[api_claude] Follow-up response stream initialized")
                chunk_count = 0
                for text_chunk in stream.text_stream:
                    if text_chunk:
                        chunk_count += 1
                        accumulated_response += text_chunk
                        yield text_chunk
                logger.debug(f"[api_claude] Follow-up completed: {chunk_count} chunks received")
        except anthropic.APIStatusError as e:
            logger.error(f"[api_claude] API status error: {e.status_code} – {e.message}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"[api_claude] Error during follow-up: {e}", exc_info=True)
            raise

        # Append assistant response to history for next follow-up
        self.chat_history.append({"role": "assistant", "content": accumulated_response})
