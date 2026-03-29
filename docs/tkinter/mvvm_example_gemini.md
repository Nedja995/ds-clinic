


Here is a professional, expandable example of the MVVM (Model-View-ViewModel) architecture using Python 3, `pydantic` (V2), and `tkinter`/`ttk`. 

### Architecture Breakdown
1. **Model**: Uses `pydantic.BaseModel` to guarantee data integrity and validation. It has no knowledge of the UI.
2. **ViewModel**: Acts as the bridge. It holds the `tkinter` control variables (`StringVar`, `IntVar`) and contains the business logic to update the Model from the Views and vice versa. It catches Pydantic validation errors and prepares them for the UI.
3. **Views**: Subclassed `ttk.Frame` and `ttk.PanedWindow` objects. They strictly handle the layout and bind to the ViewModel's variables. They never interact directly with the Pydantic Model.

### Python Code

```python
import tkinter as tk
from tkinter import ttk
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, Any


# ==========================================
# 1. MODEL
# ==========================================
class EmployeeModel(BaseModel):
    """
    Pydantic model representing our core data structure.
    Strictly handles data validation and structure.
    """
    first_name: str = Field(default="", min_length=2, max_length=50)
    last_name: str = Field(default="", min_length=2, max_length=50)
    age: int = Field(default=18, ge=18, le=100, description="Age must be between 18 and 100")


# ==========================================
# 2. VIEWMODEL
# ==========================================
class EmployeeViewModel:
    """
    ViewModel connecting the UI (Views) to the Data (Model).
    Exposes Tkinter variables for binding and methods for interaction.
    """
    def __init__(self, model: Optional[EmployeeModel] = None) -> None:
        self._model = model or EmployeeModel()

        # Tkinter StringVars for two-way data binding with Views
        # We use StringVar even for numbers to easily handle empty inputs during typing
        self.first_name_var: tk.StringVar = tk.StringVar(value=self._model.first_name)
        self.last_name_var: tk.StringVar = tk.StringVar(value=self._model.last_name)
        self.age_var: tk.StringVar = tk.StringVar(value=str(self._model.age))

        # Variables for UI feedback (Right View)
        self.status_message_var: tk.StringVar = tk.StringVar(value="Ready for input.")
        self.status_color_var: tk.StringVar = tk.StringVar(value="black")
        self.summary_var: tk.StringVar = tk.StringVar(value="No data saved yet.")

        # Optional: Add traces to clear status when user starts typing again
        self._setup_traces()

    def _setup_traces(self) -> None:
        """Clear error messages dynamically when user modifies input."""
        def clear_status(*args: Any) -> None:
            if self.status_color_var.get() == "red":
                self.status_message_var.set("Typing...")
                self.status_color_var.set("black")

        self.first_name_var.trace_add("write", clear_status)
        self.last_name_var.trace_add("write", clear_status)
        self.age_var.trace_add("write", clear_status)

    def save_data(self) -> None:
        """
        Attempts to update the Pydantic model with current variable states.
        Handles validation errors and updates status variables.
        """
        try:
            # Pydantic automatically coerces compatible types (e.g., str -> int for age)
            self._model = EmployeeModel(
                first_name=self.first_name_var.get(),
                last_name=self.last_name_var.get(),
                age=self.age_var.get()
            )
            
            # Update View feedback on success
            self.status_message_var.set("Data saved successfully!")
            self.status_color_var.set("green")
            self.summary_var.set(
                f"Saved Employee:\n"
                f"Name: {self._model.first_name} {self._model.last_name}\n"
                f"Age: {self._model.age}"
            )
        except ValidationError as e:
            # Extract the first error message from Pydantic and show it
            error_msg = e.errors()[0]["msg"]
            failed_field = e.errors()[0]["loc"][0]
            
            self.status_message_var.set(f"Error ({failed_field}): {error_msg}")
            self.status_color_var.set("red")
        except ValueError:
            self.status_message_var.set("Error: Age must be a valid number.")
            self.status_color_var.set("red")


# ==========================================
# 3. VIEWS
# ==========================================
class LeftInputView(ttk.Frame):
    """
    Left pane handling user input. 
    Binds Tkinter elements to ViewModel variables.
    """
    def __init__(self, parent: tk.Misc, viewmodel: EmployeeViewModel, **kwargs: Any) -> None:
        super().__init__(parent, **kwargs)
        self.viewmodel = viewmodel
        self._build_ui()

    def _build_ui(self) -> None:
        # Padding and Grid configuration for expandable layout
        self.columnconfigure(1, weight=1)

        # First Name
        ttk.Label(self, text="First Name:").grid(row=0, column=0, padx=5, pady=10, sticky=tk.W)
        first_name_entry = ttk.Entry(self, textvariable=self.viewmodel.first_name_var)
        first_name_entry.grid(row=0, column=1, padx=5, pady=10, sticky=tk.EW)

        # Last Name
        ttk.Label(self, text="Last Name:").grid(row=1, column=0, padx=5, pady=10, sticky=tk.W)
        last_name_entry = ttk.Entry(self, textvariable=self.viewmodel.last_name_var)
        last_name_entry.grid(row=1, column=1, padx=5, pady=10, sticky=tk.EW)

        # Age
        ttk.Label(self, text="Age:").grid(row=2, column=0, padx=5, pady=10, sticky=tk.W)
        age_entry = ttk.Entry(self, textvariable=self.viewmodel.age_var)
        age_entry.grid(row=2, column=1, padx=5, pady=10, sticky=tk.EW)

        # Save Button
        save_btn = ttk.Button(self, text="Save / Validate", command=self.viewmodel.save_data)
        save_btn.grid(row=3, column=0, columnspan=2, pady=20, sticky=tk.EW, padx=5)


class RightOutputView(ttk.Frame):
    """
    Right pane handling read-only output and application status.
    Reacts automatically to ViewModel changes.
    """
    def __init__(self, parent: tk.Misc, viewmodel: EmployeeViewModel, **kwargs: Any) -> None:
        super().__init__(parent, **kwargs)
        self.viewmodel = viewmodel
        self._build_ui()

    def _build_ui(self) -> None:
        ttk.Label(self, text="System Feedback", font=("Helvetica", 12, "bold")).pack(pady=10)

        # Status Label (Changes color based on success/error)
        self.status_label = ttk.Label(self, textvariable=self.viewmodel.status_message_var, wraplength=250)
        self.status_label.pack(pady=5, fill=tk.X)
        
        # Trace the color variable to dynamically update the label's foreground color
        self.viewmodel.status_color_var.trace_add("write", self._update_status_color)

        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)

        # Summary Label
        ttk.Label(self, text="Database Record:", font=("Helvetica", 10, "italic")).pack(anchor=tk.W)
        ttk.Label(self, textvariable=self.viewmodel.summary_var, justify=tk.LEFT).pack(anchor=tk.W, pady=5)

    def _update_status_color(self, *args: Any) -> None:
        """Updates the foreground color of the status label."""
        color = self.viewmodel.status_color_var.get()
        self.status_label.config(foreground=color)


class MainContainerView(ttk.PanedWindow):
    """
    Main layout controller. Uses a horizontal PanedWindow to separate 
    left and right views with a vertical, draggable sash.
    """
    def __init__(self, parent: tk.Misc, viewmodel: EmployeeViewModel, **kwargs: Any) -> None:
        # orient=tk.HORIZONTAL creates panes side-by-side separated by a vertical line
        super().__init__(parent, orient=tk.HORIZONTAL, **kwargs)

        # Instantiate sub-views
        self.left_view = LeftInputView(self, viewmodel, padding=15)
        self.right_view = RightOutputView(self, viewmodel, padding=15)

        # Add views to PanedWindow
        # weight=1 allows both sides to expand equally when resizing window
        self.add(self.left_view, weight=1)
        self.add(self.right_view, weight=1)


# ==========================================
# 4. APP ENTRY POINT
# ==========================================
class App(tk.Tk):
    """
    Root Application window.
    Bootstraps the ViewModel and the Main Container.
    """
    def __init__(self) -> None:
        super().__init__()
        
        self.title("Expandable MVVM Pattern")
        self.geometry("650x350")
        self.minsize(500, 300)

        # 1. Initialize ViewModel
        self.viewmodel = EmployeeViewModel()

        # 2. Initialize Main View Container
        self.main_container = MainContainerView(self, self.viewmodel)
        
        # 3. Pack container into root window
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Configure generic styles if needed
        self._configure_styles()

    def _configure_styles(self) -> None:
        """Set up standard ttk styles for professional look."""
        style = ttk.Style(self)
        # Using native OS theme ('clam', 'alt', 'default', 'vista' depending on OS)
        if "clam" in style.theme_names():
            style.theme_use("clam")


if __name__ == "__main__":
    app = App()
    app.mainloop()
```

### Key Highlights of the Code:
1. **Vertical Separator**: Uses `ttk.PanedWindow(orient=tk.HORIZONTAL)`. This implies the layout flow is horizontal, which results in a **vertical draggable sash** that cleanly separates the `LeftInputView` and `RightOutputView` and allows the user to resize them.
2. **`pydantic` Validations**: The `EmployeeModel` uses boundaries (`ge=18`, `min_length=2`). The `save_data` method correctly catches `ValidationError` dynamically and maps the validation message into a `ttk.Label` warning.
3. **Type Checking**: Subclassed types accurately point to tkinter base classes (`tk.Misc` for `parent`, `tk.Tk` for App, `ttk.Frame` for layouts). Included `Any` and `Optional` where required to be cleanly checked by tools like `mypy`.
4. **Expandable and Reactive Design**: The logic uses `trace_add` to dynamically reset error states when the user changes the text. You can add more complex Model variables without cluttering the views.