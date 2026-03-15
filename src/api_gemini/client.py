import os
import time
from enum import StrEnum
from typing import Iterator

from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from models import DSClinicReport
from logger import setup_logger

logger = setup_logger()


# Models
class Models(StrEnum):
    """The model names, find more <link>"""
    GEMINI_3_PRO_PREVIEW = "gemini-3-pro-preview"
    GEMINI_3_FLASH_PREVIEW = "gemini-3-flash-preview"
    GEMINI_PRO = "gemini-pro"


class GeminiConfig(BaseModel):
    api_key: str = Field(default_factory=lambda: os.getenv("GOOGLE_API_KEY", ""))
    model_name: str = "gemini-3-pro-review" #Models = Field(default=Models.GEMINI_3_PRO_PREVIEW)


class MedicalAnalyzerClient:
    def __init__(self, config: GeminiConfig = None):
        logger.info("Initializing MedicalAnalyzerClient...")
        self.config = config or GeminiConfig()
        if not self.config.api_key:
            logger.error("GOOGLE_API_KEY environment variable is missing")
            raise ValueError("GOOGLE_API_KEY environment variable is missing.")
        logger.debug(f"Using model: {self.config.model_name}")
        self._initialise_client()
        self._initialize_ai_config()
        self.initialize_chat_session()
        logger.info("MedicalAnalyzerClient initialized successfully")

    def _initialise_client(self):
        logger.debug("Initializing Google Genai Client...")
        try:
            self.client = genai.Client(
                # METHOD 1 - API Key (Recommended for testing)
                api_key=self.config.api_key,
                # METHOD 2 - VertexAI (Recommended for production)
                # vertexai=True,
                # project=GOOGLE_PROJECT_ID,
                # location=GOOGLE_PROJECT_LOCATION
            )
            logger.debug("Google Genai Client created successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Genai Client: {str(e)}", exc_info=True)
            raise


    def close(self):
        logger.debug("Closing MedicalAnalyzerClient...")
        try:
            if hasattr(self.client, 'close'):
                self.client.close()
            logger.debug("MedicalAnalyzerClient closed successfully")
        except Exception as e:
            logger.warning(f"Error while closing client: {str(e)}", exc_info=True)

    def initialize_chat_session(self):
        logger.debug(f"Creating chat session with model: {self.config.model_name}")
        try:
            self.chat_session = self.client.chats.create(
                model=self.config.model_name,
                config=self.ai_config
            )
            logger.debug("Chat session created successfully")
        except Exception as e:
            logger.error(f"Failed to create chat session: {str(e)}", exc_info=True)
            raise

    def _initialize_ai_config(self):
        logger.debug("Initializing AI configuration...")
        # TOOLS
        tools = [
            types.Tool(google_search=types.GoogleSearch()),
            # types.Tool(url_context=types.UrlContext()),
            # types.Tool(enterprise_web_search=types.EnterpriseWebSearch())
        ]
        logger.debug(f"Configured {len(tools)} tools for AI model")

        # 2. ADD TO CONFIGURATION
        self.ai_config = types.GenerateContentConfig(
            temperature=1.0,
            top_p=0.95,
            tools=tools,
            max_output_tokens=65535,  # <-- Enabled here!
            response_mime_type="application/json",
            response_schema=DSClinicReport,
            thinking_config=types.ThinkingConfig(thinking_level=types.ThinkingLevel.HIGH),
            system_instruction=(
                "You are an expert medical data analyst using equally both holistic and traditional medical data.",
                "Always highlight severe abnormalities."
            ),
            safety_settings=[types.SafetySetting(
                category="HARM_CATEGORY_HATE_SPEECH",
                threshold="OFF"
            ), types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT",
                threshold="OFF"
            ), types.SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                threshold="OFF"
            ), types.SafetySetting(
                category="HARM_CATEGORY_HARASSMENT",
                threshold="OFF"
            )
            ]
        )
        logger.debug("AI configuration initialized successfully")

    def initial_anlysis_run_chat_stream(self, documents: list[types.Part], predefined_question: str) -> Iterator[str]:
        logger.debug(f"Starting initial analysis with {len(documents)} document(s)")
        logger.debug(f"Predefined question: {predefined_question}")
        
        message_contents = ["Here are the input medical/lab documents:"]
        message_contents.extend(documents)
        message_contents.append(f"Question/Task: {predefined_question}")

        # 2. OVERRIDE CONFIG FOR THIS SPECIFIC MESSAGE TO FORCE JSON/PYDANTIC
        structured_config = types.GenerateContentConfig(
            temperature=0.1, # Even lower temp for strict JSON compliance
            response_mime_type="application/json",
            response_schema=DSClinicReport, # Pass the Pydantic model directly!
        )
        
        logger.debug("Sending analysis request to Gemini API...")
        try:
            response_stream = self.chat_session.send_message_stream(
                message_contents,
                config=structured_config
            )
            logger.debug("Streaming response received from API")
        except Exception as e:
            logger.error(f"Error during API call: {str(e)}", exc_info=True)
            raise

        chunk_count = 0
        for chunk in response_stream:
            if chunk.text:
                chunk_count += 1
                logger.debug(f"Received chunk #{chunk_count}")
                yield chunk.text
        
        logger.debug(f"Streaming completed: received {chunk_count} chunks")
                
    def initial_analysis_report_from_chat_stream(self, documents: list[types.Part], question: str) -> DSClinicReport:
        logger.info("Starting medical analysis with Google AI (Streaming JSON)...")
        start_time = time.time()
        parsed_report: DSClinicReport = None
        accumulated_json: str = ""
        
        # 1. Stream the Structured JSON chunks
        logger.debug(f"Processing {len(documents)} documents with question: {question}...")
        for chunk in self.initial_anlysis_run_chat_stream(documents, question):
            print(chunk, end="", flush=True) # Print without newlines and flush buffer immediately for the typing effect
            accumulated_json += chunk
        
        logger.debug(f"Accumulated response size: {len(accumulated_json)} characters")
        logger.info("Formatting and validating structured data...")
        
        # 2. Parse the accumulated JSON string into the Pydantic model
        try:
            parsed_report = DSClinicReport.model_validate_json(accumulated_json)
            
            elapsed_time = time.time() - start_time
            logger.info(f"Successfully parsed and validated medical report (completed in {elapsed_time:.2f}s)")
            #logger.debug(f"Report contains {len(parsed_report.severe_abnormalities) if parsed_report.severe_abnormalities else 0} severe abnormalities")
            
            # Format it nicely for the final report
            # report_text = (
            #     f"PATIENT SUMMARY:\n{parsed_report.patient_summary}\n\n"
            #     f"SEVERE ABNORMALITIES:\n" + "\n".join([f"- {item}" for item in parsed_report.severe_abnormalities]) + "\n\n"
            #     f"RECOMMENDATIONS:\n" + "\n".join([f"- {item}" for item in parsed_report.recommended_followups])
            # )
            #logger.info(f"Successfully parsed Pydantic schema! Report:\n{report_text}")
        except ValueError as e:
            elapsed_time = time.time() - start_time
            logger.error(f"\nValidation error parsing report after {elapsed_time:.2f}s: {str(e)}")
            logger.debug(f"Raw response (first 500 chars): {accumulated_json[:500]}...") # Log only first 500 chars
            logger.warning("Falling back to raw response output")
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"\nUnexpected error parsing report after {elapsed_time:.2f}s: {str(e)}", exc_info=True)
            logger.debug(f"Raw response (first 500 chars): {accumulated_json[:500]}...") # Log only first 500 chars
            
        return parsed_report


    def ask_followup_stream(self, follow_up_question: str) -> Iterator[str]:
        logger.debug(f"Sending follow-up question: {follow_up_question[:100]}...")
        try:
            response_stream = self.chat_session.send_message_stream(follow_up_question)
            logger.debug("Follow-up response stream initialized")
            chunk_count = 0
            for chunk in response_stream:
                if chunk.text:
                    chunk_count += 1
                    yield chunk.text
            logger.debug(f"Follow-up question completed: {chunk_count} chunks received")
        except Exception as e:
            logger.error(f"Error during follow-up question: {str(e)}", exc_info=True)
            raise
