import os
import datetime
import json
from google.genai import types as genai_types
import config
from npy.core.utils import get_output_data_dirpath
from npy.core.fileutils import find_input_documents, make_output_filepath, open_file_from_filepath
import pdf_maker
from models import MedicalReportModel, GeminiModelConfig, AIServiceConfig, MedicalReport
from api_gemini import client as api_gemini_client
from api_gemini import utils as api_gemini_utils

from npy.core.logger import setup_logger

logger = setup_logger()



def get_initial_analysis_report(input_dir: str,
                                model_name: str = config.AI_MODEL_NAME
                                ) -> MedicalReport:
    """Glavna funkcija"""
    if not os.path.exists(input_dir): os.makedirs(input_dir, exist_ok=True)
    
    # Find documents
    documents_filepaths = find_input_documents(input_dir)
    if not documents_filepaths:
        logger.info(f"Files not found in input directory: {input_dir}")

    # Load documents
    input_documents_parts: list[genai_types.Part] = []
    for doc_filepath in documents_filepaths:
        part = api_gemini_utils.load_document_from_file(doc_filepath)
        if part: input_documents_parts.append(part)

    # AI Client
    client_config = AIServiceConfig(api_key=config.GOOGLE_API_KEY, model_settings=GeminiModelConfig(model_name=model_name))
    gemini_client = api_gemini_client.MedicalAnalyzerClient(config=client_config)

    # Run Analyzis
    report_content: MedicalReportModel = gemini_client.initial_analysis_report_from_chat_stream(
        documents=input_documents_parts,
        question="".join(config.AI_TASK_DESCRIPTION)
    )
    
    report = MedicalReport(content=report_content)
        
    return report

def write_report_pdf(report: MedicalReport, output_dir: str | None = None):
    if output_dir is None: output_dir = get_output_data_dirpath()
    output_path = make_output_filepath(report.content.patient_name, "pdf", output_dir)

    pdf_maker.export_medical_report_pdf(
        report,
        output_filename=output_path
    )

