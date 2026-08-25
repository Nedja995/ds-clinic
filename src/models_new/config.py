"""Application configuration via pydantic-settings."""

from npy.core.settings_manager import load_saved_settings
from npy.core.utils import get_input_data_dirpath
from pydantic import Field
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
  """Root application settings.

  Values are loaded from environment variables prefixed with MedAI_
  (e.g. MedAI_GEMINI_MODEL) or from a .env file.
  """

  model_config = {"env_prefix": "MedAI_", "extra": "ignore"}  # <--- Added extra="ignore"

  # AI backend
  gemini_model: str = "gemini-2.5-flash"

  # Advisor mode
  cooldown_seconds: float = Field(default=15.0, ge=5.0, le=120.0)
  ocr_confidence_threshold: float = Field(default=0.6, ge=0.0, le=1.0)

  # Retry / backoff
  api_max_retries: int = Field(default=3, ge=1, le=10)
  api_backoff_seconds: float = Field(default=2.0, ge=0.5, le=30.0)
  api_cooldown_seconds: float = Field(default=30.0, ge=5.0, le=300.0)

  # Theme
  theme_name: str = "dark"

  # Debug
  debug_log_max_lines: int = Field(default=200, ge=50, le=1000)

  # Use default_factory so it computes the dynamic path correctly
  input_dir: str = Field(
      description="Directory for input files.",
      default_factory=get_input_data_dirpath,
  )


# 1. Load saved overrides from JSON (managed by settings_manager)
_saved = load_saved_settings()
_clean_saved = {k: v for k, v in _saved.items() if not k.startswith("_")}

# 2. Create the single global instance combining Env Vars, Defaults, and Saved JSON
app_settings = AppSettings(**_clean_saved)