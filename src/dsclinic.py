import os
import datetime
import json
from google.genai import types as genai_types
import config
from npy.core.utils import open_file_from_filepath, get_output_data_dirpath
from npy.core.fileutils import find_input_documents, make_output_filepath, read_debug_sample_response_json, write_response_json
import pdf_maker
from models import MedicalReportModel, GeminiModelConfig, AIServiceConfig, MedicalReport
from api_gemini import client as api_gemini_client
from api_gemini import utils as api_gemini_utils

from npy.core.logger import setup_logger

logger = setup_logger()



def get_initial_analysis_report(input_dir: str,
                                model_name: str = config.AI_MODEL_NAME,
                                debug_export_response: bool = True,
                                debug_response: bool = False,
                                ) -> MedicalReportModel:
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

    report: MedicalReportModel = gemini_client.initial_analysis_report_from_chat_stream(
        documents=input_documents_parts,
        question="".join(config.AI_TASK_DESCRIPTION)
    )

    if not debug_response and debug_export_response and report:
        response_json = report.model_dump() if report else response_json
        write_response_json(report.patient_name, response_json, os.path.join(get_output_data_dirpath(), "DEBUG"))
    return report

def analyze_inputs_and_export_report(input_dir: str,
                      output_dir: str,
                      model_name: str = config.AI_MODEL_NAME,
                      debug_export_response: bool = True,
                      debug_response: bool = False
                      ):
    """Glavna funkcija"""
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    report: MedicalReportModel = None
    response_json = {}

    if not debug_response:
        report = get_initial_analysis_report(input_dir, model_name, debug_export_response, debug_response)

        write_report_pdf(report, output_dir)

        open_file_from_filepath(output_dir)

        response_json = report.model_dump() if report else response_json
    else:
        # DEBUG: Čita iz lokalnog fajla
        response_json = read_debug_sample_response_json()

    if not debug_response and debug_export_response and response_json:
        # DEBUG: STORE JSON RESPONSE
        write_response_json(report.patient_name, response_json, os.path.join(output_dir, "DEBUG"))

def write_report_pdf(report: MedicalReportModel, output_dir: str | None = None):
    if output_dir is None: output_dir = get_output_data_dirpath()
    output_path = make_output_filepath(report.patient_name, "pdf", output_dir)

    pdf_maker.export_medical_report_pdf(
        report,
        output_filename=output_path
    )

