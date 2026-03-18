import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Any
from npy.core.utils import get_base_dir_path


class DirectoryFilter(logging.Filter):
    def filter(self, record):
        # Extract the directory name from the full pathname of the file
        record.dirname = os.path.basename(os.path.dirname(record.pathname))
        if "src" not in record.dirname:
            record.dirname = f"{record.dirname}."
        else:
            record.dirname = ""

        return True


# --- Global Configuration ---

# Silence noisy third-party loggers that can clutter the output.
# 'fontTools' is particularly verbose during PDF generation.
logging.getLogger('fontTools').setLevel(logging.WARNING)


# --- Custom Log Level: VERBOSE ---
# This defines a custom log level named 'VERBOSE' which is numerically
# set between DEBUG (10) and NOTSET (0). This allows for logging that is
# more detailed than INFO but less noisy than DEBUG, useful for tracking
# general program flow without deep technical details.

VERBOSE_LEVEL_NUM = 15
# logging.addLevelName(VERBOSE_LEVEL_NUM, "VERBOSE")

def verbose(self: logging.Logger, message: str, *args: Any, **kws: Any) -> None:
    """Logs a message with level VERBOSE."""
    if self.isEnabledFor(VERBOSE_LEVEL_NUM):
        # The `_log` method is the internal machinery for logging.
        self._log(VERBOSE_LEVEL_NUM, message, args, **kws)

# Bind the custom 'verbose' method to the base Logger class so it can be
# called directly on any logger instance (e.g., logger.verbose("..."))
# logging.Logger.verbose = verbose  # type: ignore

# For consistency, create a 'fatal' alias for 'critical'.
# This doesn't add new functionality but can improve readability if 'fatal'
# is a more intuitive term for the developer.
logging.Logger.fatal = logging.Logger.critical


def setup_logger(name: str = "dsclinic", log_dir_name: str = "logs", level: int = None) -> logging.Logger:
    """
    Configures and returns a logger with console and rotating file handlers.

    This function is idempotent: if a logger with the given name has already
    been configured, it will return the existing instance without re-configuring.

    The logger is configured with two handlers:
    1. Console Handler: Logs INFO level and above to the standard output.
    2. Rotating File Handler: Logs VERBOSE level and above to a file in the
       specified log directory. The log file rotates when it reaches ~1MB,
       and up to 7 backup files are kept.

    Args:
        name (str): The name of the logger. Defaults to "dsclinic".
        log_dir_name (str): The name of the directory to store log files.
                            Defaults to "logs".

    Returns:
        logging.Logger: The configured logger instance.
    """
    logger = logging.getLogger(name)
    
    # If the logger is already configured, don't add more handlers
    if logger.hasHandlers():
        return logger

    # Set the logger's base level to the lowest custom level.
    # This ensures that messages of any severity are captured and can be
    # filtered by the individual handlers.
    if level is not None:
        logger.setLevel(level)
    else:
        logger.setLevel(level=logging.INFO)
        pass
    
    # --- Define Logging Formats ---
    # File format includes more context (file name, line number) for easier debugging.
    file_formatter = logging.Formatter(
        # asctime: Timestamp | levelname: Log level | filename:lineno: Source | message: The log message
        "%(asctime)s | %(levelname)-5s | %(dirname)s%(filename)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    # Console format is cleaner for general user feedback.
    console_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-5s | %(message)s", 
        datefmt="%H:%M:%S"
    )

    # --- 1. Console Handler ---
    # This handler prints logs to the terminal.
    console_handler = logging.StreamHandler()
    # Only show INFO and higher messages in the console to avoid spam.
    if level is not None:
        console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # --- 2. Rotating File Handler ---
    # This handler writes logs to a file, with automatic rotation to prevent
    # the log file from growing indefinitely.
    try:
        root_dir = get_base_dir_path()
        log_dir = os.path.join(root_dir, log_dir_name)
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"{name}.log")

        # Configure rotation: 1MB per file, keeping the last 7 files.
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=1 * 1024 * 1024,  # 1 MB
            backupCount=7,
            encoding="utf-8"
        )
        # The file handler should log everything from VERBOSE upwards.
        if level is not None:
            file_handler.setLevel(level)
        file_handler.setFormatter(file_formatter)
        file_handler.addFilter(DirectoryFilter())
        logger.addHandler(file_handler)
    except Exception as e:
        # If file logging fails, log an error to the console and continue.
        logger.error(f"Failed to set up file logging: {e}")

    return logger