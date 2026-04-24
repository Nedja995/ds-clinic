##
# Configuration file for DSClinic project
#
import os.path
import sys
import json
from npy.core.logger import setup_logger
from npy.core.utils import get_base_dir_path

logger = setup_logger()

###########################  APP ROOT DIRECTORY  ###############################
##
_base_dir_path = get_base_dir_path()


############################  LOAD JSON CONFIG  ################################
##
json_config: dict[str, any] = {}                                          # Load JSON config with error handling
json_config_path: str       = os.path.join(_base_dir_path, "config.json") # Path to config.json

try:
    with open(json_config_path, 'r', encoding='utf-8') as f:
        json_config = json.load(f)
except FileNotFoundError:
    logger.error(f"Ne mogu da pronađem config.json na putanji: {json_config_path}")
    # Dodato da se konzola ne zatvori odmah
    print("Enter to exit...")
    input()
    # Exit app with error code
    sys.exit(1)
except json.JSONDecodeError as e:
    logger.error(f"Ne mogu da dekodiram config.json! Greška:\n{e}")
    # Dodato da se konzola ne zatvori odmah
    print("Enter to exit...")
    input() 
    # Exit app with error code
    sys.exit(1)


#############################  LOAD INI CONFIG  ################################
##
# Using configparser to load settings.ini
import configparser
ini_config = configparser.ConfigParser()
# Path to settings.ini
ini_config_path = os.path.join(_base_dir_path, "settings.ini")
# Read the INI config file
ini_config.read(ini_config_path, encoding='utf-8')


##############################  READ CONFIG PROPERTIES  ################################
##

###########  APP BASE  ###########
#
APP_VERSION: str                = ini_config["APP"]["VERSION"].replace('"', '').replace("'", "")
APP_NAME: str                   = ini_config["APP"]["NAME"].replace('"', '').replace("'", "")

###########  DEBUG  ##############
#
APP_LOG_LEVEL: str              = json_config.get("app", {}).get("log_level", "INFO")
APP_DEBUG_EXPORT_RESPONSE: bool = json_config.get("app", {}).get("debug_export_response", True)
APP_DEBUG_RESPONSE: bool        = json_config.get("app", {}).get("debug_response", False)
                                                          
###########  SERVICES  ###########
#
GOOGLE_API_KEY: str    = ini_config['GOOGLE']['GOOGLE_API_KEY'].replace('"', '').replace("'", "")       # GOOGLE API (Gemini)
ANTHROPIC_API_KEY: str = ini_config['ANTHROPIC']['ANTHROPIC_API_KEY'].replace('"', '').replace("'", "") # ANTHROPIC API (Claude)

###########  AI CONFIG  ##########
##
AI_TASK_KEY: str                                      = json_config.get("ai_initial_task_key", "")          # Initial Task Key (TODO: check is neccessery)
AI_TASK_DESCRIPTIONS: dict[str, dict[str, list[str]]] = json_config.get("ai_task_descriptions", {})         # Task Descriptions
AI_TASK_DESCRIPTION:  dict[str, str]                  = AI_TASK_DESCRIPTIONS.get(AI_TASK_KEY, {})           # Initial Task Description dict
AI_TASK_DESCRIPTION:  str                             = "".join(AI_TASK_DESCRIPTION.get("description", [])) # Initial Task Description string

# Supported Models (Gemini)
AI_SUPPORTED_MODELS: dict[str, str] = json_config.get("ai_supported_models", {})

# Model Parameters
AI_MODEL_CONFIG: dict = json_config.get("ai_initial_model_config", None)
if not AI_MODEL_CONFIG:
    raise Exception(f"'ai_model_config' is not defined in config.json or is empty.")

# Model name
AI_MODEL_NAME: str = AI_MODEL_CONFIG.get("name", None)
if not AI_MODEL_NAME or len(AI_MODEL_NAME) == 0:
    raise Exception(f"'ai_initial_model_config.name' not defined. Please check onfig.json")

AI_MODEL_TOP_P: float = AI_MODEL_CONFIG.get("top_p", 0.95)
AI_MODEL_TEMPERATURE: float = AI_MODEL_CONFIG.get("temperature", 1.0)
AI_MODEL_MAX_OUTPUT_TOKENS: int = AI_MODEL_CONFIG.get("max_output_tokens", 65535)
AI_MODEL_TOP_K: int = AI_MODEL_CONFIG.get("top_k", 64)
AI_THINKING_LEVEL: str = AI_MODEL_CONFIG.get("thinking_level", "default")

# System instructions
AI_SYSTEM_INSTRUCTIONS: list[str] = json_config.get("ai_system_instructions", [])

AI_INITIAL_TASK_DESCRIPTION: str = "".join(json_config.get("ai_initial_task_description", [
    "Analyze given medical documents like labaratory results, holistic results and other medical reports.",
    "and answer questions about medical conditions, issues, causses of issues, treatments, and general health advice. ",
    "Provide accurate and concise information. ",
    "If you don't know the answer, state that you don't know. ",
    "Always answer in Serbian."
]))

