import sys
import os.path
import logging


logger = logging.getLogger()


############################ App base filesistem paths #########################
##
#
def get_base_dir_path() -> str:
    """
    Determines the base directory of the application, handling both script
    execution and frozen executables (like those from PyInstaller).

    - When run as a script, it finds the project root directory (one level
      above the 'src' directory).
    - When run as a frozen executable, it uses the directory of the executable.

    Returns:
        str: The absolute path to the application's root directory.
    """
    # from args
    app_entry_filepath = sys.argv[0]  # sys.executable #resource_path(".") #__file__
    if getattr(sys, 'frozen', False):
        # Running as a PyInstaller bundle or other frozen executable.
        # The base path is the directory containing the executable.
        base_path = os.path.dirname(sys.executable)
        logger.debug(f"Running as frozen executable. Base path: {base_path}")
    elif not app_entry_filepath or not isinstance(app_entry_filepath, str) or not os.path.exists(app_entry_filepath):
        # TODO: CHECK
        # Running as a Console app
        # sys.argv[0] exists
        base_path = app_entry_filepath
        logger.debug(f"Running as console app. Base path: {base_path}")  
    else:
        # Running as a standard Python script.
        # __file__ is '.../src/npy/core/utils.py', so we go up three level to get the project root.
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        logger.debug(f"Running as script. Base path: {base_path}")
    return base_path

def get_resource_dirpath(dir_name: str = "resources") -> str:
    """Constructs and validates the path to a resource directory."""
    base_dirpath = get_base_dir_path()
    resource_dirpath = base_dirpath
    
    if dir_name == "resources":
        resource_dirpath = os.path.join(base_dirpath, dir_name)
    elif dir_name and len(dir_name) > 0:
        resource_dirpath = os.path.join(os.path.join(resource_dirpath, "resources"), dir_name)

    if not os.path.exists(resource_dirpath):
        raise FileNotFoundError(f"FATAL ERROR: Missing resource directory at '{resource_dirpath}'")
    return resource_dirpath

def get_resource_filepath(filename: str) -> str:
    """Constructs and validates the path to a specific resource file."""
    # Corrected: Call the function get_resource_dirpath()
    filepath: str = os.path.join(get_resource_dirpath(), filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"FATAL ERROR: Missing resource file at '{filepath}'.")
    return filepath

def get_input_data_dirpath(dir_name: str = "ULAZ") -> str:
    """
    Constructs and validates the path to the input data directory.
    Note: This is a utility function; dsclinic_cli.py constructs this path from arguments.
    """
    dirpath = os.path.join(get_base_dir_path(), dir_name)
    if not os.path.exists(dirpath):
        raise FileNotFoundError(f"FATAL ERROR: Missing input data directory ('{dir_name}') at: '{dirpath}'")
    return dirpath

def get_output_data_dirpath(dir_name: str = "IZVESTAJI") -> str:
    """
    Constructs the path to the output data directory, creating it if it
    does not exist.
    Note: This is a utility function; dsclinic_cli.py constructs this path from arguments.
    """
    dirpath = os.path.join(get_base_dir_path(), dir_name)
    if not os.path.exists(dirpath):
        # Missing - Create it
        os.makedirs(dirpath, exist_ok=True)
        logger.info(f"Created missing output directory at '{dirpath}'.")
    return dirpath





