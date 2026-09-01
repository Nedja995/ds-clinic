"""
Main layout controller.

Owns: the top-level horizontal PanedWindow that divides the three primary
panes — session history sidebar (left), report form (centre), chat (right).

Does NOT own: any business logic, persistence, or widget state beyond the
sash layout.
"""
import tkinter as tk
from tkinter import ttk
from typing import Any

from dsclinic_gui.report_view import MedicalReportView
from dsclinic_gui.report_view_models import DSClinicViewModel
from dsclinic_gui.chat_session_view import ChatSessionView
from dsclinic_gui.session_history_view import SessionHistoryView


class MainContainerView(ttk.PanedWindow):
    """
    Three-pane horizontal layout:
      weight=2  SessionHistoryView  — saved session sidebar
      weight=6  MedicalReportView   — report form (reduced from 8 to make room)
      weight=2  ChatSessionView     — AI chat panel
    """

    def __init__(self, parent: tk.Misc, view_model: DSClinicViewModel, **kwargs: Any) -> None:
        super().__init__(parent, orient=tk.HORIZONTAL, **kwargs)

        self.session_view = SessionHistoryView(self, view_model)
        self.left_view    = MedicalReportView(self, view_model, padding=4)
        self.right_view   = ChatSessionView(self, view_model, padding=4)

        self.add(self.session_view, weight=2)
        self.add(self.left_view,    weight=6)
        self.add(self.right_view,   weight=2)
