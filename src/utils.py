##
#
import sys
import os.path
import logging

logger = logging.getLogger(__name__)


##### App base filesistem paths ##### 
#

def get_base_dir_path() -> str:
    # from args
    app_entry_filepath = sys.argv[0]  # sys.executable #resource_path(".") #__file__
    if not app_entry_filepath or not isinstance(app_entry_filepath, str) or not os.path.exists(app_entry_filepath):
        print(f"|DSClinic||WARNING| get_base_dir_path() - Wrong sys.argv[0] = {sys.argv[0]}.")
    
    # 
    app_entry_filepath = sys.executable
    if not app_entry_filepath or not isinstance(app_entry_filepath, str) or not os.path.exists(app_entry_filepath):
        print(f"|DSClinic||WARNING| get_base_dir_path() - Wrong sys.executable = {sys.executable}.")
    
    # 
    app_entry_filepath = __file__  
    if not app_entry_filepath or not isinstance(app_entry_filepath, str) or not os.path.exists(app_entry_filepath):
        print(f"|DSClinic||WARNING| get_base_dir_path() - Wrong __file__ = {__file__}.")
    
    #
    app_entry_dirpath = os.path.dirname(os.path.abspath(app_entry_filepath))
    
    return app_entry_dirpath

def get_resource_dirpath(dir_name: str = "resources") -> str:
    base_dirpath = get_base_dir_path()
    
    resource_dirpath = os.path.join(base_dirpath, dir_name)
    if not os.path.exists(resource_dirpath):
        ## FATAL ERROR - Missing app resources
        raise Exception(f"FATAL ERROR - MISSING APP RESOURCE DIR AT: '{resource_dirpath}'")
      
    return resource_dirpath

def get_resource_filepath(filename: str) -> str:
    filepath: str = os.path.join(get_resource_dirpath, filename)
    
    if not os.path.exists(filepath):
        ## FATAL ERROR - Missing app resources
        raise FileNotFoundError(f"FATAL ERROR - MISSING APP RESOURCE FILE AT: '{filepath}'.")
    
    return filepath

def get_input_data_dirpath(dir_name: str = "ULAZ") -> str:
    dirpath: str = None
    
    dirpath = os.path.join(get_base_dir_path(), dir_name)
    if not os.path.exists(dirpath):
        ## FATAL ERROR - Missing
        raise Exception(f"FATAL ERROR - MISSING APP INPUT DATA DIR ('ULAZ') AT: '{dirpath}'")
    
    return dirpath

def get_output_data_dirpath(dir_name: str = "IZVESTAJI") -> str:
    dirpath: str = None
    
    dirpath = os.path.join(get_base_dir_path(), dir_name)
    if not os.path.exists(dirpath):
        # Missing - Create it
        os.makedirs(dirpath, exist_ok=True)
        logger.info(f"Created missing output directory at '{dirpath}'.")
    
    return dirpath