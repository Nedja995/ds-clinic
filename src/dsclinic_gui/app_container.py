import tkinter as tk
from tkinter import ttk
from typing import Any

from dsclinic_gui.report_view_models import DSClinicViewModel


class RootContainerView(ttk.Frame):
    """
    Root container for the entire application. This is the top-level frame that holds all other views.
    It can be used to manage global state or provide common functionality to all child views.
    """
    def __init__(self, parent: tk.Misc, view_model: DSClinicViewModel, **kwargs: Any) -> None:
        super().__init__(parent, **kwargs)
        
        self.view_model = view_model
        
        self.configure(style="Root.TFrame", padding=0)