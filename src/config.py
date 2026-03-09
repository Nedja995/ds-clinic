##
# Configuration file for DSClinic project
#
from enum import StrEnum
import os.path
import sys
import json
from logger import setup_logger
from utils import get_base_dir_path

logger = setup_logger()

##### APP #####
#APP_VERSION = "v2.0.1"

######### PROGRAM RUN SETTINGS #########

#### GEMINI

## Tinking level
ARG_GEMINI_THINKING_LEVEL_STR: str = "HIGH"

## Models
class GEMINI_MODELS(StrEnum):
  """The model names, find more <link>"""
  GEMINI_3_PRO_PREVIEW = "gemini-3-pro-preview"
  GEMINI_3_FLASH_PREVIEW = "gemini-3-flash-preview"
  GEMINI_PRO = "gemini-pro"

## AI Task descriptions
class AI_TASKS(StrEnum):
  """AI analysis task descriptions."""
  TASK_1 = "Make analysis from these two laboratory results"
  TASK_2 = "Analiziraj laboratorijske nalaze i uporedi sa prethodnim nalazom. Pronadji anomalije i promene u odnosu na prethodni nalaz. Napravi detaljnu analizu i predlozi moguce dijagnoze i preporuke za dalje korake."
  TASK_3 = "Spoji, analiziraj i sumiraj analizu iz dva nalaza jedan je iz MetaHuner program a drugi je iz labaratorije"
  TASK_4 = "Procitaj podatke iz dokumenata/izvestaja i ukazi na kriticne nalaze, predstavi podatke formatirane u json formatu, koji sadrzi polje 'ime_pacijenta', polje 'datum' (trenutni), polje 'dijagnoza_bolesti', polje 'dijagnoza_summarized', polje 'dijagnoza', polje 'strucno_misljenje_dijagnoza_summarized', polje 'preporucena_terapija_i_savet_summarized', polje 'nalazi' u dictionary formatu sa poljima, 'misljenje_i_dijagnoza', polje 'parametar', vrednost', 'status', 'znacaj', 'parametar_i_vrednost', 'dijagnoza'."
  TASK_5 = "spoji podatke iz oba dokumenta i ukazi na kriticne nalaze, nije bitno da li su od razlicitih pacijenata, prikazi ih kao json listu"
  TASK_6 = "Merge medical data from all documents and show critical symptoms summarized in Serbian language"
  TASK_7 = "spoji podatke iz oba dokumenta i ukazi na kriticne nalaze, nije bitno da li su od razlicitih pacijenata"
  TASK_8 = "spoji podatke iz oba dokumenta i ukazi na kriticne nalaze, nije bitno da li su od razlicitih pacijenata i prikazi ih kao json lista, a zatim napravi detaljnu analizu i predlozi moguce dijagnoze i preporuke za dalje korake"
  # TASK_9 = ("Procitaj podatke iz dokumenata/izvestaja i ukazi na kriticne nalaze i gde su problemi, predstavi podatke formatirane u json formatu, koji sadrzi polje 'ime_pacijenta', polje 'datum' (trenutni), polje 'dijagnoza_bolesti', polje 'dijagnoza_summarized', polje 'dijagnoza', polje 'strucno_misljenje_dijagnoza_summarized', polje 'preporucena_terapija_i_savet_summarized', polje 'gde je problem', polje 'rezime', polje 'uzrok_problema', polje 'nalazi' u dictionary formatu sa poljima, 'misljenje_i_dijagnoza', polje 'parametar', vrednost', 'status', 'znacaj', 'parametar_i_vrednost', 'dijagnoza', 'gde_je_problem', 'rezime', 'uzrok_problema', 'uzrok_problema_detaljno', 'uzrok_problema_summarized'."
  TASK_9 = ("Procitaj podatke iz medicinskih svih prilozenih dokumenata, nalaza, rezultata, izvestaja i ostalih podataka i " 
            "ukazi na kriticne nalaze, predlozi moguce dijagnoze, gde su problemi i sta su uzroci."
            "Predstavi podatke u json formatu, koristeci sledecu strukturu:"
            "{ "
            "   'ime_pacijenta', "
            "   'trenutni_datum', "
            "   'dijagnoza_bolesti', "
            "   'dijagnoza_summarized', "
            "   'dijagnoza', "
            "   'strucno_misljenje_dijagnoza_summarized', "
            "   'preporucena_terapija_i_savet_summarized', "
            "   'gde_je_problem', "
            "   'rezime', "
            "   'uzrok_problema', "
            "   'uzrok_problema_detaljno', "
            "   'uzrok_problema_summarized', "
            "   'nalazi': [ "
            "       { "
            "           'misljenje_i_dijagnoza', "
            "           'parametar', "
            "           'vrednost', "
            "           'status', "
            "           'znacaj', "
            "           'parametar_i_vrednost', "
            "           'dijagnoza', "
            "           'gde_je_problem', "
            "           'rezime', "
            "           'uzrok_problema', "
            "           'uzrok_problema_detaljno', "
            "           'uzrok_problema_summarized' "
            "       }, "
            "   ] "
            "} "
            " "
  )



