##
#
#
import os
import sys
import datetime
import re;
from typing import List
import json
#
import src.api_gemini as api_gemini
# import src.exporter as exporter
from src import word_utils
from src import pdf_maker
from src.models import ReportItem
#
import config
#
#
# import warnings
# warnings.filterwarnings("ignore")
# sys.stdout.reconfigure(encoding='utf-8')


# PROGRAM PARAMETERS
SCRIPT_FILE = sys.argv[0]  # sys.executable #resource_path(".") #__file__
ROOT_DIR = os.path.dirname(os.path.abspath(SCRIPT_FILE))


print(f"\n---------- |DSCLINIC-{config.APP_VERSION}| Run programm with parameters: --------------")
print(f"\n---------- ROOT_DIR: ${ROOT_DIR}.")


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
print(f"\n----------------------- AI TASK DESCRIPTION BEGIN: ----------------------")
print(f"\n{AI_TASK_DESCRIPTION}")
print(f"\n----------------------- AI TASK DESCRIPTION END.   ----------------------")




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


def pokreni_analizu_gemini():
    documents_filepaths = find_input_documents()

    # Call Gemini API to analyze lab result documents
    results_dict: dict = api_gemini.analyze_docs(documents_filepaths=documents_filepaths)

    print(f"\n---------- |GEMINI| - Analysis success. --------------\n")
    print(f"{results_dict}")
    print(f"\n-------------------------------------------------------------------\n")
    print(f"---------------------------------------------------------------------")
    formatted_json = json.dumps(results_dict, indent=4, sort_keys=False)
    print(formatted_json)
    

    # GHENERISANJE IZVESTAJA
    result = results_dict if results_dict else {}

    if isinstance(results_dict, list) and len(results_dict) > 0:
        result = results_dict[0]
    elif isinstance(results_dict, dict):
        result = results_dict
    else:
        print(f"\n\n---------- |ERROR|DSCLINIC| - Bad response: ------\n")
        print(f"{results_dict}")
        print(f"\n-------------------------------------------------------------------\n")
        
    ime_pacijenta = result.get("ime_pacijenta", "NEPOZNATO")
    datum = result.get("trenutni_datum", "NEPOZNATO")
    strucno_misljenje_dijagnoza = result.get(config_json['MAPIRANJE']['PREPORUCENA_TERAPIJA_I_SAVET'], "NEPOZNATO")
    nalazi_list: list = result.get(config_json['MAPIRANJE']['NALAZI'], [])
    nalazi_models: List[ReportItem] = []

    for nalaz in nalazi_list:
        misljenje: str = nalaz.get(config_json['MAPIRANJE']['EXPERTSKO_MISLJENJE'], "NEPOZNATO")
        parametar_i_vrednost: str = nalaz.get(config_json['MAPIRANJE']['PARAMETAR_APARATA'], "NEPOZNATO")
        nalazi_models.append(ReportItem(misljenje=misljenje, parametar=parametar_i_vrednost))

    # WRITE PDF REPORT

    # ANALIZA TEXTA I NALAZAK PROTOKOLA
    #protokoli: list = [{"nalaz": "Neki nalaz", "terapija": ["terapija1", "terapija2"], "napomena": "Napomena o terapiji"},]
    # protokoli = analyze_content(text, BASE_SYNDROMS.VELIKA_BAZA)

    # WRITE PDF REPORT
    # Output path
    output_filename = ime_pacijenta.replace(".", " ")
    output_filename = output_filename.replace("/", "")
    current_date = datetime.datetime.now().strftime("%d.%m.%Y")
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    output_path = os.path.join(OUTPUT_DIR, f"NALAZ_{output_filename}_{timestamp_str}.pdf")
    # Create dirs if need
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # Generate pdf
    pdf_maker.generate_report_pdf(
        patient_name=ime_pacijenta,
        report_date=current_date,
        terapija_i_saveti=strucno_misljenje_dijagnoza,
        table_data=nalazi_models,
        output_filename=output_path
    )
    
    #
    if 'true' in config_json['EXPORT_RAW_RESPONSE_JSON']:
        raw_response_output_filepath = os.path.join(OUTPUT_DEBUG_DIR, f"NALAZ_{output_filename}_{timestamp_str}.json")
        with open(raw_response_output_filepath, "w") as file:
            json.dump(formatted_json, file, indent=4) # Using indent for human-readable formatting
        
    print(f"\n--------------- PROGRAM COMPLETE --------------------------\n")


def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    if not os.path.exists(OUTPUT_DEBUG_DIR):
        os.makedirs(OUTPUT_DEBUG_DIR)
    if not os.path.exists(INPUT_DIR):
        os.makedirs(INPUT_DIR)

    # pokreni_analizu()
    pokreni_analizu_gemini()

    if os.name == 'nt':
        os.startfile(OUTPUT_DIR)
    elif os.name == 'posix':
        os.system(f'open {OUTPUT_DIR}')

    input("Press Enter to exit...")


if __name__ == "__main__":
    main()
