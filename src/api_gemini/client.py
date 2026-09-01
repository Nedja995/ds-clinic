import time
from enum import StrEnum
from typing import Any, Iterator, Optional

from google import genai
from google.genai import types as genai_types

from models import MedicalReportModel, GeminiModelConfig, AIServiceConfig
from npy.core.logger import setup_logger

logger = setup_logger()


class Models(StrEnum):
    """The model names, find more <link>"""
    GEMINI_3_PRO_PREVIEW = "gemini-3-pro-preview"
    GEMINI_3_FLASH_PREVIEW = "gemini-3-flash-preview"
    GEMINI_PRO = "gemini-pro"


class MedicalAnalyzerClient:
    """Client for interacting with the Gemini API for medical report analysis."""

    def __init__(self, config: Optional[AIServiceConfig] = None) -> None:
        logger.info("Initializing MedicalAnalyzerClient...")
        self.config: AIServiceConfig = config or AIServiceConfig()
        self.client: Optional[genai.Client] = None
        self.chat_session: Optional[Any] = None  # genai chat handle — no stable public type
        self.ai_config: Optional[genai_types.GenerateContentConfig] = None

        if not self.config.api_key:
            logger.warning(
                "Gemini API key is not set. "
                "Open Settings → AI → Google API Key and save your key. "
                "Analysis will fail until a valid key is provided."
            )
            return

        logger.debug(f"Using model: {self.config.model_settings.model_name}")
        self._initialise_client()
        self._initialize_ai_config()
        self.initialize_chat_session()
        logger.info("MedicalAnalyzerClient initialized successfully")

    def _initialise_client(self) -> None:
        logger.debug(f"{'  '}Initializing Google Genai Client...")
        try:
            self.client = genai.Client(api_key=self.config.api_key)
            logger.debug(f"{'    '}Google Genai Client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Genai Client: {str(e)}", exc_info=True)
            raise

    def close(self) -> None:
        logger.debug("Closing MedicalAnalyzerClient...")
        try:
            if self.client and hasattr(self.client, "close"):
                self.client.close()
            logger.debug("MedicalAnalyzerClient closed successfully")
        except Exception as e:
            logger.warning(f"Error while closing client: {str(e)}", exc_info=True)

    def initialize_chat_session(self) -> None:
        logger.debug(f"Creating chat session with model: {self.config.model_settings.model_name}")
        try:
            assert self.client is not None
            self.chat_session = self.client.chats.create(
                model=self.config.model_settings.model_name,
                config=self.ai_config,
            )
            logger.debug("Chat session created successfully")
        except Exception as e:
            logger.error(f"Failed to create chat session: {str(e)}", exc_info=True)
            raise

    def _initialize_ai_config(self) -> None:
        logger.debug(f"{'  '}Initializing AI configuration...")
        tools: list[genai_types.Tool] = [
            genai_types.Tool(google_search=genai_types.GoogleSearch()),
        ]
        logger.debug(f"{'    '}Configured {len(tools)} tools for AI model")

        thinking_config = genai_types.ThinkingConfig(
            thinking_level=self.config.model_settings.thinking_level
        )

        system_text = " ".join(self.config.model_settings.system_instruction)

        self.ai_config = genai_types.GenerateContentConfig(
            temperature=self.config.model_settings.temperature,
            top_p=self.config.model_settings.top_p,
            tools=tools,  # type: ignore[arg-type]
            max_output_tokens=self.config.model_settings.max_output_tokens,
            response_mime_type="application/json",
            response_schema=MedicalReportModel,
            thinking_config=thinking_config,
            system_instruction=system_text,
            safety_settings=[
                genai_types.SafetySetting(
                    category=genai_types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                    threshold=genai_types.HarmBlockThreshold.OFF,
                ),
                genai_types.SafetySetting(
                    category=genai_types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    threshold=genai_types.HarmBlockThreshold.OFF,
                ),
                genai_types.SafetySetting(
                    category=genai_types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                    threshold=genai_types.HarmBlockThreshold.OFF,
                ),
                genai_types.SafetySetting(
                    category=genai_types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                    threshold=genai_types.HarmBlockThreshold.OFF,
                ),
            ],
        )
        logger.debug(f"{'    '}AI configuration initialized successfully")

    def initial_analysis_report_from_chat_stream(
        self,
        documents: list[genai_types.Part],
        question: str,
    ) -> Optional[MedicalReportModel]:
        if not self.client or not self.chat_session:
            raise RuntimeError(
                "Gemini client is not initialized. "
                "Set your Google API Key in Settings → AI → Google API Key."
            )

        logger.info("Run initial medical analysis from chat stream (Streaming JSON).")
        start_time = time.time()
        accumulated_json: str = ""
        parsed_report: Optional[MedicalReportModel] = None

        for chunk in self._initial_analysis_run_chat_stream(documents, question):
            accumulated_json += chunk

        elapsed_time = time.time() - start_time
        logger.info(f"{'  '}Successfully completed in {elapsed_time:.2f}s.")
        logger.info(f"{'  '}Accumulated response size: {len(accumulated_json)} characters.")
        logger.debug(f"{'  '}Formatting and validating structured data...")

        try:
            parsed_report = MedicalReportModel.model_validate_json(accumulated_json)
            logger.info(f"{'  '}Successfully parsed and validated response in {elapsed_time:.2f}s")
        except ValueError as e:
            logger.error(f"\nValidation error parsing report after {elapsed_time:.2f}s: {str(e)}")
            logger.debug(f"Raw response (first 500 chars): {accumulated_json[:500]}...")
            logger.warning("Falling back to raw response output")
        except Exception as e:
            logger.error(f"\nUnexpected error parsing report after {elapsed_time:.2f}s: {str(e)}", exc_info=True)
            logger.debug(f"Raw response (first 500 chars): {accumulated_json[:500]}...")

        return parsed_report

    def _initial_analysis_run_chat_stream(
        self,
        documents: list[genai_types.Part],
        predefined_question: str,
    ) -> Iterator[str]:
        logger.debug("Run initial analysis chat")

        message_contents: list[str | genai_types.Part] = [
            "Here are the input medical/lab documents:"
        ]
        message_contents.extend(documents)
        message_contents.append(f"Question/Task: {predefined_question}")

        config_response = genai_types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json",
            response_schema=MedicalReportModel,
        )

        logger.debug(f"{'  '}Sending analysis request to Gemini API...")
        try:
            assert self.chat_session is not None
            response_stream = self.chat_session.send_message_stream(
                message_contents,
                config=config_response,
            )
            logger.debug(f"{'    '}Streaming response received from API")
        except Exception as e:
            logger.error(f"Error during API call: {str(e)}", exc_info=True)
            raise

        chunk_count = 0
        for chunk in response_stream:
            if chunk.text:
                chunk_count += 1
                logger.debug(f"{'    '}Received chunk #{chunk_count}")
                yield chunk.text

        logger.debug(f"Streaming completed: received {chunk_count} chunks")

    def ask_followup_question(self, question: str) -> str:
        if not self.client or not self.chat_session:
            raise RuntimeError(
                "Gemini client is not initialized. "
                "Set your Google API Key in Settings → AI → Google API Key."
            )

        logger.info("Run ask follow-up question from chat stream.")
        accumulated_response: str = ""

        for chunk in self._run_ask_followup_stream(question):
            accumulated_response += chunk

        return accumulated_response

    def _run_ask_followup_stream(self, question: str) -> Iterator[str]:
        logger.debug(f"Run followup chat with question: {question}")

        config_response = genai_types.GenerateContentConfig(temperature=1.0)

        logger.debug(f"{'  '}Sending chat question to Gemini API...")
        try:
            assert self.chat_session is not None
            response_stream = self.chat_session.send_message_stream(
                question,
                config=config_response,
            )
            logger.debug(f"{'    '}Streaming response received from API")
        except Exception as e:
            logger.error(f"Error during API call: {str(e)}", exc_info=True)
            raise

        chunk_count = 0
        for chunk in response_stream:
            if chunk.text:
                chunk_count += 1
                logger.debug(f"{'    '}Received chunk #{chunk_count}")
                yield chunk.text

        logger.debug(f"Streaming completed: received {chunk_count} chunks")
