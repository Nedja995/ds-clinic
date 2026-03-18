import tkinter as tk
from tkinter import ttk

class CustomMessageBox(object):
    def __init__(self, parent, title, message, button_texts: list[str] = ["OK"]):
        # Store the parent window
        self.parent = parent
        self.choice = None  # This will store the button clicked
        
        # Create the Toplevel window and make it transient to the parent
        self.top = tk.Toplevel(parent)
        self.top.transient(parent)
        self.top.title(title)

        # Hide window while we build it and position it
        self.top.withdraw()
        
        # Prevent the main window from being used while the dialog is open
        self.top.grab_set() 
        
        # Add a message label
        ttk.Label(self.top, text=message, padding=10).pack(pady=10)
        
        # Create a frame for the buttons
        button_frame = ttk.Frame(self.top)
        button_frame.pack(pady=10)
        
        # Create custom buttons
        for text in button_texts:
            ttk.Button(button_frame, text=text, 
                       command=lambda t=text: self.on_button_click(t)).pack(side=tk.LEFT, padx=5)

        # --- Center the window on the parent ---
        self.top.update_idletasks()  # Update "requested size" from geometry manager

        # Get parent and dialog window sizes
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()

        dialog_width = self.top.winfo_width()
        dialog_height = self.top.winfo_height()

        # Calculate position to center the dialog and set it
        pos_x = parent_x + (parent_width // 2) - (dialog_width // 2)
        pos_y = parent_y + (parent_height // 2) - (dialog_height // 2)
        self.top.geometry(f"+{pos_x}+{pos_y}")
        self.top.deiconify() # Show the window now that it's positioned
            
        # Ensure the window waits here until it's closed
        self.top.wait_window()

    def on_button_click(self, choice):
        """Handle button clicks and close the window."""
        self.choice = choice
        self.top.destroy()

# def show_custom_message():
#     """Function to launch the custom message box."""
#     # Create an instance of our custom message box
#     msg_box = CustomMessageBox(root, "Choose an Option", "Please select one of the following:", 
#                                ["Option A", "Option B", "Option C"])
#     # The program flow stops at wait_window() until the dialog is closed.
#     # The result is available after the window is destroyed.
#     print(f"User chose: {msg_box.choice}")
