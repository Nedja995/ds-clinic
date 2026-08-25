

import tkinter as tk
from tkinter import ttk
from typing import Any

from dsclinic_gui.report_view import MedicalReportView
from dsclinic_gui.report_view_models import DSClinicViewModel
from dsclinic_gui.chat_session_view import ChatSessionView
from dsclinic_gui.constants import INIT_WIDTH

class MainContainerView(ttk.PanedWindow):
    """
    Main layout controller. Uses a horizontal PanedWindow to separate 
    left and right views with a vertical, draggable sash.
    """
    def __init__(self, parent: tk.Misc, view_model: DSClinicViewModel, **kwargs: Any) -> None:
        # orient=tk.HORIZONTAL creates panes side-by-side separated by a vertical line
        super().__init__(parent, orient=tk.HORIZONTAL, **kwargs)

        # Instantiate sub-views
        self.left_view = MedicalReportView(self, view_model, padding=4)
        self.right_view = ChatSessionView(self, view_model, padding=4)

        # Add views to PanedWindow
        self.add(self.left_view, weight=8)  # weight=8 means it takes 8 parts of the scalable space (80% of the total width)
        self.add(self.right_view, weight=2) # weight=2 means it takes 2 parts of the scalable space (20% of the total width)


        # self.left_view.configure(width=left_w)
        # self.right_view.configure(width=right_w)