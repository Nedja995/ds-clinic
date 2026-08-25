import tkinter as tk
from npy.core.logger import setup_logger
import logging
import config
from npy.core import utils
from models import MedicalReport
from dsclinic_gui.report_view_models import DSClinicViewModel
from dsclinic_gui.main_container import MainContainerView
from dsclinic_gui.styles import build_styles
from dsclinic_gui.constants import MIN_WIDTH, MIN_HEIGHT, INIT_WIDTH, INIT_HEIGHT
from datetime import datetime

#
logger = setup_logger()


#

#######################################################################################
## MAIN GUI APP
#
class DSClinicAppGUI(tk.Tk):
    """
    Main Application Window for DSClinic GUI.
    """
    def __init__(self, initial_data: MedicalReport | dict):
        super().__init__()
        # Initialize App Window
        self._configure_app()
        # Styles
        build_styles()
        
        # Data
        medical_report: MedicalReport = initial_data if not initial_data else MedicalReport.model_validate(initial_data)
        
        ## View Models 
        # Report
        self.view_model = DSClinicViewModel(
            schedule_poll_fn=self.after, 
            model=medical_report)
        
        # Main Container View
        self.main_container = MainContainerView(self, self.view_model)
        self.main_container.pack(fill=tk.BOTH, expand=True)
    
        
        # View
        #self.report_view = MedicalReportView(self, self.view_model, self.medical_report)
        
        self._center_window(INIT_WIDTH, INIT_HEIGHT)
    
        # # Force update and set initial sash position to 80% of INIT_WIDTH
        # self.update_idletasks()
        # self.main_container.sashpos(0, int(INIT_WIDTH * 0.7))
        
    def _configure_app(self):
        self.title(config.APP_NAME)
        self.minsize(MIN_WIDTH, MIN_HEIGHT)
        self.geometry(f"{INIT_WIDTH}x{INIT_HEIGHT}")
        self.resizable(width=True, height=True)
        # self.update_idletasks() # Ensure geometry is applied before further calculations
        # self.grid_columnconfigure(0, weight=1)
        # self.grid_rowconfigure(0, weight=1)
    
    def _center_window(self, w: int, h: int):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")


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
    
    


    # Get the current local date and time
    current_date = datetime.now()

    # Format the date as day.month.year
    formatted_date = current_date.strftime("%d.%m.%Y")
    
    # Initial / Test Data
    # test_podaci = {
    #     "report_id": "1",
    #     "report_date": formatted_date,
    #     "content": {
    #         "patient_name": "Nepoznato",
    #         "recommended_therapy_and_advice": "Smanjiti fizički napor.",
    #         "critical_findings": [{"expertsko_misljenje": "Puls je povišen.", "parametar_and_value": "Puls: 75 bpm"}]
    #     }
    # }
    test_podaci = {
        "report_id": "1",
        "report_date": formatted_date,
        "content": {
            "patient_name": "Nepoznato",
            "recommended_therapy_and_advice": "",
            "critical_findings": []
        }
    }

    # Init App
    app = DSClinicAppGUI(initial_data=test_podaci)
    # Run App
    app.mainloop()