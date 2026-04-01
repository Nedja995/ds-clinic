import tkinter as tk
from dsclinic_gui.settings.settings_view import SettingsWindow


def open_settings(master: tk.Misc) -> None:
    SettingsWindow(master)
