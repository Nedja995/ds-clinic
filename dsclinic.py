##
#
#
import os
import sys
import datetime
import re;
from typing import List
import json
import logging
#
import src.api_gemini as api_gemini
# import src.exporter as exporter
from src import word_utils
from src import pdf_maker
from src.models import ReportItem, Report
#
import config
#
#
# import warnings
# warnings.filterwarnings("ignore")
# sys.stdout.reconfigure(encoding='utf-8')

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# Silence noisy third-party loggers
logging.getLogger('fontTools').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# PROGRAM PARAMETERS
SCRIPT_FILE = sys.argv[0]  # sys.executable #resource_path(".") #__file__
ROOT_DIR = os.path.dirname(os.path.abspath(SCRIPT_FILE))


print(f"---------- |DSCLINIC-{config.APP_VERSION}| Run programm with parameters: --------------")
print(f"---------- ROOT_DIR: ${ROOT_DIR}.")


config_json = {}

# Load config from a file
CONFIG_JSON_PATH = os.path.join(ROOT_DIR, "config.json")
with open(CONFIG_JSON_PATH, 'r') as f:
    config_json = json.load(f)
    

PITANJE = config_json['PITANJE']
PITANJE = "".join(PITANJE)
# PITANJE = re.sub(' +', ' ', PITANJE)
# PITANJE = re.sub("\s\s+", "", PITANJE)
PITANJE = word_utils.normalize_whitespace(PITANJE)
# if '  ' in PITANJE:
#     while '  ' in PITANJE:
#         PITANJE = PITANJE.replace('  ', '')
PITANJE = PITANJE.strip()
AI_TASK_DESCRIPTION = PITANJE
print(f"----------------------- AI TASK DESCRIPTION BEGIN: ----------------------")
print(f"{AI_TASK_DESCRIPTION}")
print(f"----------------------- AI TASK DESCRIPTION END.   ----------------------")


# Data paths
DATA_DIR = ROOT_DIR
INPUT_DIR = os.path.join(DATA_DIR, "ULAZ")
OUTPUT_DIR = os.path.join(DATA_DIR, "IZVESTAJI")
OUTPUT_DEBUG_DIR = os.path.join(OUTPUT_DIR, "DEBUG")
#

def find_input_documents() -> List[str]:
    #documents_names = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.pdf') or f.lower().endswith('.jpg') or f.lower().endswith('.jpeg') or f.lower().endswith('.png')]
    documents_names = os.listdir(INPUT_DIR)
    documents_names = [f for f in documents_names if f.lower().endswith(tuple(config_json["SUPPORTED_EXTENSIONS"]))]
    #documents_names = [f for f in documents_names if os.path.splitext(f.lower()) in config_json["SUPPORTED_EXTENSIONS"]]
    documents_filepaths = [os.path.join(INPUT_DIR, f) for f in documents_names]
    return documents_filepaths

def write_report_to_pdf(report: Report, filepath: str = "report.pdf"):
    # WRITE PDF REPORT
    # Output path
    output_filename = report.patient_name.replace(".", " ")
    output_filename = output_filename.replace("/", "")
    current_date = datetime.datetime.now().strftime("%d.%m.%Y")
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    output_path = os.path.join(OUTPUT_DIR, f"NALAZ_{output_filename}_{timestamp_str}.pdf")

    # Generate pdf
    pdf_maker.generate_report_pdf(
        patient_name=report.patient_name,
        report_date=report.report_date or current_date,
        terapija_i_saveti=report.terapija_i_saveti,
        table_data=report.nalazi,
        output_filename=output_path
    )
    
    
def obradi(data_dict: dict) -> Report:
    # formatted_json = json.dumps(data_dict, indent=4, sort_keys=False)
    # print(formatted_json)
    

    # GHENERISANJE IZVESTAJA
    result = data_dict if data_dict else {}

    if isinstance(data_dict, list) and len(data_dict) > 0:
        result = data_dict[0]
    elif isinstance(data_dict, dict):
        result = data_dict
    else:
        print(f"\n\n---------- |ERROR|DSCLINIC| - Bad response: ------\n")
        print(f"{data_dict}")
        print(f"\n-------------------------------------------------------------------\n")

    ime_pacijenta = result.get("ime_pacijenta", "NEPOZNATO")
    datum = result.get("trenutni_datum", "NEPOZNATO")
    terapija_i_saveti = result.get(config_json['MAPIRANJE']['PREPORUCENA_TERAPIJA_I_SAVET'], "NEPOZNATO")
    nalazi_list: list = result.get(config_json['MAPIRANJE']['NALAZI'], [])
    nalazi_models: List[ReportItem] = []

    for nalaz in nalazi_list:
        misljenje: str = nalaz.get(config_json['MAPIRANJE']['EXPERTSKO_MISLJENJE'], "NEPOZNATO")
        parametar_i_vrednost: str = nalaz.get(config_json['MAPIRANJE']['PARAMETAR_APARATA'], "NEPOZNATO")
        nalazi_models.append(ReportItem(misljenje=misljenje, parametar=parametar_i_vrednost))

    report: Report = Report()
    report.patient_name = ime_pacijenta
    report.report_date = datum
    report.terapija_i_saveti = terapija_i_saveti
    report.nalazi = nalazi_models
    
    return report
    


def pokreni_analizu_gemini():
    documents_filepaths = find_input_documents()

    # Call Gemini API to analyze lab result documents
    data_dict: dict = api_gemini.analyze_docs(documents_filepaths=documents_filepaths)

    print(f"---------- |GEMINI| - Analysis success. --------------")
    print(f"{data_dict}")
    print(f"------------------------------------------------------")
    
    return data_dict


def main():
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    if not os.path.exists(INPUT_DIR): os.makedirs(INPUT_DIR)

    response_json = {}

    if "False" in config_json['_DEBUG_USE_RAW_JSON_RESPONSE']:
        #
        response_json = pokreni_analizu_gemini()
        # protokoli = analyze_content(text, BASE_SYNDROMS.VELIKA_BAZA)
        response_data = obradi(response_json)
    else:
        # DEBUG INPUT
        raw_response_output_filepath = os.path.join(OUTPUT_DEBUG_DIR, f"raw_response.json")
        
        with open(raw_response_output_filepath, "r", encoding="utf-8") as file:
            response_json = json.load(file)
            response_data = obradi(response_json)
            f = 1   
    
    write_report_to_pdf(response_data)
    
    if "True" in config_json['_DEBUG_EXPORT_RAW_RESPONSE_JSON']:
        # DEBUG 
        # Output path
        output_filename = "neko nEkic" #report.patient_name.replace(".", " ")
        output_filename = output_filename.replace("/", "")
        current_date = datetime.datetime.now().strftime("%d.%m.%Y")
        timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        output_path = os.path.join(OUTPUT_DIR, f"NALAZ_{output_filename}_{timestamp_str}.pdf")
        raw_response_output_filepath = os.path.join(OUTPUT_DEBUG_DIR, f"raw_response_{output_filename}_{timestamp_str}.json")
        #
        if not os.path.exists(OUTPUT_DEBUG_DIR): os.makedirs(OUTPUT_DEBUG_DIR, exist_ok=True)
        
        with open(raw_response_output_filepath, "w", encoding="utf-8") as file:
            json.dump(response_json, file, indent=4, ensure_ascii=False) # Using indent for human-readable formatting
        
    if os.name == 'nt': os.startfile(OUTPUT_DIR)
    elif os.name == 'posix': os.system(f'open {OUTPUT_DIR}')

    input("Press Enter to exit...")


if __name__ == "__main__":
    main()