# --- Global Configuration ---
_base_dir_path = get_base_dir_path()
json_config: dict[str, any] = {}
json_config_path = os.path.join(_base_dir_path, "config.json")

try:
    with open(json_config_path, 'r', encoding='utf-8') as f:
        json_config = json.load(f)
except FileNotFoundError:
    logger.error(f"Ne mogu da pronađem config.json na putanji: {json_config_path}")
    print("Enter to exit...")
    input() # Dodato da se konzola ne zatvori odmah
    sys.exit(1)
except json.JSONDecodeError as e:
    logger.error(f"Ne mogu da dekodiram config.json! Greška:\n{e}")
    print("Enter to exit...")
    input() # Dodato da se konzola ne zatvori odmah
    sys.exit(1)
    
# ##
# #
# TASK_AI_DESCRIPTION: str = json_config.get("PITANJE", "")
# TASK_AI_DESCRIPTION = "".join(TASK_AI_DESCRIPTION)
# import word_utils
# TASK_AI_DESCRIPTION = word_utils.normalize_whitespace(TASK_AI_DESCRIPTION)
# logger.info(f"----------------------- AI TASK DESCRIPTION BEGIN: ----------------------")
# logger.info(f"{TASK_AI_DESCRIPTION}")
# logger.info(f"----------------------- AI TASK DESCRIPTION END.   ----------------------")


##
#
SUPPORTED_EXTENSIONS: list[str] = [
    ".jpg", ".jpeg", ".png", 
    ".pdf"
]



##
#
import configparser

ini_config_path = os.path.join(_base_dir_path, "settings.ini")

ini_config = configparser.ConfigParser()
ini_config.read(ini_config_path)


GOOGLE_API_KEY: str = ini_config['GOOGLE']['GOOGLE_API_KEY'].replace('"', '').replace("'", "")

TASK_AI_DESCRIPTION: str = ini_config['APP']['TASK_AI_DESCRIPTION'].replace('"', '').replace("'", "")
GEMINI_MODEL: str = ini_config['GOOGLE']['GEMINI_MODEL'].replace('"', '').replace("'", "")



##
#
import tomllib
from pathlib import Path

def get_version_from_toml(file_path="pyproject.toml"):
    """Reads the project version directly from the pyproject.toml file."""
    try:
        with open(os.path.join(_base_dir_path, file_path), "rb") as f:
            data = tomllib.load(f)
        version = data.get("project", {}).get("version")
        if version:
            return version
        else:
            # Handle cases where the version is dynamic or in a different section (e.g., tool.poetry)
            return data.get("tool", {}).get("poetry", {}).get("version")
    except FileNotFoundError:
        return "unknown (pyproject.toml not found)"
    except Exception as e:
        return f"error reading TOML: {e}"

# Example usage:
# print(f"App version from TOML file: {get_version_from_toml()}")
APP_VERSION: str = get_version_from_toml()
#
LOG_LEVEL: str = ini_config["APP"]["LOG_LEVEL"]