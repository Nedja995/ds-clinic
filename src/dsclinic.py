import os
import datetime
import json
from typing import List
from google.genai import types as genai_types
from models import DSClinicReport
import config, pdf_maker
from api_gemini import client as api_gemini_client
from api_gemini import utils as api_gemini_utils

from logger import setup_logger

logger = setup_logger()


def process_documents(input_dir: str, output_dir: str, debug_mode: bool = False, model_name: str = config.GEMINI_MODELS.GEMINI_3_PRO_PREVIEW.value):
    """Glavna funkcija koju poziva dsclinic_cli.py konzolna aplikacija"""
    model_name = config.GEMINI_MODEL
    
    output_debug_dir = os.path.join(output_dir, "DEBUG")
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    if not os.path.exists(input_dir): os.makedirs(input_dir)

    if not debug_mode:
        documents_filepaths = find_input_documents(input_dir)
        if not documents_filepaths:
            logger.error(f"Nisu pronađeni fajlovi za analizu u folderu: {input_dir}")
            return
         
        input_documents_parts: list[genai_types.Part] = []
        for doc_filepath in documents_filepaths:
            part = api_gemini_utils.load_document_from_file(doc_filepath)
            if part:
                input_documents_parts.append(part)

        client_config = api_gemini_client.GeminiConfig(api_key=config.GOOGLE_API_KEY, model_name=model_name)
        gemini_client = api_gemini_client.MedicalAnalyzerClient(config=client_config)
        
        report: DSClinicReport = gemini_client.initial_analysis_report_from_chat_stream(
            input_documents_parts, 
            question=config.TASK_AI_DESCRIPTION
        )

        output_filename = report.patient_name.replace(".", " ").replace("/", "")
        timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        output_path = os.path.join(output_dir, f"NALAZ_{output_filename}_{timestamp_str}.pdf")

        pdf_maker.export_report(
            report, 
            output_filename=output_path
        )

        response_json = report.model_dump() if report else {}
        logger.info("USPEH: Izveštaj je uspešno generisan!")
        
        # Otvaranje foldera
        if os.name == 'nt': os.startfile(output_dir)
        elif os.name == 'posix': os.system(f'open "{output_dir}"')
    else:
        # DEBUG MODE: Čita iz lokalnog fajla
        raw_response_output_filepath = os.path.join(output_debug_dir, f"raw_response.json")
        logger.debug(f"DEBUG MOD: Čitam podatke iz {raw_response_output_filepath}")
        if os.path.exists(raw_response_output_filepath):
            with open(raw_response_output_filepath, "r", encoding="utf-8") as file:
                response_json = json.load(file)
                #report = obradi(response_json)
        else:
            logger.error(f"Fajl za debug mod ne postoji na putanji: {raw_response_output_filepath}")
            return
    
    if response_json:
        # Pisanje u PDF
        #write_report_to_pdf(report, output_dir)
        logger.debug("Raw json writen to /Debug/ directory.")
    
        # Čuvanje JSON kopije
        if config.json_config['_DEBUG_EXPORT_RAW_RESPONSE_JSON'] == "True":
            output_filename = report.patient_name.replace(".", " ").replace("/", "")
            timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
            raw_response_output_filepath = os.path.join(output_debug_dir, f"raw_response_{output_filename}_{timestamp_str}.json")
            
            if not os.path.exists(output_debug_dir): os.makedirs(output_debug_dir, exist_ok=True)
            with open(raw_response_output_filepath, "w", encoding="utf-8") as file:
                json.dump(response_json, file, indent=4, ensure_ascii=False)



def find_input_documents(input_dir: str) -> List[str]:
    if not os.path.exists(input_dir):
        return []
    documents_names = os.listdir(input_dir)
    # Ensure extensions have a dot prefix for endswith() to work correctly
    supported_exts = tuple(f".{ext.lstrip('.')}" for ext in config.SUPPORTED_EXTENSIONS)
    documents_names = [f for f in documents_names if f.lower().endswith(supported_exts)]
    documents_filepaths = [os.path.join(input_dir, f) for f in documents_names]
    return documents_filepaths