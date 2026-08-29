import os
import datetime
import json
from google.genai import types as genai_types
from npy.core.utils import get_output_data_dirpath, get_input_data_dirpath
from npy.core.fileutils import find_input_documents, make_output_filepath, open_file_from_filepath
import pdf_maker
from models import (
    app_settings,
    MedicalReportModel,
    GeminiModelConfig,
    AIServiceConfig,
    MedicalReport,
)
from api_gemini import client as api_gemini_client
from api_gemini import utils as api_gemini_utils

from npy.core.logger import setup_logger

logger = setup_logger()

class DSClinic:
    """Glavna logika za DSClinic aplikaciju."""
    
    def __init__(self, model_name: str | None = None):
        # ── settings ──────────────────────────────────────────────────────
        self.input_dir = app_settings.input_dir
        self.output_dir = get_output_data_dirpath()
        self.model_name = model_name or app_settings.ai_model_name
        logger.info(f"Initializing DSClinic with model: {self.model_name}, input_dir: {self.input_dir}, output_dir: {self.output_dir}")
        
        # AI Client Config
        self.client_config = AIServiceConfig(
            api_key=app_settings.google_api_key,
            model_settings=GeminiModelConfig(
                model_name=self.model_name, 
                system_instruction=tuple(app_settings.ai_system_instructions),
                thinking_level=app_settings.ai_thinking_level,
                temperature=app_settings.ai_model_temperature,
                top_p=app_settings.ai_model_top_p,
                max_output_tokens=app_settings.ai_model_max_output_tokens
            )
        )
        self.gemini_client = api_gemini_client.MedicalAnalyzerClient(config=self.client_config)
        self.report: MedicalReport | None = None
    
    def get_initial_analysis_report(self, scrubbed_files_map: dict[str, str] | None = None) -> MedicalReport:
        """Glavna funkcija za analizu nalaza."""
        logger.info("Starting initial analysis report generation...")
        if not os.path.exists(self.input_dir):
            raise FileNotFoundError(f"Input directory not found: {self.input_dir}")
        
        # Sync input directory in case settings were updated
        self.input_dir = app_settings.input_dir
        
        # ── CHECK: VERIFY IF ANONYMIZATION TOGGLE IS ACTIVE ──────────────────
        anonymization_enabled = app_settings.anonymization_on
        # ──────────────────────────────────────────────────────────────────────
        
        # Find documents
        documents_filepaths = find_input_documents(self.input_dir)
        if not documents_filepaths:
            logger.info(f"Files not found in input directory: {self.input_dir}")

        # Load documents
        input_documents_parts: list[genai_types.Part] = []
        for doc_filepath in documents_filepaths:
            if "ANONIMIZOVANO" in doc_filepath or "_scrubbed" in doc_filepath:
                continue

            # ── CONDITIONAL FILE MAPPING PATTERN BLOCK ────────────────────────
            if anonymization_enabled:
                # If the original file was a PDF, look for its generated page images inside ANONIMIZOVANO
                if doc_filepath.lower().endswith('.pdf'):
                    parent_dir = os.path.dirname(doc_filepath)
                    filename = os.path.basename(doc_filepath)
                    base, _ = os.path.splitext(filename)
                    anonymized_subfolder = os.path.join(parent_dir, "ANONIMIZOVANO")
                    
                    # Find all processed pages for this specific PDF file
                    if os.path.exists(anonymized_subfolder):
                        for file in os.listdir(anonymized_subfolder):
                            if file.startswith(f"{base}_scrubbed_page_") and file.lower().endswith('.jpg'):
                                page_path = os.path.join(anonymized_subfolder, file)
                                logger.info(f"PDF Page Mapping active: Loading {page_path} for Gemini")
                                part = api_gemini_utils.load_document_from_file(page_path)
                                if part: input_documents_parts.append(part)
                    continue

                # Standard single-image file replacement mapping
                target_filepath = doc_filepath
                if scrubbed_files_map and doc_filepath in scrubbed_files_map:
                    target_filepath = scrubbed_files_map[doc_filepath]
                    logger.info(f"Anonymization map active: Swapping {doc_filepath} -> {target_filepath}")
            else:
                # If anonymization toggle is turned off, parse the raw input directly
                target_filepath = doc_filepath
                logger.info(f"Anonymization disabled by user: Loading original asset path {target_filepath}")
            # ──────────────────────────────────────────────────────────────────
            
            part = api_gemini_utils.load_document_from_file(target_filepath)
            if part: input_documents_parts.append(part)

        # Clean up question to be a single-line string without newlines and unnecessary spaces to spare tokens
        raw_question = app_settings.ai_initial_task_description
        cleaned_question = " ".join(raw_question.split())

        # Run Analysis
        report_content: MedicalReportModel = self.gemini_client.initial_analysis_report_from_chat_stream(
            documents=input_documents_parts,
            question=cleaned_question
        )
        
        self.report = MedicalReport(content=report_content)
        return self.report

    def ask_followup_question(self, question: str) -> str:
        if not self.report:
            raise ValueError("No initial report available. Please run analysis first.")
        
        followup_response = self.gemini_client.ask_followup_question(question)
        return followup_response


def write_report_pdf(report: MedicalReport, output_dir: str | None = None):
    if output_dir is None: output_dir = get_output_data_dirpath()
    output_path = make_output_filepath(report.content.patient_name, "pdf", output_dir)

    pdf_maker.generate_report_pdf_at_filepath(
        report,
        output_filename=output_path
    )
