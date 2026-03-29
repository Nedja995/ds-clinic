import tkinter as tk
from npy.core.logger import setup_logger
import logging
import config
from npy.core import utils
from models import MedicalReport
from dsclinic_gui.report_view_models import DSClinicViewModel
from dsclinic_gui.report_view import MedicalReportView
from dsclinic_gui.main_container import MainContainerView
from dsclinic_gui.styles import build_styles

#
logger = setup_logger()

_WINDOW_TITLE = "Holisticki centar"
MIN_WIDTH = 620
MIN_HEIGHT = 700
INIT_WIDTH = 620
INIT_HEIGHT = 700

#######################################################################################
## MAIN GUI APP
#
class DSClinicAppGUI(tk.Tk):
    def __init__(self, initial_data: MedicalReport | dict):
        super().__init__()
        
        #
        self._configure_app()
        
        #
        build_styles()
        
        # Data
        medical_report: MedicalReport = initial_data if not initial_data else MedicalReport.model_validate(initial_data)
        
        # View Model
        self.view_model = DSClinicViewModel(medical_report)
        
        # Main Container View
        self.main_container = MainContainerView(self, self.view_model)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # View
        #self.report_view = MedicalReportView(self, self.view_model, self.medical_report)
        
    def _configure_app(self):
        self.title(_WINDOW_TITLE)
        self.minsize(MIN_WIDTH, MIN_HEIGHT)
        self.geometry(f"{INIT_WIDTH}x{INIT_HEIGHT}")
        self.resizable(width=True, height=True)
        # self.root.update_idletasks() # Ensure geometry is applied before further calculations
        # self.root.grid_columnconfigure(0, weight=1)
        # self.root.grid_rowconfigure(0, weight=1)

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