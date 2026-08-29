import json
import logging
import platform
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from npy.core.utils import get_base_dir_path, get_input_data_dirpath

logger = logging.getLogger(__name__)

_APP_NAME = "medai_vitec"


class AppSettings(BaseSettings):
    """Unified, Pydantic-based Hybrid Application Settings and I/O Loader."""

    model_config = {"env_prefix": "MedAI_", "extra": "ignore"}

    # ── 1. STATIC SYSTEM DEFAULTS (bundled read-only config.json) ──
    app_name: str = "DSClinic"
    app_version: str = "2.1.10"
    app_log_level: str = "INFO"
    app_debug_export_response: bool = True
    app_debug_response: bool = False
    
    ai_supported_models: Dict[str, str] = Field(default_factory=dict)
    ai_supported_input_filetypes: Dict[str, str] = Field(default_factory=dict)
    
    ai_response_description: Dict[str, str] = Field(default_factory=dict)
    ai_initial_task_key: str = "TASK_1"
    ai_task_descriptions: Dict[str, Dict[str, Any]] = Field(default_factory=dict)

    claude_supported_models: Dict[str, str] = Field(default_factory=dict)

    # ── 2. WRITABLE CLINICIAN PREFERENCES (settings.json overrides) ──
    language_code: str = "sr"
    anonymization_on: bool = False
    anonymization_custom_texts_on: bool = False

    # Advisor mode parameters
    cooldown_seconds: float = Field(default=15.0, ge=5.0, le=120.0)
    ocr_confidence_threshold: float = Field(default=0.6, ge=0.0, le=1.0)

    # Retry / backoff
    api_max_retries: int = Field(default=3, ge=1, le=10)
    api_backoff_seconds: float = Field(default=2.0, ge=0.5, le=30.0)
    api_cooldown_seconds: float = Field(default=30.0, ge=5.0, le=300.0)

    theme_name: str = "dark"
    debug_log_max_lines: int = Field(default=200, ge=50, le=1000)

    # API Keys
    google_api_key: str = ""
    anthropic_api_key: str = ""

    # Models & System Prompts
    ai_model_name: str = "gemini-2.5-flash"
    ai_model_temperature: float = 1.0
    ai_model_top_p: float = 0.95
    ai_model_max_output_tokens: int = 65535
    ai_model_top_k: int = 64
    ai_thinking_level: str = "default"

    claude_model_name: str = "claude-3-5-sonnet-20241022"

    ai_initial_task_description: str = ""
    ai_system_instructions: List[str] = Field(default_factory=list)

    # Clinician prompt templates
    ai_response_recommended_therapy_and_advice: str = ""
    ai_response_critical_findings: str = ""
    ai_response_critical_finding_experts_opinion: str = ""
    ai_response_critical_finding_param_and_value: str = ""

    # Dynamic directories
    input_dir: str = Field(
        description="Directory for input files.",
        default_factory=get_input_data_dirpath,
    )

    # ── 3. HYBRID LOADER (Layering Base Defaults -> Presets -> Profile Overrides) ──
    @classmethod
    def load_unified(cls, profile_id: str = "default", preset_name: Optional[str] = None) -> "AppSettings":
        """
        Loads base config.json defaults, overlays requested presets, and merges user profile overrides.
        """
        base_dir = Path(get_base_dir_path())
        merged_data: Dict[str, Any] = {}

        # A0. Read settings.ini (for keys, version, and app name baseline)
        import configparser
        ini_config = configparser.ConfigParser()
        ini_path = base_dir / "settings.ini"
        if ini_path.exists():
            try:
                ini_config.read(ini_path, encoding="utf-8")
                merged_data["app_name"] = ini_config.get("APP", "NAME", fallback="DSClinic").replace('"', '').replace("'", "")
                merged_data["app_version"] = ini_config.get("APP", "VERSION", fallback="2.1.10").replace('"', '').replace("'", "")
                
                # Fetch API Keys from INI as base
                google_key = ini_config.get("GOOGLE", "GOOGLE_API_KEY", fallback="").replace('"', '').replace("'", "")
                anthropic_key = ini_config.get("ANTHROPIC", "ANTHROPIC_API_KEY", fallback="").replace('"', '').replace("'", "")
                if google_key:
                    merged_data["google_api_key"] = google_key
                if anthropic_key:
                    merged_data["anthropic_api_key"] = anthropic_key
            except Exception as e:
                logger.warning(f"Error reading settings.ini fallback parameters: {e}")

        # A. Read static config.json defaults
        config_path = base_dir / "config.json"
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config_defaults = json.load(f)
                    
                    # Map flat or nested config.json fields to match AppSettings lowercase property names
                    merged_data["app_log_level"] = config_defaults.get("app", {}).get("log_level", "INFO")
                    merged_data["app_debug_export_response"] = config_defaults.get("app", {}).get("debug_export_response", True)
                    merged_data["app_debug_response"] = config_defaults.get("app", {}).get("debug_response", False)
                    
                    merged_data["ai_supported_models"] = config_defaults.get("ai_supported_models", {})
                    merged_data["ai_supported_input_filetypes"] = config_defaults.get("ai_supported_input_filetypes", {})
                    
                    merged_data["ai_response_description"] = config_defaults.get("ai_response_description", {})
                    merged_data["ai_initial_task_key"] = config_defaults.get("ai_initial_task_key", "TASK_1")
                    merged_data["ai_task_descriptions"] = config_defaults.get("ai_task_descriptions", {})

                    # Extract default Gemini settings
                    gemini_cfg = config_defaults.get("ai_initial_model_config", {})
                    merged_data["ai_model_name"] = gemini_cfg.get("name", "gemini-2.5-flash")
                    merged_data["ai_model_temperature"] = gemini_cfg.get("temperature", 1.0)
                    merged_data["ai_model_top_p"] = gemini_cfg.get("top_p", 0.95)
                    merged_data["ai_model_max_output_tokens"] = gemini_cfg.get("max_output_tokens", 65535)
                    merged_data["ai_model_top_k"] = gemini_cfg.get("top_k", 64)
                    merged_data["ai_thinking_level"] = gemini_cfg.get("thinking_level", "default")

                    # Extract system prompts and instructions
                    raw_task_desc = config_defaults.get("ai_initial_task_description", [])
                    merged_data["ai_initial_task_description"] = "".join(raw_task_desc) if isinstance(raw_task_desc, list) else raw_task_desc
                    merged_data["ai_system_instructions"] = config_defaults.get("ai_system_instructions", [])

                    # Extract default response templates
                    resp_desc = config_defaults.get("ai_response_description", {})
                    merged_data["ai_response_recommended_therapy_and_advice"] = resp_desc.get("ai_response_recommended_therapy_and_advice", "")
                    merged_data["ai_response_critical_findings"] = resp_desc.get("ai_response_critical_findings", "")
                    merged_data["ai_response_critical_finding_experts_opinion"] = resp_desc.get("ai_response_critical_finding_experts_opinion", "")
                    merged_data["ai_response_critical_finding_param_and_value"] = resp_desc.get("ai_response_critical_finding_param_and_value", "")

                    # Extract Claude settings
                    claude_cfg = config_defaults.get("claude_initial_model_config", {})
                    merged_data["claude_model_name"] = claude_cfg.get("name", "claude-3-5-sonnet-20241022")
                    merged_data["claude_supported_models"] = config_defaults.get("claude_supported_models", {})
            except Exception as e:
                logger.error(f"Failed to read static config.json defaults: {e}")

        # B. Optionally layer predefined canned presets (e.g., config/presets/holistic.json)
        if preset_name:
            preset_path = base_dir / "config" / "presets" / f"{preset_name}.json"
            if preset_path.exists():
                try:
                    with open(preset_path, "r", encoding="utf-8") as f:
                        preset_overrides = json.load(f)
                        merged_data.update(preset_overrides)
                except Exception as e:
                    logger.warning(f"Failed to load canned preset '{preset_name}': {e}")

        # C. Layer active clinician settings override (settings_profile_id.json)
        config_dir = base_dir / ".config" / _APP_NAME
        profile_path = config_dir / (f"settings_{profile_id}.json" if profile_id != "default" else "settings.json")
        if profile_path.exists():
            try:
                with open(profile_path, "r", encoding="utf-8") as f:
                    profile_overrides = json.load(f)
                    
                    # Clean out keys starting with '_' (like geometry metrics)
                    clean_overrides = {k: v for k, v in profile_overrides.items() if not k.startswith("_")}
                    merged_data.update(clean_overrides)
            except Exception as e:
                logger.warning(f"Failed to load clinician profile settings from {profile_path}: {e}")

        return cls(**merged_data)

    # ── 4. HYBRID SAVER (Atomic Writable Swapping) ──
    def save_unified(self, profile_id: str = "default") -> None:
        """
        Saves current writable preferences back to the local profile's settings JSON atomically.
        """
        base_dir = Path(get_base_dir_path())
        config_dir = base_dir / ".config" / _APP_NAME
        config_dir.mkdir(parents=True, exist_ok=True)
        
        profile_path = config_dir / (f"settings_{profile_id}.json" if profile_id != "default" else "settings.json")

        # Exclude read-only system structures to keep the user profile light and upgrade-resilient
        exclude_fields = {
            "ai_supported_models",
            "ai_supported_input_filetypes",
            "ai_response_description",
            "ai_initial_task_key",
            "ai_task_descriptions",
            "claude_supported_models"
        }
        
        # Serialize only fields that are customizable by the user
        save_data = self.model_dump(exclude=exclude_fields)

        # Merge existing metadata (like geometry / private prompt history starting with '_') so we don't erase them
        if profile_path.exists():
            try:
                with open(profile_path, "r", encoding="utf-8") as f:
                    old_data = json.load(f)
                    metadata_keys = {k: v for k, v in old_data.items() if k.startswith("_")}
                    save_data.update(metadata_keys)
            except Exception:
                pass

        # Write atomically using a temporary file and renaming swap (atomic on all platforms)
        tmp_path = profile_path.with_suffix(".tmp")
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(save_data, f, indent=2)
            tmp_path.replace(profile_path)
            logger.info(f"Successfully saved user settings atomically to {profile_path}")
        except OSError as exc:
            logger.error(f"Failed to save settings atomically to {profile_path}: {exc}")
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass
            raise


# ── Single Global Instance Initialized on Import ──
app_settings = AppSettings.load_unified()


def reload_app_settings(profile_id: str = "default", preset_name: Optional[str] = None) -> None:
    """
    Reloads the global app_settings instance from defaults and the selected profile.
    """
    global app_settings
    app_settings = AppSettings.load_unified(profile_id=profile_id, preset_name=preset_name)
    logger.info(f"Dynamically reloaded AppSettings for profile '{profile_id}'")
