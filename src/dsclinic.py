import os
import datetime
import json
from google.genai import types as genai_types
import config
from npy.core.settings_manager import load_saved_settings, save_settings
from models_new.config import AppSettings
from npy.core.utils import get_output_data_dirpath, get_input_data_dirpath
from npy.core.fileutils import find_input_documents, make_output_filepath, open_file_from_filepath
import pdf_maker
from models import MedicalReportModel, GeminiModelConfig, AIServiceConfig, MedicalReport
from api_gemini import client as api_gemini_client
from api_gemini import utils as api_gemini_utils

from npy.core.logger import setup_logger

logger = setup_logger()

class DSClinic:
    """Glavna logika za DSClinic aplikaciju."""
    
    def __init__(self, model_name: str = config.AI_MODEL_NAME):
        # ── settings ──────────────────────────────────────────────────────
        # from npy.core.settings_manager import load_saved_settings, save_settings
        saved = load_saved_settings()
        appSettings = AppSettings(**{k: v for k, v in saved.items() if not k.startswith("_")})
        self.input_dir = appSettings.input_dir
        self.output_dir = get_output_data_dirpath()
        self.model_name = model_name
        logger.info(f"Initializing DSClinic with model: {self.model_name}, input_dir: {self.input_dir}, output_dir: {self.output_dir}")
        
        # AI Client
        self.client_config = AIServiceConfig(api_key=config.GOOGLE_API_KEY, model_settings=GeminiModelConfig(
            model_name=model_name, 
            system_instruction=config.AI_SYSTEM_INSTRUCTIONS,
            thinking_level=config.AI_THINKING_LEVEL,
            temperature=config.AI_MODEL_TEMPERATURE,
            top_p=config.AI_MODEL_TOP_P,
            max_output_tokens=config.AI_MODEL_MAX_OUTPUT_TOKENS
        ))
        self.gemini_client = api_gemini_client.MedicalAnalyzerClient(config=self.client_config)
        
        self.report: MedicalReport | None = None
    
    def get_initial_analysis_report(self) -> MedicalReport:
        """Glavna funkcija"""
        logger.info("Starting initial analysis report generation...")
        if not os.path.exists(self.input_dir):
            raise FileNotFoundError(f"Input directory not found: {self.input_dir}")
        
        # Get input dir
        saved = load_saved_settings()
        appSettings = AppSettings(**{k: v for k, v in saved.items() if not k.startswith("_")})
        self.input_dir = appSettings.input_dir
        
        # Find documents
        documents_filepaths = find_input_documents(self.input_dir)
        if not documents_filepaths:
            logger.info(f"Files not found in input directory: {self.input_dir}")

        # Load documents
        input_documents_parts: list[genai_types.Part] = []
        for doc_filepath in documents_filepaths:
            part = api_gemini_utils.load_document_from_file(doc_filepath)
            if part: input_documents_parts.append(part)

        # Run Analyzis
        report_content: MedicalReportModel = self.gemini_client.initial_analysis_report_from_chat_stream(
            documents=input_documents_parts,
            question=config.AI_INITIAL_TASK_DESCRIPTION
        )
        
        self.report = MedicalReport(content=report_content)
            
        return self.report
    
    
    def ask_followup_question(self, question: str) -> str:
        if not self.report:
            raise ValueError("No initial report available. Please run analysis first.")
        
        # Placeholder for actual AI interaction
        # In a real scenario, this would involve sending the question and report context to the AI model
        # followup_response = self.gemini_client.ask_followup_stream(
        #     report_content=self.report.content, question=question
        # )
        followup_response = self.gemini_client.ask_followup_question(question)
        
        return followup_response


def write_report_pdf(report: MedicalReport, output_dir: str | None = None):
    if output_dir is None: output_dir = get_output_data_dirpath()
    output_path = make_output_filepath(report.content.patient_name, "pdf", output_dir)

    pdf_maker.generate_report_pdf_at_filepath(
        report,
        output_filename=output_path
    )