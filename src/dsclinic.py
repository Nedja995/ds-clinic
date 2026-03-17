import os
import datetime
import json
from typing import List
from google.genai import types as genai_types
import config
from utils import open_file_from_filepath
import pdf_maker
from models import MedicalReportModel
from api_gemini import client as api_gemini_client
from api_gemini import utils as api_gemini_utils

from logger import setup_logger
import utils

logger = setup_logger()



def get_initial_analysis_report(input_dir: str,
                                model_name: str = config.GEMINI_MODEL,
                                debug_export_response: bool = True,
                                ):
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


    client_config = api_gemini_client.GeminiConfig(api_key=config.GOOGLE_API_KEY, model_name=model_name)
    gemini_client = api_gemini_client.MedicalAnalyzerClient(config=client_config)

    report: MedicalReportModel = gemini_client.initial_analysis_report_from_chat_stream(
        input_documents_parts,
        question=config.TASK_AI_DESCRIPTION
    )

    return report

def analyze_inputs_and_export_report(input_dir: str,
                      output_dir: str,
                      model_name: str = config.GEMINI_MODEL,
                      debug_export_response: bool = True,
                      debug_response: bool = False
                      ):
    """Glavna funkcija"""
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    report: MedicalReportModel = None
    response_json = {}

    if not debug_response:
        report = get_initial_analysis_report(input_dir, model_name, debug_export_response)

        write_report_pdf(report, output_dir)

        open_file_from_filepath(output_dir)

        response_json = report.model_dump() if report else response_json
    else:
        # DEBUG: Čita iz lokalnog fajla
        response_json = read_debug_sample_response_json()

    if debug_export_response and response_json:
        # DEBUG: STORE JSON RESPONSE
        write_response_json(report.patient_name, response_json, os.path.join(output_dir, "DEBUG"))

def write_report_pdf(report: MedicalReportModel, output_dir: str | None = None):
    if output_dir is None: output_dir = utils.get_output_data_dirpath()
    output_path = make_output_filepath(report.patient_name, "pdf", output_dir)

    pdf_maker.export_medical_report_pdf(
        report,
        output_filename=output_path
    )

def read_debug_sample_response_json(name: str = "sample_response", input_filepath: str | None = None) -> dict | None:
    if not input_filepath:
        input_filepath = utils.get_resource_filepath(f"{name}.json")
        
    logger.debug(f"DEBUG MOD: Čitam podatke iz {input_filepath}")
    if os.path.exists(input_filepath):
        with open(input_filepath, "r", encoding="utf-8") as file:
            response_json = json.load(file)
    else:
        logger.error(f"Fajl za debug mod ne postoji na putanji: {input_filepath}")
        raise FileNotFoundError(f"Fajl za debug mod ne postoji na putanji: {input_filepath}")
    
    return response_json

def write_response_json(name: str, response_json: dict, output_dir: str | None = None):
    if not output_dir:
        output_dir = utils.get_output_data_dirpath()
        output_dir = os.path.join(output_dir, "DEBUG")
        if not os.path.exists(output_dir): os.makedirs(output_dir, exist_ok=True)

    response_json_filepath = make_output_filepath(name, "json", output_dir)

    with open(response_json_filepath, "w", encoding="utf-8") as file:
        json.dump(response_json, file, indent=4, ensure_ascii=False)
        logger.info(f"Written JSON response to {response_json_filepath}")

def find_input_documents(input_dir: str) -> list[str]:
    if not os.path.exists(input_dir):
        logger.error(f"Input directory not found: {input_dir}")
        return []
    # List files
    filepaths = os.listdir(input_dir)
    # Ensure extensions have a dot prefix for endswith() to work correctly
    supported_exts = tuple(f".{ext.lstrip('.')}" for ext in config.SUPPORTED_INPUT_FILETYPES.values())
    filepaths = [f for f in filepaths if f.lower().endswith(supported_exts)]
    documents_filepaths = [os.path.join(input_dir, f) for f in filepaths]
    return documents_filepaths

def make_output_filepath(patient_name: str, extension: str, output_dir: str | None) -> str:
    if not output_dir: output_dir = utils.get_output_data_dirpath()
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    output_path = os.path.join(output_dir, f"NALAZ_{patient_name}_{timestamp_str}.{extension}")
    return output_path