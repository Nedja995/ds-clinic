"""
settings_view_model.py – Settings ViewModel
============================================
Holds all observable state for SettingsWindow.
Intentional tk.* exceptions: tk.StringVar / tk.DoubleVar / tk.BooleanVar – always tk.
"""
import re
import tkinter as tk
from models import app_settings

class SettingsViewModel:
    def __init__(self) -> None:
        # __ APP _____________________________________________________________________
        self.var_app_language = tk.StringVar(value=app_settings.language_code)
        # __ PATIENT DATA ____________________________________________________________
        self.var_anonymization_on              = tk.BooleanVar(value=app_settings.anonymization_on)
        self.var_anonymization_custom_texts_on = tk.BooleanVar(value=app_settings.anonymization_custom_texts_on)
        
        # ── AI / Model ────────────────────────────────────────────────────────
        self.available_models               = list(app_settings.ai_supported_models.keys())
        
        # Find default model display name
        default_model = app_settings.ai_supported_models.get(app_settings.ai_model_name)
        if not default_model and self.available_models:
            default_model = self.available_models[0]
        self.var_model_name                 = tk.StringVar(value=default_model)
        
        self.var_temperature                = tk.DoubleVar(value=app_settings.ai_model_temperature)
        self.var_top_p                      = tk.DoubleVar(value=app_settings.ai_model_top_p)

        # ── AI / Analyze Instructions ─────────────────────────────────────────
        self.var_recommended_therapy_prompt = tk.StringVar(value=app_settings.ai_response_recommended_therapy_and_advice)
        self.var_critical_findings_prompt   = tk.StringVar(value=app_settings.ai_response_critical_findings)
        self.var_expert_opinion_label       = tk.StringVar(value=app_settings.ai_response_critical_finding_experts_opinion)
        self.var_parameter_value_label      = tk.StringVar(value=app_settings.ai_response_critical_finding_param_and_value)
        
        task_desc = "".join(app_settings.ai_initial_task_description) if isinstance(app_settings.ai_initial_task_description, list) else app_settings.ai_initial_task_description
        self.var_initial_task_text          = tk.StringVar(value=task_desc)
        self.var_system_instructions_text   = tk.StringVar(value="".join(app_settings.ai_system_instructions))
        self.var_google_api_key             = tk.StringVar(value=app_settings.google_api_key)

        # ── App General ───────────────────────────────────────────────────────────
        self.var_support_email              = tk.StringVar(value="nprm1555@gmail.com")
        self.var_app_version                = tk.StringVar(value=app_settings.app_version)
        self.var_email_valid                = tk.BooleanVar(value=True)

    def update_from_config(self) -> None:
        # Update all fields from config (useful if config can be changed at runtime)
        self.var_app_language.set(app_settings.language_code)
        # Patient Data
        self.var_anonymization_on.set(app_settings.anonymization_on)
        self.var_anonymization_custom_texts_on.set(app_settings.anonymization_custom_texts_on)
        #
        default_model = app_settings.ai_supported_models.get(app_settings.ai_model_name)
        if not default_model and self.available_models:
            default_model = self.available_models[0]
        self.var_model_name.set(default_model)
        
        self.var_temperature.set(app_settings.ai_model_temperature)
        self.var_top_p.set(app_settings.ai_model_top_p)
        #
        task_desc = "".join(app_settings.ai_initial_task_description) if isinstance(app_settings.ai_initial_task_description, list) else app_settings.ai_initial_task_description
        self.var_initial_task_text.set(task_desc)
        self.var_system_instructions_text.set("".join(app_settings.ai_system_instructions))
        #
        self.var_recommended_therapy_prompt.set(app_settings.ai_response_recommended_therapy_and_advice)
        self.var_critical_findings_prompt.set(app_settings.ai_response_critical_findings)
        self.var_expert_opinion_label.set(app_settings.ai_response_critical_finding_experts_opinion)
        self.var_parameter_value_label.set(app_settings.ai_response_critical_finding_param_and_value)
        #
        self.var_google_api_key.set(app_settings.google_api_key)
        
    def save_to_config(self) -> None:
        # Save current settings back to AppSettings
        lang_val = self.var_app_language.get()
        lang_mapping = {"English": "en", "Srpski": "sr", "Español": "es"}
        app_settings.language_code = lang_mapping.get(lang_val, lang_val)
        
        # Patient Data
        app_settings.anonymization_on = self.var_anonymization_on.get()
        app_settings.anonymization_custom_texts_on = self.var_anonymization_custom_texts_on.get()
        
        # AI / Model Selection
        selected_model_display = self.var_model_name.get()
        # Find internal model key from display name
        internal_model_name = app_settings.ai_model_name
        for model_key, model_display in app_settings.ai_supported_models.items():
            if model_display == selected_model_display:
                internal_model_name = model_key
                break
        app_settings.ai_model_name = internal_model_name
        
        app_settings.ai_model_temperature = self.var_temperature.get()
        app_settings.ai_model_top_p = self.var_top_p.get()
        
        # Custom Prompts & Instructions
        app_settings.ai_initial_task_description = self.var_initial_task_text.get()
        
        # Split system instructions by lines while keeping format
        sys_instrs = self.var_system_instructions_text.get().splitlines(keepends=True)
        app_settings.ai_system_instructions = sys_instrs if sys_instrs else []
        
        # Response prompt templates
        app_settings.ai_response_recommended_therapy_and_advice = self.var_recommended_therapy_prompt.get()
        app_settings.ai_response_critical_findings = self.var_critical_findings_prompt.get()
        app_settings.ai_response_critical_finding_experts_opinion = self.var_expert_opinion_label.get()
        app_settings.ai_response_critical_finding_param_and_value = self.var_parameter_value_label.get()
        
        # API Keys
        app_settings.google_api_key = self.var_google_api_key.get()
        
        # Save to file atomically
        app_settings.save_unified()
        
        
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
