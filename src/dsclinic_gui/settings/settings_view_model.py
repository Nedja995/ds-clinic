"""
settings_view_model.py – Settings ViewModel
============================================
Holds all observable state for SettingsWindow.
Intentional tk.* exceptions: tk.StringVar / tk.DoubleVar / tk.BooleanVar – always tk.
"""
import re
import tkinter as tk


AVAILABLE_MODELS: list[str] = [
    "gemini-2.5-pro",
    "gemini-3-pro-preview",
    "gemini-3-flash-preview",
]

_APP_VERSION = "1.0.0"


class SettingsViewModel:

    def __init__(self, root: tk.Misc) -> None:
        # ── AI / Model ────────────────────────────────────────────────────────
        self.available_models               = AVAILABLE_MODELS
        self.var_model_name                 = tk.StringVar(root, value=AVAILABLE_MODELS[0])
        self.var_temperature                = tk.DoubleVar(root, value=1.0)
        self.var_top_p                      = tk.DoubleVar(root, value=0.95)

        # ── AI / Analyze Instructions ─────────────────────────────────────────
        self.var_recommended_therapy_prompt = tk.StringVar(root, value="")
        self.var_critical_findings_prompt   = tk.StringVar(root, value="")
        self.var_expert_opinion_label       = tk.StringVar(root, value="")
        self.var_parameter_value_label      = tk.StringVar(root, value="")
        self.var_initial_task_text          = tk.StringVar(root, value="")
        self.var_system_instructions_text   = tk.StringVar(root, value="")
        self.var_google_api_key             = tk.StringVar(root, value="")

        # ── General ───────────────────────────────────────────────────────────
        self.var_support_email              = tk.StringVar(root, value="")
        self.var_app_version                = tk.StringVar(root, value=_APP_VERSION)
        self.var_email_valid                = tk.BooleanVar(root, value=True)

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
