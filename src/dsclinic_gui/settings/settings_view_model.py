"""
settings_view_model.py – Settings ViewModel
============================================
Holds all observable state for SettingsWindow.
Intentional tk.* exceptions: tk.StringVar / tk.DoubleVar / tk.BooleanVar – always tk.
"""
import re
import tkinter as tk
import config

class SettingsViewModel:
    def __init__(self) -> None:
        # ── AI / Model ────────────────────────────────────────────────────────
        self.available_models               = list(config.AI_SUPPORTED_MODELS.keys())
        self.var_model_name                 = tk.StringVar(value=config.AI_SUPPORTED_MODELS.get(config.AI_MODEL_NAME, list(config.AI_SUPPORTED_MODELS.keys())[0]))
        self.var_temperature                = tk.DoubleVar(value=config.AI_MODEL_TEMPERATURE)
        self.var_top_p                      = tk.DoubleVar(value=config.AI_MODEL_TOP_P)

        # ── AI / Analyze Instructions ─────────────────────────────────────────
        self.var_recommended_therapy_prompt = tk.StringVar(value=config.AI_RESPONSE_RECOMMENDED_THERAPY_AND_ADVICE)
        self.var_critical_findings_prompt   = tk.StringVar(value=config.AI_RESPONSE_CRITICAL_FINDINGS)
        self.var_expert_opinion_label       = tk.StringVar(value=config.AI_RESPONSE_CRITICAL_FINDING_EXPERTS_OPINION)
        self.var_parameter_value_label      = tk.StringVar(value=config.AI_RESPONSE_CRITICAL_FINDING_PARAM_AND_VALUE)
        self.var_initial_task_text          = tk.StringVar(value="".join(config.AI_INITIAL_TASK_DESCRIPTION))
        self.var_system_instructions_text   = tk.StringVar(value="".join(config.AI_SYSTEM_INSTRUCTIONS))
        self.var_google_api_key             = tk.StringVar(value=config.GOOGLE_API_KEY)

        # ── App General ───────────────────────────────────────────────────────────
        self.var_support_email              = tk.StringVar(value="nprm1555@gmail.com")
        self.var_app_version                = tk.StringVar(value=config.APP_VERSION)
        self.var_email_valid                = tk.BooleanVar(value=True)

    def update_from_config(self) -> None:
        # Update all fields from config (useful if config can be changed at runtime)
        #
        self.var_model_name.set(config.AI_SUPPORTED_MODELS.get(config.AI_MODEL_NAME, list(config.AI_SUPPORTED_MODELS.keys())[0]))
        self.var_temperature.set(config.AI_MODEL_TEMPERATURE)
        self.var_top_p.set(config.AI_MODEL_TOP_P)
        #
        self.var_initial_task_text.set("".join(config.AI_INITIAL_TASK_DESCRIPTION))
        self.var_system_instructions_text.set("".join(config.AI_SYSTEM_INSTRUCTIONS))
        #
        self.var_recommended_therapy_prompt.set(config.AI_RESPONSE_RECOMMENDED_THERAPY_AND_ADVICE)
        self.var_critical_findings_prompt.set(config.AI_RESPONSE_CRITICAL_FINDINGS)
        self.var_expert_opinion_label.set(config.AI_RESPONSE_CRITICAL_FINDING_EXPERTS_OPINION)
        self.var_parameter_value_label.set(config.AI_RESPONSE_CRITICAL_FINDING_PARAM_AND_VALUE)
        #
        self.var_google_api_key.set(config.GOOGLE_API_KEY)
        
    def save_to_config(self) -> None:
        # Save current settings back to config (useful if you want to persist changes)
        #
        config.AI_MODEL_NAME = self.var_model_name.get()
        config.AI_MODEL_TEMPERATURE = self.var_temperature.get()
        config.AI_MODEL_TOP_P = self.var_top_p.get()
        #
        config.AI_TASK_DESCRIPTION = self.var_initial_task_text.get().splitlines(keepends=True)
        config.AI_SYSTEM_INSTRUCTIONS = self.var_system_instructions_text.get().splitlines(keepends=True)
        #
        config.AI_RESPONSE_RECOMMENDED_THERAPY_AND_ADVICE = self.var_recommended_therapy_prompt.get()
        config.AI_RESPONSE_CRITICAL_FINDINGS = self.var_critical_findings_prompt.get()
        config.AI_RESPONSE_CRITICAL_FINDING_EXPERTS_OPINION = self.var_expert_opinion_label.get()
        config.AI_RESPONSE_CRITICAL_FINDING_PARAM_AND_VALUE = self.var_parameter_value_label.get()
        #
        config.GOOGLE_API_KEY = self.var_google_api_key.get()
        
        #
        config.save_config()
        
        
    # ── Validation ────────────────────────────────────────────────────────────

    def validate_email(self) -> bool:
        email = self.var_support_email.get().strip()
        if not email:
            self.var_email_valid.set(True)
            return True
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        valid = bool(re.match(pattern, email))
        self.var_email_valid.set(valid)
        return valid

    # ── Commands ──────────────────────────────────────────────────────────────

    def on_send_logs(self) -> None:
        pass  # TODO: implement log shipping

    def on_show_logs_folder(self) -> None:
        pass  # TODO: open logs dir in OS file explorer
