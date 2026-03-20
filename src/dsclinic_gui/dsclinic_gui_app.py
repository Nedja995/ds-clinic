import tkinter as tk
from dsclinic_gui.report_controller import DSClinicController
from dsclinic_gui.report_view import DSClinicView
from dsclinic_gui.report_view_models import DSClinicViewModel
from npy.core.logger import setup_logger
import logging
import config
from npy.core import utils
from models import MedicalReport

#
logger = setup_logger()


#######################################################################################
## MAIN GUI APP
#
class DSClinicAppGUI(tk.Tk):
    def __init__(self, initial_data: dict | None = None):
        super().__init__()

        # Model
        self.model: MedicalReport = MedicalReport() if not initial_data else MedicalReport.model_validate(initial_data)

        # ViewModel
        self.view_model = DSClinicViewModel(self, self.model)

        # Main View
        self.view = DSClinicView(self, self.view_model)
        
        # Main Controller
        self.controller = DSClinicController(self, self.model, self.view, self.view_model)


##########################################################################################
## SCRIPT FILE ENTRY POINT
#
if __name__ == "__main__":
    # Config
    logger.setLevel(logging.DEBUG)

    logger.info(f" DSClinicGUI v{config.APP_VERSION} run with parameters:\n")
    # Pravljenje apsolutnih putanja pomoću PyInstaller-safe funkcije
    base_dir = utils.get_base_dir_path()
    logger.info(f"{' ' * 3}- Root directory: {base_dir}.")
    logger.info("="*60)
    
    
    # Initial / Test Data
    test_podaci = {
        "report_id": "1",
        "report_date": "03/19/2026",
        "content": {
            "patient_name": "Marko Marković",
            "recommended_therapy_and_advice": "Smanjiti fizički napor.",
            "critical_findings": [{"expertsko_misljenje": "Puls je povišen.", "parametar_and_value": "Puls: 75 bpm"}]
        }
    }

    # Init App
    app = DSClinicAppGUI(initial_data=test_podaci)
    # Run App
    app.mainloop()