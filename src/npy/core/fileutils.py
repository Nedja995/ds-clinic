
import os
import json
import datetime

from npy.core.logger import setup_logger
from npy.core.utils import get_resource_filepath, get_output_data_dirpath
import config

logger = setup_logger()


def open_file_from_filepath(filepath: str):
    if os.name == 'nt':
        os.startfile(filepath)
    elif os.name == 'posix':
        os.system(f'open "{filepath}"')

def read_debug_sample_response_json(name: str = "sample_response", input_filepath: str | None = None) -> dict | None:
    if not input_filepath:
        input_filepath = get_resource_filepath(f"{name}.json")
        
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
        output_dir = get_output_data_dirpath()
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
    supported_exts = tuple(f".{ext.lstrip('.')}" for ext, filetype in config.AI_SUPPORTED_INPUT_FILETYPES.items())
    # Filter files by supported extensions
    filepaths = [f for f in filepaths if f.lower().endswith(supported_exts)]
    # Input documents filepaths with full path
    documents_filepaths = [os.path.join(input_dir, f) for f in filepaths]
    return documents_filepaths

def make_output_filepath(patient_name: str, extension: str, output_dir: str | None) -> str:
    if not output_dir: output_dir = get_output_data_dirpath()
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    output_path = os.path.join(output_dir, f"NALAZ_{patient_name}_{timestamp_str}.{extension}")
    return output_path