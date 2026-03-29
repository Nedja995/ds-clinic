import tkinter as tk
from npy.core.logger import setup_logger
import logging
import config
from npy.core import utils
from models import MedicalReport
from dsclinic_gui.report_view_models import DSClinicViewModel
from dsclinic_gui.report_view import DSClinicView

#
logger = setup_logger()


#######################################################################################
## MAIN GUI APP
#
class DSClinicAppGUI(tk.Tk):
    def __init__(self, initial_data: MedicalReport | dict):
        super().__init__()
        # Data
        self.medical_report: MedicalReport = initial_data if not initial_data else MedicalReport.model_validate(initial_data)
        # View Model
        self.view_model = DSClinicViewModel(self, self.medical_report)
        # View
        self.report_view = DSClinicView(self, self.view_model, self.medical_report)


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