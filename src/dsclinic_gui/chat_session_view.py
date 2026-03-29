from typing import Optional, Any
import tkinter as tk
import tkinter.ttk as ttk
from dsclinic_gui.report_view_models import DSClinicViewModel

class ChatSessionView(ttk.Frame):
    """
    View for a single chat session, including initial question, response, 
    and follow-up question.
    """
    def __init__(self, parent: tk.Misc, view_model: DSClinicViewModel, **kwargs: Any) -> None:
        super().__init__(parent, **kwargs)
        self.view_model = view_model
        self.configure(style="Panel.TFrame", padding=10)
        #self._build_ui()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        # Proportions: 30%, 40%, 15% -> ~6, 8, 3
        self.rowconfigure(1, weight=6)
        self.rowconfigure(3, weight=8)
        self.rowconfigure(4, weight=3)

        # --- Initial Question ---
        ttk.Label(self, text="Inicijalno pitanje:", style="FormLabel.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 2))
        self.txt_initial_question = ttk.Entry(self, textvariable=self.view_model.var_initial_question) #self.view._scrolled_text(self, height=1)
        self.txt_initial_question.grid(row=1, column=0, sticky="nsew", pady=(0, 10))

        # --- Response ---
        ttk.Label(self, text="Odgovor:", style="FormLabel.TLabel").grid(row=2, column=0, sticky="w", pady=(0, 2))
        self.txt_response = ttk.Entry(self, textvariable=self.view_model.var_response) #self.view._scrolled_text(self, height=1)
        self.txt_response.grid(row=3, column=0, sticky="nsew", pady=(0, 10))

        # --- Follow-up Question ---
        follow_up_frame = ttk.Frame(self, style="Panel.TFrame")
        follow_up_frame.grid(row=4, column=0, sticky="nsew", pady=(10, 0))
        follow_up_frame.columnconfigure(1, weight=1)
        follow_up_frame.rowconfigure(0, weight=1)

        ttk.Label(
            follow_up_frame, text="Pitanje:", style="FormLabel.TLabel"
        ).grid(row=0, column=0, sticky="w", padx=(0, 6))

        self.txt_follow_up = ttk.Entry(follow_up_frame) #self.view._scrolled_text(follow_up_frame, height=1)
        self.txt_follow_up.grid(row=0, column=1, sticky="nsew")

        ask_button = ttk.Button(
            follow_up_frame, text="Ask", style="Accent.TButton",
            # command=... # TODO: Add command
        )
        ask_button.grid(row=0, column=2, sticky="e", padx=(6, 0))
        
