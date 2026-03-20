import tkinter as tk
#
from npy.core.logger import setup_logger
from models import MedicalReport
#
from dsclinic_gui.report_view import DSClinicView
from dsclinic_gui.report_view_models import DSClinicViewModel

logger = setup_logger()


class DSClinicController:
    """
    Application Composer / Coordinator.
    Initializes the Model, ViewModel, and View, and connects them.
    """
    def __init__(self, root: tk.Tk, model: MedicalReport, view: DSClinicView, viewModel: DSClinicViewModel):
        self.root = root
        self.model = model
        self.view = view
        self.view_model = viewModel
