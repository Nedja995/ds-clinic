import tkinter as tk
from dsclinic_gui.report_controller import DSClinicController
from dsclinic_gui.report_view import DSClinicView
from logger import setup_logger
import logging
from models import MedicalReportModel

#
logger = setup_logger()


#######################################################################################
## MAIN GUI APP
#
class DSClinicAppGUI(tk.Tk):
    def __init__(self, initial_data: dict | None = None):
        super().__init__()

        # Model
        self.model: MedicalReportModel = MedicalReportModel() if not initial_data else MedicalReportModel.model_validate(initial_data)

        # Main View
        self.view = DSClinicView(self)
        
        # Main Controller
        self.controller = DSClinicController(self, self.model, self.view)


##########################################################################################
## SCRIPT FILE ENTRY POINT
#
if __name__ == "__main__":
    # Config
    logger.setLevel(logging.DEBUG)
    
    # Initial / Test Data
    test_podaci = {
        "patient_name": "Marko Marković",
        "report_date": "24.05.2024.",
        "preporucena_terapija_i_savet": "Smanjiti fizički napor.",
        "nalazi": [{"parametar_i_vrednost": "Puls", "expertsko_misljenje": "75 bpm"}]
    }

    # Init App
    app = DSClinicAppGUI(initial_data=test_podaci)
    # Run App
    app.mainloop()