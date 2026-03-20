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
## get string example: ini_config['APP']['TASK_AI_DESCRIPTION'].replace('"', '').replace("'", "")
##
import tomllib
toml_config = None

toml_config_path = os.path.join(_base_dir_path, "pyproject.toml")
try:
    with open(toml_config_path, "rb") as f:
        toml_config = tomllib.load(f)
except FileNotFoundError:
    logger.warning(f"Missing toml config file at: '{toml_config_path}'")
    #raise FileNotFoundError(f"Missing toml config file at: '{toml_config_path}'")
    pass
except tomllib.TOMLDecodeError as e:
    raise tomllib.TOMLDecodeError(f"Error decoding TOML file: {e}")
except Exception as e:
    raise Exception(f"Error reading TOML: {e}")

def get_version_from_toml(file_path="pyproject.toml"):
    version = toml_config.get("project", {}).get("version")
    if version: return version
    else: return toml_config.get("tool", {}).get("poetry", {}).get("version")


################################  PROPERTIES  ##################################
##

#### APP BASE
APP_VERSION: str = ini_config["APP"]["VERSION"].replace('"', '').replace("'", "")
APP_NAME: str = ini_config["APP"]["NAME"].replace('"', '').replace("'", "")
# Debug
APP_LOG_LEVEL: str = json_config.get("LOG_LEVEL", "INFO")
APP_DEBUG_EXPORT_RESPONSE: bool = json_config.get("debug_export_response", True)
APP_DEBUG_RESPONSE: bool = json_config.get("debug_response", False)

#### SERVICES
## Google
GOOGLE_API_KEY: str = ini_config['GOOGLE']['GOOGLE_API_KEY'].replace('"', '').replace("'", "")

#### AI

# Initial Task Key
AI_TASK_KEY: str = json_config.get("ai_initial_task_key", "")
# Task Descriptions
AI_TASK_DESCRIPTIONS: dict[str, dict[str, list[str]]] = json_config.get("ai_task_descriptions", {})
# Initial Task Description
AI_TASK_DESCRIPTION: dict[str, str] = AI_TASK_DESCRIPTIONS.get(AI_TASK_KEY, {})
AI_TASK_DESCRIPTION: list[str] = AI_TASK_DESCRIPTION.get("description", "")

# Supported Models
AI_SUPPORTED_MODELS: dict[str, dict[str, str]] = json_config.get("ai_supported_models", {})

# Model Parameters
AI_MODEL_CONFIG: dict = json_config.get("ai_initial_model_config", None)
if not AI_MODEL_CONFIG:
    raise Exception(f"'ai_model_config' is not defined in config.json or is empty.")

# Model name
AI_MODEL_NAME: str = AI_MODEL_CONFIG.get("name", None)
if not AI_MODEL_NAME or len(AI_MODEL_NAME) == 0:
    raise Exception(f"'ai_initial_model_config.name' not defined. Please check onfig.json")

# System instructions
AI_SYSTEM_INSTRUCTIONS: list[str] = json_config.get("ai_system_instructions", [])

# Supported
AI_SUPPORTED_INPUT_FILETYPES: dict[str, str] = {
    "text/plain": ".txt", "text/xml": ".xml", "text/csv": ".csv", "text/rtf": ".rtf",
    "image/jpeg": ".jpeg", "image/png": ".png", "image/bmp": ".bmp", "image/webp": ".webp",
    "application/pdf": ".pdf",
    "application/json": ".json", 
    "text/html": ".html", 
}
# Ensure extensions have a dot prefix for endswith() to work correctly
#supported_exts = tuple(f".{ext.lstrip('.')}" for ext in config.SUPPORTED_INPUT_FILETYPES.values())
