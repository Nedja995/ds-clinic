"""
settings_view_model.py – Settings ViewModel
============================================
Holds all observable state for SettingsWindow.
Intentional tk.* exceptions: tk.StringVar / tk.DoubleVar / tk.BooleanVar – always tk.

API keys are read from and written to the OS keyring only (AD-11).
They are never read from app_settings or written via save_unified().

Ollama connection config (base_url, model_name) is NOT a secret — stored
in app_settings and persisted to settings.json via save_unified() (AD-13).
"""
import re
import tkinter as tk
from models import app_settings, get_credential, set_credential


class SettingsViewModel:
    def __init__(self) -> None:
        # ── App ──────────────────────────────────────────────────────────────
        self.var_app_language = tk.StringVar(value=app_settings.language_code)

        # ── Patient Data ──────────────────────────────────────────────────────
        self.var_anonymization_on              = tk.BooleanVar(value=app_settings.anonymization_on)
        self.var_anonymization_custom_texts_on = tk.BooleanVar(value=app_settings.anonymization_custom_texts_on)

        # ── AI / Model ────────────────────────────────────────────────────────
        self.available_models = list(app_settings.ai_supported_models.keys())

        _default_model = app_settings.ai_supported_models.get(app_settings.ai_model_name)
        if not _default_model and self.available_models:
            _default_model = self.available_models[0]
        self.var_model_name  = tk.StringVar(value=_default_model)
        self.var_temperature = tk.DoubleVar(value=app_settings.ai_model_temperature)
        self.var_top_p       = tk.DoubleVar(value=app_settings.ai_model_top_p)

        # ── AI / Analyze Instructions ─────────────────────────────────────────
        self.var_recommended_therapy_prompt = tk.StringVar(value=app_settings.ai_response_recommended_therapy_and_advice)
        self.var_critical_findings_prompt   = tk.StringVar(value=app_settings.ai_response_critical_findings)
        self.var_expert_opinion_label       = tk.StringVar(value=app_settings.ai_response_critical_finding_experts_opinion)
        self.var_parameter_value_label      = tk.StringVar(value=app_settings.ai_response_critical_finding_param_and_value)

        _task_desc = (
            "".join(app_settings.ai_initial_task_description)
            if isinstance(app_settings.ai_initial_task_description, list)
            else app_settings.ai_initial_task_description
        )
        self.var_initial_task_text        = tk.StringVar(value=_task_desc)
        self.var_system_instructions_text = tk.StringVar(value="".join(app_settings.ai_system_instructions))

        # ── API Credentials — read from OS keyring only (AD-11) ───────────────
        self.var_google_api_key      = tk.StringVar(value=get_credential("gemini") or "")
        self.var_anthropic_api_key   = tk.StringVar(value=get_credential("anthropic") or "")
        self.var_google_project_id   = tk.StringVar(value=get_credential("google_project_id") or "")
        # v2.9.1 — OpenAI-compatible cloud providers
        self.var_groq_api_key        = tk.StringVar(value=get_credential("groq") or "")
        self.var_together_api_key    = tk.StringVar(value=get_credential("together") or "")
        self.var_huggingface_api_key = tk.StringVar(value=get_credential("huggingface") or "")

        # v2.10.1 — Ollama local provider (not secrets — read from app_settings)
        self.var_ollama_base_url   = tk.StringVar(value=app_settings.ollama_base_url)
        self.var_ollama_model_name = tk.StringVar(value=app_settings.ollama_model_name)
        self.ollama_supported_models = list(app_settings.ollama_supported_models.keys())

        # ── App General ───────────────────────────────────────────────────────
        self.var_support_email = tk.StringVar(value="nprm1555@gmail.com")
        self.var_app_version   = tk.StringVar(value=app_settings.app_version)
        self.var_email_valid   = tk.BooleanVar(value=True)

    def update_from_config(self) -> None:
        """Refresh all vars from app_settings and OS keyring."""
        self.var_app_language.set(app_settings.language_code)

        self.var_anonymization_on.set(app_settings.anonymization_on)
        self.var_anonymization_custom_texts_on.set(app_settings.anonymization_custom_texts_on)

        _default_model = app_settings.ai_supported_models.get(app_settings.ai_model_name)
        if not _default_model and self.available_models:
            _default_model = self.available_models[0]
        self.var_model_name.set(_default_model)
        self.var_temperature.set(app_settings.ai_model_temperature)
        self.var_top_p.set(app_settings.ai_model_top_p)

        _task_desc = (
            "".join(app_settings.ai_initial_task_description)
            if isinstance(app_settings.ai_initial_task_description, list)
            else app_settings.ai_initial_task_description
        )
        self.var_initial_task_text.set(_task_desc)
        self.var_system_instructions_text.set("".join(app_settings.ai_system_instructions))

        self.var_recommended_therapy_prompt.set(app_settings.ai_response_recommended_therapy_and_advice)
        self.var_critical_findings_prompt.set(app_settings.ai_response_critical_findings)
        self.var_expert_opinion_label.set(app_settings.ai_response_critical_finding_experts_opinion)
        self.var_parameter_value_label.set(app_settings.ai_response_critical_finding_param_and_value)

        # Credentials — always re-read from keyring, never from app_settings
        self.var_google_api_key.set(get_credential("gemini") or "")
        self.var_anthropic_api_key.set(get_credential("anthropic") or "")
        self.var_google_project_id.set(get_credential("google_project_id") or "")
        self.var_groq_api_key.set(get_credential("groq") or "")
        self.var_together_api_key.set(get_credential("together") or "")
        self.var_huggingface_api_key.set(get_credential("huggingface") or "")

        # Ollama — re-read from app_settings (persisted to settings.json, not keyring)
        self.var_ollama_base_url.set(app_settings.ollama_base_url)
        self.var_ollama_model_name.set(app_settings.ollama_model_name)

    def save_to_config(self) -> None:
        """Persist settings to app_settings + disk, and credentials to OS keyring."""
        _lang_val = self.var_app_language.get()
        _lang_mapping = {"English": "en", "Srpski": "sr", "Español": "es"}
        app_settings.language_code = _lang_mapping.get(_lang_val, _lang_val)

        app_settings.anonymization_on = self.var_anonymization_on.get()
        app_settings.anonymization_custom_texts_on = self.var_anonymization_custom_texts_on.get()

        # AI / Model Selection
        _selected_display = self.var_model_name.get()
        _internal_model = app_settings.ai_model_name
        for _key, _display in app_settings.ai_supported_models.items():
            if _display == _selected_display:
                _internal_model = _key
                break
        app_settings.ai_model_name = _internal_model
        app_settings.ai_model_temperature = self.var_temperature.get()
        app_settings.ai_model_top_p = self.var_top_p.get()

        # Custom Prompts & Instructions
        app_settings.ai_initial_task_description = self.var_initial_task_text.get()
        _sys_instrs = self.var_system_instructions_text.get().splitlines(keepends=True)
        app_settings.ai_system_instructions = _sys_instrs if _sys_instrs else []

        app_settings.ai_response_recommended_therapy_and_advice = self.var_recommended_therapy_prompt.get()
        app_settings.ai_response_critical_findings              = self.var_critical_findings_prompt.get()
        app_settings.ai_response_critical_finding_experts_opinion = self.var_expert_opinion_label.get()
        app_settings.ai_response_critical_finding_param_and_value = self.var_parameter_value_label.get()

        # v2.10.1 — Ollama user prefs written to app_settings before save_unified()
        app_settings.ollama_base_url   = self.var_ollama_base_url.get().strip()
        app_settings.ollama_model_name = self.var_ollama_model_name.get()

        # Persist non-secret settings to disk
        app_settings.save_unified()

        # API credentials — written to OS keyring only, never to disk (AD-11)
        set_credential("gemini",            self.var_google_api_key.get())
        set_credential("anthropic",         self.var_anthropic_api_key.get())
        set_credential("google_project_id", self.var_google_project_id.get())
        set_credential("groq",              self.var_groq_api_key.get())
        set_credential("together",          self.var_together_api_key.get())
        set_credential("huggingface",       self.var_huggingface_api_key.get())

    # ── Validation ────────────────────────────────────────────────────────────

    def validate_email(self) -> bool:
        _email = self.var_support_email.get().strip()
        if not _email:
            self.var_email_valid.set(True)
            return True
        _pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        _valid = bool(re.match(_pattern, _email))
        self.var_email_valid.set(_valid)
        return _valid

    # ── Commands ──────────────────────────────────────────────────────────────

    def on_send_logs(self) -> None:
        pass  # TODO: implement log shipping

    def on_show_logs_folder(self) -> None:
        pass  # TODO: open logs dir in OS file explorer
