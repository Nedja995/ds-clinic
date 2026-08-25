import tkinter as tk
import tkinter.ttk as ttk
from typing import Callable, Optional, Any


class Toolbar(ttk.Frame):
    """
    A standalone toolbar widget.
    It should not depend on a specific ViewModel, but rather on constructor
    arguments for Tk variables and action commands.
    """

    def __init__(
        self,
        parent: tk.Misc,
        analyze_text_var: tk.StringVar,
        analyze_command: Callable[[], None],
        export_command: Callable[[], None],
        details_command: Optional[Callable[[], None]] = None,
        settings_command: Optional[Callable[[], None]] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(parent, style="Toolbar.TFrame", padding=(0, 6), **kwargs)

        self.analyze_text_var = analyze_text_var
        self.analyze_command = analyze_command
        self.export_command = export_command
        self.details_command = details_command
        self.settings_command = settings_command

        self._build_ui()

    def _build_ui(self) -> None:
        # Analyze Button
        self.btn_analyze = self._toolbar_button(
            self,
            textvariable=self.analyze_text_var,
            command=self.analyze_command,
            side="left"
        )

        # Export Button
        self.btn_export = self._toolbar_button(
            self, text="Export 1", command=self.export_command, side="left"
        )

        # Details Button (disabled if no command provided)
        self.btn_full_report = self._toolbar_button(
            self, text="Details", command=self.details_command,
            state="disabled" if self.details_command is None else "normal", side="left"
        )

        # Settings Button
        self.btn_settings = self._toolbar_button(
            self, text="Settings", command=self.settings_command, side="right"
        )

    def _toolbar_button(self, parent: tk.Widget, text: str = "", textvariable: Optional[tk.StringVar] = None,
                         command: Optional[Callable[[], None]] = None, state: str = "normal", side: str = "left") -> ttk.Button:
        kw: dict = dict(style="Toolbar.TButton", state=state, command=command)
        if textvariable:
            btn = ttk.Button(parent, textvariable=textvariable, **kw)
        else:
            btn = ttk.Button(parent, text=text, **kw)
        btn.pack(side=side, padx=(6, 0) if side == "left" else (0, 6))
        return btn
