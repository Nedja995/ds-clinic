##
# Configuration file for DSClinic project
#
import os.path
import sys
import json
from npy.core.logger import setup_logger
from npy.core.utils import get_base_dir_path

logger = setup_logger()

##
_base_dir_path = get_base_dir_path()


############################  LOAD JSON CONFIG  ################################
##
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


#############################  LOAD INI CONFIG  ################################
##
import configparser
ini_config = configparser.ConfigParser()

ini_config_path = os.path.join(_base_dir_path, "settings.ini")
ini_config.read(ini_config_path)


#############################  LOAD TOML CONFIG  ###############################
##
import tomllib
toml_config = None

toml_config_path = os.path.join(_base_dir_path, "pyproject.toml")
try:
    with open(toml_config_path, "rb") as f:
        toml_config = tomllib.load(f)
except FileNotFoundError:
    raise FileNotFoundError(f"Missing toml config file at: '{toml_config_path}'")
except Exception as e:
    raise Exception(f"Error reading TOML: {e}")

def get_version_from_toml(file_path="pyproject.toml"):
    version = toml_config.get("project", {}).get("version")
    if version: return version
    else: return toml_config.get("tool", {}).get("poetry", {}).get("version")



################################  PROPERTIES  ##################################
##
#

#### APP BASE
APP_VERSION: str = get_version_from_toml()
# Debug
APP_LOG_LEVEL: str = ini_config["APP"]["LOG_LEVEL"].replace('"', '').replace("'", "")

#### SERVICES
## Google
GOOGLE_API_KEY: str = ini_config['GOOGLE']['GOOGLE_API_KEY'].replace('"', '').replace("'", "")

#### AI
AI_TASK_DESCRIPTION: str = ini_config['APP']['TASK_AI_DESCRIPTION'].replace('"', '').replace("'", "")
# import word_utils
# AI_TASK_DESCRIPTION = word_utils.normalize_whitespace("".join(json_config.get("PITANJE", "")))
AI_MODEL_NAME: str = ini_config['GOOGLE']['GEMINI_MODEL'].replace('"', '').replace("'", "")

AI_SUPPORTED_INPUT_FILETYPES: dict[str, str] = {
    "text/plain": ".txt", "text/xml": ".xml", "text/csv": ".csv", "text/rtf": ".rtf",
    "image/jpeg": ".jpeg", "image/png": ".png", "image/bmp": ".bmp", "image/webp": ".webp",
    "application/pdf": ".pdf",
    "application/json": ".json", 
    "text/html": ".html", 
}
# Ensure extensions have a dot prefix for endswith() to work correctly
#supported_exts = tuple(f".{ext.lstrip('.')}" for ext in config.SUPPORTED_INPUT_FILETYPES.values())
