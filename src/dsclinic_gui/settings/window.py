import tkinter as tk

def open_settings(master: tk.Misc):
    # Create a secondary window
    settings_win = tk.Toplevel(master)
    settings_win.title("Settings")
    settings_win.geometry("250x150")
    
    # Add settings widgets (labels, entries, buttons)
    tk.Label(settings_win, text="Settings Options").pack(pady=10)
    tk.Button(settings_win, text="Close", command=settings_win.destroy).pack()

# root = tk.Tk()
# root.title("Main Application")
# root.geometry("400x300")

# # Button to open settings
# tk.Button(root, text="Open Settings", command=open_settings).pack(pady=20)

# root.mainloop()