# Supported
AI_SUPPORTED_INPUT_FILETYPES: dict[str, str] = json_config.get("ai_supported_input_filetypes", {})
# Ensure extensions have a dot prefix for endswith() to work correctly
#supported_exts = tuple(f".{ext.lstrip('.')}" for ext in config.SUPPORTED_INPUT_FILETYPES.values())

AI_RESPONSE_DESCRIPTION: dict[str, str] = json_config.get("ai_response_description", {})

AI_RESPONSE_RECOMMENDED_THERAPY_AND_ADVICE: str = AI_RESPONSE_DESCRIPTION.get(
    "ai_response_recommended_therapy_and_advice", 
    "Comprehensive summary including: root cause analysis, diagnosis summary, recommended therapy, lifestyle advice, and next steps.")

AI_RESPONSE_CRITICAL_FINDINGS: str = AI_RESPONSE_DESCRIPTION.get(
    "ai_response_critical_findings", 
    "List of all critical or notable medical findings with expert opinions and raw parameter values.")

AI_RESPONSE_CRITICAL_FINDING_EXPERTS_OPINION: str = AI_RESPONSE_DESCRIPTION.get(
    "ai_response_critical_finding_experts_opinion", 
    "Expert opinion, diagnosis, explanation of the problem, and its cause. Highlight severity if applicable.")

AI_RESPONSE_CRITICAL_FINDING_PARAM_AND_VALUE: str = AI_RESPONSE_DESCRIPTION.get(
    "ai_response_critical_finding_param_and_value", 
    "The specific medical parameter and its measured value (e.g., 'Glucose 7.8 mmol/L' or 'D=0.004').")
    
# add default if empty
if "ai_response_recommended_therapy_and_advice" not in AI_RESPONSE_DESCRIPTION:
    AI_RESPONSE_DESCRIPTION["ai_response_recommended_therapy_and_advice"] = AI_RESPONSE_RECOMMENDED_THERAPY_AND_ADVICE
if "ai_response_critical_findings" not in AI_RESPONSE_DESCRIPTION:
    AI_RESPONSE_DESCRIPTION["ai_response_critical_findings"] = AI_RESPONSE_CRITICAL_FINDINGS
if "ai_response_critical_finding_experts_opinion" not in AI_RESPONSE_DESCRIPTION:
    AI_RESPONSE_DESCRIPTION["ai_response_critical_finding_experts_opinion"] = AI_RESPONSE_CRITICAL_FINDING_EXPERTS_OPINION
if "ai_response_critical_finding_param_and_value" not in AI_RESPONSE_DESCRIPTION:
    AI_RESPONSE_DESCRIPTION["ai_response_critical_finding_param_and_value"] = AI_RESPONSE_CRITICAL_FINDING_PARAM_AND_VALUE
    
    
#### CLAUDE AI CONFIG
# Model config block for Claude (optional — app may not always use Claude)
CLAUDE_MODEL_CONFIG: dict = json_config.get("claude_initial_model_config", {})
CLAUDE_MODEL_NAME: str = CLAUDE_MODEL_CONFIG.get("name", "claude-3-5-sonnet-20241022")
CLAUDE_SUPPORTED_MODELS: dict[str, str] = json_config.get("claude_supported_models", {})


def save_config():
    """
    Save the current configuration back to config.json
    """
    # global json_config
    AI_RESPONSE_DESCRIPTION["ai_response_recommended_therapy_and_advice"] = AI_RESPONSE_RECOMMENDED_THERAPY_AND_ADVICE
    AI_RESPONSE_DESCRIPTION["ai_response_critical_findings"] = AI_RESPONSE_CRITICAL_FINDINGS
    AI_RESPONSE_DESCRIPTION["ai_response_critical_finding_experts_opinion"] = AI_RESPONSE_CRITICAL_FINDING_EXPERTS_OPINION
    AI_RESPONSE_DESCRIPTION["ai_response_critical_finding_param_and_value"] = AI_RESPONSE_CRITICAL_FINDING_PARAM_AND_VALUE
    
    json_config["ai_response_description"] = AI_RESPONSE_DESCRIPTION
    json_config["ai_initial_model_config"]["name"] = AI_MODEL_NAME
    json_config["ai_initial_model_config"]["temperature"] = AI_MODEL_TEMPERATURE
    json_config["ai_initial_model_config"]["top_p"] = AI_MODEL_TOP_P
    json_config["ai_initial_task_description"] = AI_INITIAL_TASK_DESCRIPTION
    json_config["ai_system_instructions"] = AI_SYSTEM_INSTRUCTIONS

    with open(json_config_path, 'w', encoding='utf-8') as f:
        json.dump(json_config, f, indent=4)