import os
import time
from enum import StrEnum
from typing import Iterator
from google import genai
from google.genai import types as genai_types
from pydantic import BaseModel, Field
from models import MedicalReportModel, GeminiModelConfig, AIServiceConfig
from npy.core.logger import setup_logger

logger = setup_logger()


# Models
class Models(StrEnum):
    """The model names, find more <link>"""
    GEMINI_3_PRO_PREVIEW = "gemini-3-pro-preview"
    GEMINI_3_FLASH_PREVIEW = "gemini-3-flash-preview"
    GEMINI_PRO = "gemini-pro"





class MedicalAnalyzerClient:
    """Client for interacting with the Gemini API for medical report analysis."""
    client: genai.Client = None
    chat_session: genai_types.ChatSession = None
    ai_config: genai_types.GenerateContentConfig = None

    def __init__(self, config: AIServiceConfig = None):
        logger.info("Initializing MedicalAnalyzerClient...")
        self.config = config or AIServiceConfig()
        if not self.config.api_key:
            logger.error("GOOGLE_API_KEY environment variable is missing")
            raise ValueError("GOOGLE_API_KEY environment variable is missing.")
        
        logger.debug(f"Using model: {self.config.model_settings.model_name}")
        
        self._initialise_client()
        self._initialize_ai_config()
        self.initialize_chat_session()
        
        logger.info("MedicalAnalyzerClient initialized successfully")

    def _initialise_client(self):
        logger.debug(f"{' ' * 2}Initializing Google Genai Client...")
        try:
            self.client = genai.Client(
                # METHOD 1 - API Key (Recommended for testing)
                api_key=self.config.api_key,
                # METHOD 2 - VertexAI (Recommended for production)
                # vertexai=True,
                # project=GOOGLE_PROJECT_ID,
                # location=GOOGLE_PROJECT_LOCATION
            )
            logger.debug(f"{' ' * 4}Google Genai Client initialized successfully")
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
        logger.debug(f"Creating chat session with model: {self.config.model_settings.model_name}")
        try:
            self.chat_session = self.client.chats.create(
                model=self.config.model_settings.model_name,
                config=self.ai_config
            )
            logger.debug("Chat session created successfully")
        except Exception as e:
            logger.error(f"Failed to create chat session: {str(e)}", exc_info=True)
            raise

    def _initialize_ai_config(self):
        logger.debug(f"{' ' * 2}Initializing AI configuration...")
        # TOOLS
        tools = [
            genai_types.Tool(google_search=genai_types.GoogleSearch()),
            # genai_types.Tool(url_context=genai_types.UrlContext()),
            # genai_types.Tool(enterprise_web_search=genai_types.EnterpriseWebSearch())
        ]
        logger.debug(f"{' ' * 4}Configured {len(tools)} tools for AI model")

        # Tkining config self.config.model_settings.thinking_level
        thinking_config = genai_types.ThinkingConfig(thinking_level=self.config.model_settings.thinking_level)

        # 2. ADD TO CONFIGURATION
        self.ai_config = genai_types.GenerateContentConfig(
            temperature=self.config.model_settings.temperature,
            top_p=self.config.model_settings.top_p,
            tools=tools,
            max_output_tokens=self.config.model_settings.max_output_tokens,
            response_mime_type="application/json",
            response_schema=MedicalReportModel,
            thinking_config=thinking_config,
            system_instruction=(
                "You are an expert medical data analyst using equally both holistic and traditional medical data.",
                "Always highlight severe abnormalities."
            ),
            safety_settings=[genai_types.SafetySetting(
                category="HARM_CATEGORY_HATE_SPEECH",
                threshold="OFF"
            ), genai_types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT",
                threshold="OFF"
            ), genai_types.SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                threshold="OFF"
            ), genai_types.SafetySetting(
                category="HARM_CATEGORY_HARASSMENT",
                threshold="OFF"
            )
            ]
        )
        logger.debug(f"{' ' * 4}AI configuration initialized successfully")
                
    def initial_analysis_report_from_chat_stream(self, documents: list[genai_types.Part], question: str) -> MedicalReportModel:
        logger.info("Run initial medical analysis from chat stream (Streaming JSON).")
        start_time = time.time()
        parsed_report: MedicalReportModel = None
        accumulated_json: str = ""
        
        # 1. Stream the Structured JSON chunks
        #logger.debug(f"Processing {len(documents)} documents with question: {question}...")
        for chunk in self._initial_analysis_run_chat_stream(documents, question):
            #print(chunk, end="", flush=True) # Print without newlines and flush buffer immediately for the typing effect
            #logger.debug(chunk)
            accumulated_json += chunk
        
        elapsed_time = time.time() - start_time
        logger.info(f"{' ' * 2}Successfully complited in {elapsed_time:.2f}s.")
        logger.info(f"{' ' * 2}Accumulated response size: {len(accumulated_json)} characters.")
        logger.debug(f"{' ' * 2}Formatting and validating structured data...")
        
        # 2. Parse the accumulated JSON string into the Pydantic model
        elapsed_time = time.time() - start_time
        try:
            parsed_report = MedicalReportModel.model_validate_json(accumulated_json)
            logger.info(f"{' ' * 2}Successfully parsed and validated response in {elapsed_time:.2f}s)")
        except ValueError as e:
            logger.error(f"\nValidation error parsing report after {elapsed_time:.2f}s: {str(e)}")
            logger.debug(f"Raw response (first 500 chars): {accumulated_json[:500]}...") # Log only first 500 chars
            logger.warning("Falling back to raw response output")
        except Exception as e:
            logger.error(f"\nUnexpected error parsing report after {elapsed_time:.2f}s: {str(e)}", exc_info=True)
            logger.debug(f"Raw response (first 500 chars): {accumulated_json[:500]}...") # Log only first 500 chars
            
        return parsed_report

    def _initial_analysis_run_chat_stream(self, documents: list[genai_types.Part], predefined_question: str) -> Iterator[str]:
        logger.debug(f"Run initial analysis chat")
        # logger.debug(f"{'' * 2}Processing {len(documents)} document(s)")
        # logger.debug(f"{'' * 2}Question: {predefined_question}")
        
        message_contents = ["Here are the input medical/lab documents:"]
        message_contents.extend(documents)
        message_contents.append(f"Question/Task: {predefined_question}")
        
        logger.debug(f"{'' * 2}Arguments: {message_contents}")

        # 2. OVERRIDE CONFIG FOR THIS SPECIFIC MESSAGE TO FORCE JSON/PYDANTIC
        config_response = genai_types.GenerateContentConfig(
            temperature=0.1, # Even lower temp for strict JSON compliance
            response_mime_type="application/json",
            response_schema=MedicalReportModel, # Pass the Pydantic model directly!
        )
        
        logger.debug(f"{'' * 2}Sending analysis request to Gemini API...")
        try:
            response_stream = self.chat_session.send_message_stream(
                message_contents,
                config=config_response
            )
            logger.debug(f"{'' * 4}Streaming response received from API")
        except Exception as e:
            logger.error(f"Error during API call: {str(e)}", exc_info=True)
            raise

        chunk_count = 0
        for chunk in response_stream:
            if chunk.text:
                chunk_count += 1
                logger.debug(f"{'' * 4}Received chunk #{chunk_count}")
                yield chunk.text
        
        logger.debug(f"Streaming completed: received {chunk_count} chunks")


    def ask_followup_question(self, question: str) -> str:
        logger.info("Run ask follow-up question from chat stream.")

        accumulated_response: str = ""
        
        # 1. Stream the Structured JSON chunks
        logger.debug(f"Processing question: {question}...")
        for chunk in self._run_ask_followup_stream(question):
            #print(chunk, end="", flush=True) # Print without newlines and flush buffer immediately for the typing effect
            #logger.debug(chunk)
            accumulated_response += chunk
        
        return accumulated_response
    

    def _run_ask_followup_stream(self, question: str) -> Iterator[str]:
        logger.debug(f"Run followup chat with question: {question}")

        # 2. OVERRIDE CONFIG FOR THIS SPECIFIC MESSAGE TO FORCE STRING RESPONSE
        config_response = genai_types.GenerateContentConfig(
            temperature=1.0,
            #top_p=self.ai_config.top_p,
            #response_mime_type="text/plain",
            #thinking_config=self.ai_config.thinking_config, # Reuse the same thinking config with tools
            #system_instruction=self.ai_config.system_instruction, # Reuse the same system instruction
            #safety_settings=self.ai_config.safety_settings, # Reuse the same safety settings
            #tools=self.ai_config.tools, # Reuse the same tools (e.g. Google Search)
        )
        
        logger.debug(f"{'' * 2}Sending chat question to Gemini API...")
        try:
            response_stream = self.chat_session.send_message_stream(
                question,
                config=config_response
            )
            logger.debug(f"{'' * 4}Streaming response received from API")
        except Exception as e:
            logger.error(f"Error during API call: {str(e)}", exc_info=True)
            raise

        chunk_count = 0
        for chunk in response_stream:
            if chunk.text:
                chunk_count += 1
                logger.debug(f"{'' * 4}Received chunk #{chunk_count}")
                yield chunk.text
        
        logger.debug(f"Streaming completed: received {chunk_count} chunks")