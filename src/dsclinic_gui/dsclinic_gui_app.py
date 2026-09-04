import multiprocessing
import tkinter as tk
from npy.core.logger import setup_logger
import logging
from npy.core import utils
from models import app_settings, MedicalReport
from models.brand import brand_config
from dsclinic_gui.report_view_models import DSClinicViewModel
from dsclinic_gui.main_container import MainContainerView
from dsclinic_gui.styles import build_styles
from dsclinic_gui.constants import MIN_WIDTH, MIN_HEIGHT, INIT_WIDTH, INIT_HEIGHT
from datetime import datetime
from npy.core.localization import TranslationManager

logger = setup_logger()

class DSClinicAppGUI(tk.Tk):
    """
    Main application window for DSClinic GUI.
    Window title is sourced from brand_config.clinic_name (AD-20) so that
    white-label builds show the clinic's own product name in the OS taskbar
    without any code changes.
    """
    def __init__(self, initial_data: MedicalReport | dict):
        super().__init__()

        locale_dir = utils.get_resource_dirpath('locale')

        initial_lang = self.load_config_language()

        self.translator = TranslationManager(
            locale_dir=locale_dir,
            default_lang=initial_lang,
        )

        self.languages = {"English": "en", "Srpski": "sr", "Español": "es"}

        self.lang_var = tk.StringVar()
        self.translator.register_ui(self.refresh_text)
        self.refresh_text()

        self._configure_app()
        build_styles()

        medical_report: MedicalReport = initial_data if not initial_data else MedicalReport.model_validate(initial_data)

        self.view_model = DSClinicViewModel(
            schedule_poll_fn=self.after,
            model=medical_report
        )

        self.main_container = MainContainerView(self, self.view_model)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        self._center_window(INIT_WIDTH, INIT_HEIGHT)

    def _configure_app(self):
        # Window title from brand_config — white-label builds show their clinic
        # name in the OS taskbar; generic SaaS builds show "MedAI - ViTec".
        self.title(brand_config.clinic_name)
        self.minsize(MIN_WIDTH, MIN_HEIGHT)
        self.geometry(f"{INIT_WIDTH}x{INIT_HEIGHT}")
        self.resizable(width=True, height=True)

    def _center_window(self, w: int, h: int):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def refresh_text(self):
        """Updates text elements sitting on the dashboard workspace."""
        current_code = self.translator.current_lang
        for display_name, code in self.languages.items():
            if code == current_code:
                self.lang_var.set(display_name)
                break

    def load_config_language(self):
        """Loads language preference from settings."""
        return app_settings.language_code


if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    logger.info(f" DSClinicGUI v{app_settings.app_version} run with parameters:\n")
    base_dir = utils.get_base_dir_path()
    logger.info(f"{' ' * 3}- Root directory: {base_dir}.")
    logger.info("="*60)

    current_date = datetime.now()
    formatted_date = current_date.strftime("%d.%m.%Y")

    test_podaci = {
        "report_id": "1",
        "report_date": formatted_date,
        "content": {
            "patient_name": "Nepoznato",
            "recommended_therapy_and_advice": "",
            "critical_findings": []
        }
    }

    # Mandatory to prevent recursive Tkinter windows spawning in frozen builds
    multiprocessing.freeze_support()

    app = DSClinicAppGUI(initial_data=test_podaci)
    app.mainloop()
