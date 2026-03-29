


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







In the MVVM architecture, the **ViewModel** is a standard Python class designed to be independent of the UI framework's main window lifecycle. Because it doesn't inherit from Tkinter widgets (like `tk.Tk` or `tk.Frame`), it does not have access to the `.after()` method. 

Here is the professional way to handle this separation of concerns:

1. **The Thread and Queue** belong in the **ViewModel** (or a separate Service class called by the ViewModel). The ViewModel is responsible for spawning the thread, doing the long-running task, and pushing results to the queue.
2. **The `.after()` loop** belongs in the **View**. The View is part of the Tkinter event loop and should be responsible for polling the ViewModel to see if there's new data.

To make this highly efficient, we shouldn't poll forever. Instead, we can use a `tk.BooleanVar` in the ViewModel to indicate when a background task is running, and the View can trace this variable to start and stop its `.after()` polling loop.

Here is how you expand the previous example to properly implement this:

### 1. Update the ViewModel

We will add a `queue.Queue`, a `threading.Thread`, and a boolean variable that tells the View when to start checking for updates.

```python
import threading
import queue
import time
import tkinter as tk
from typing import Optional, Any
from pydantic import BaseModel # (Assuming EmployeeModel is already defined)

class EmployeeViewModel:
    def __init__(self, model: Optional['EmployeeModel'] = None) -> None:
        # ... (Previous initializations: first_name_var, etc.) ...
        
        # --- NEW: Threading & Queue Variables ---
        self.task_queue: queue.Queue = queue.Queue()
        self.is_processing_var: tk.BooleanVar = tk.BooleanVar(value=False)
        self.progress_var: tk.IntVar = tk.IntVar(value=0) # For a progress bar

    def start_long_running_task(self) -> None:
        """Starts the background thread safely."""
        if self.is_processing_var.get():
            return  # Prevent multiple threads from starting

        # Set UI state to processing
        self.is_processing_var.set(True)
        self.progress_var.set(0)
        self.status_message_var.set("Connecting to server...")
        self.status_color_var.set("blue")

        # Spawn daemon thread so it closes if the main app closes
        threading.Thread(target=self._heavy_worker_process, daemon=True).start()

    def _heavy_worker_process(self) -> None:
        """The blocking process running in a separate thread. NEVER update Tkinter UI directly here."""
        try:
            # Simulate a 5-second blocking process (e.g., API call, Database write)
            for i in range(1, 6):
                time.sleep(1) # Blocking call
                # Put progress updates in the queue
                self.task_queue.put({"type": "progress", "value": i * 20})
            
            # Put final success result in queue
            self.task_queue.put({"type": "success", "message": "Data synced successfully!"})
        
        except Exception as e:
            self.task_queue.put({"type": "error", "message": str(e)})

    def process_queue_messages(self) -> None:
        """Called by the View to process messages safely on the Main UI Thread."""
        try:
            # Loop to empty all currently available messages in the queue
            while True:
                msg = self.task_queue.get_nowait()
                
                if msg["type"] == "progress":
                    self.progress_var.set(msg["value"])
                
                elif msg["type"] == "success":
                    self.status_message_var.set(msg["message"])
                    self.status_color_var.set("green")
                    self.is_processing_var.set(False) # Stop the View's polling
                
                elif msg["type"] == "error":
                    self.status_message_var.set(f"Thread Error: {msg['message']}")
                    self.status_color_var.set("red")
                    self.is_processing_var.set(False) # Stop the View's polling

        except queue.Empty:
            # Queue is empty, nothing to do right now
            pass
```

### 2. Update the View

The View will "listen" (via `trace_add`) to `is_processing_var`. When it turns `True`, the View will kick off a `.after()` loop to check the queue every 100 milliseconds.

```python
from tkinter import ttk

class RightOutputView(ttk.Frame):
    def __init__(self, parent: tk.Misc, viewmodel: EmployeeViewModel, **kwargs: Any) -> None:
        super().__init__(parent, **kwargs)
        self.viewmodel = viewmodel
        self._build_ui()
        self._setup_polling()

    def _build_ui(self) -> None:
        # ... (Previous UI setup: status labels, etc.) ...
        
        # --- NEW: Progress Bar ---
        self.progress_bar = ttk.Progressbar(
            self, 
            orient=tk.HORIZONTAL, 
            mode='determinate', 
            variable=self.viewmodel.progress_var
        )
        self.progress_bar.pack(fill=tk.X, pady=10)
        
        # --- NEW: Test Button ---
        ttk.Button(
            self, 
            text="Simulate API Sync", 
            command=self.viewmodel.start_long_running_task
        ).pack(pady=5)

    def _setup_polling(self) -> None:
        """Sets up a listener for when processing starts."""
        self.viewmodel.is_processing_var.trace_add("write", self._on_processing_changed)

    def _on_processing_changed(self, *args: Any) -> None:
        """Triggered automatically when the background task starts or stops."""
        is_running = self.viewmodel.is_processing_var.get()
        
        if is_running:
            # Lock the UI/Buttons if necessary, and start polling the queue
            self._poll_queue()
        else:
            # Ensure the queue is checked one last time when stopping
            self.viewmodel.process_queue_messages()

    def _poll_queue(self) -> None:
        """The loop that checks the queue while processing is True."""
        # 1. Ask ViewModel to process any messages in the queue
        self.viewmodel.process_queue_messages()
        
        # 2. If the task is still running, schedule another check in 100ms
        if self.viewmodel.is_processing_var.get():
            self.after(100, self._poll_queue)
```

### Why this structure is excellent:
1. **Thread Safety**: Tkinter crashes or behaves unpredictably if you update UI variables (like `StringVar` or `.config()`) from a background thread. `queue.Queue` acts as a thread-safe mailbox.
2. **Resource Friendly**: You aren't running an infinite `.after()` loop in the background of your app from the moment it opens. The View only starts polling exactly when the `is_processing_var` becomes `True`, and stops exactly when it hits `False`.
3. **Strict MVVM**: The ViewModel knows absolutely nothing about Tkinter Widgets or the Main Event Loop (`.after()`), which makes testing the ViewModel with `pytest` incredibly easy—you can just call `start_long_running_task()` in your unit tests and evaluate the queue contents directly without needing to boot up a Tkinter GUI.








You have excellent architectural instincts! You've hit on one of the classic challenges of implementing MVVM in single-threaded UI frameworks like Tkinter.

You are correct that **Views should be as "dumb" as possible**—they should only handle layout and binding, not the orchestration of when to check for background tasks. 

Let's evaluate your two suggestions:

1. **Passing `.after()` to the ViewModel:** This breaks strict MVVM. The ViewModel should not know about Tkinter's event loop. If you later decided to port your app to PyQt, Web, or a CLI, your ViewModel would crash because `.after()` doesn't exist in those frameworks.
2. **Putting it in the `App` main class:** **This is the perfect solution.** In MVVM, the Root class (often called the App, Bootstrapper, or WindowManager) acts as the **Dispatcher**. It bridges the framework-specific event loop to your UI-agnostic ViewModels.

Here is how you refactor the code to achieve absolute architectural purity: the View does zero orchestration, the ViewModel does zero Tkinter looping, and the App handles the framework mechanics.

### 1. The Clean View (No polling logic)
We completely remove the polling logic from the View. The View goes back to doing only what it should: displaying data and firing commands.

```python
from tkinter import ttk
import tkinter as tk
from typing import Any

class RightOutputView(ttk.Frame):
    """
    100% 'Dumb' View. 
    It only binds to variables and knows nothing about threads or queues.
    """
    def __init__(self, parent: tk.Misc, viewmodel: 'EmployeeViewModel', **kwargs: Any) -> None:
        super().__init__(parent, **kwargs)
        self.viewmodel = viewmodel
        self._build_ui()

    def _build_ui(self) -> None:
        # Status Label
        self.status_label = ttk.Label(self, textvariable=self.viewmodel.status_message_var)
        self.status_label.pack(pady=5, fill=tk.X)
        self.viewmodel.status_color_var.trace_add("write", self._update_status_color)
        
        # Progress Bar
        self.progress_bar = ttk.Progressbar(
            self, orient=tk.HORIZONTAL, mode='determinate', 
            variable=self.viewmodel.progress_var
        )
        self.progress_bar.pack(fill=tk.X, pady=10)
        
        # Button triggers ViewModel command directly
        ttk.Button(
            self, text="Simulate API Sync", 
            command=self.viewmodel.start_long_running_task
        ).pack(pady=5)

    def _update_status_color(self, *args: Any) -> None:
        color = self.viewmodel.status_color_var.get()
        self.status_label.config(foreground=color)
```

### 2. The Pure ViewModel
The ViewModel handles the thread and the queue, and exposes a `flush_queue()` method. It remains completely unaware of how or when `flush_queue()` is called.

```python
import threading
import queue
import time
import tkinter as tk
from typing import Optional

class EmployeeViewModel:
    def __init__(self, model: Optional['EmployeeModel'] = None) -> None:
        # Standard variables
        self.status_message_var = tk.StringVar(value="Ready.")
        self.status_color_var = tk.StringVar(value="black")
        
        # Threading state
        self.progress_var = tk.IntVar(value=0)
        self.is_processing_var = tk.BooleanVar(value=False)
        self.task_queue: queue.Queue = queue.Queue()

    def start_long_running_task(self) -> None:
        """Kicks off the background business logic."""
        if self.is_processing_var.get():
            return
            
        self.is_processing_var.set(True)
        self.status_message_var.set("Processing...")
        
        # The ViewModel manages its own thread
        threading.Thread(target=self._heavy_worker, daemon=True).start()

    def _heavy_worker(self) -> None:
        """Pure python logic running in background."""
        for i in range(1, 6):
            time.sleep(1) # Simulate API call
            self.task_queue.put({"type": "progress", "value": i * 20})
            
        self.task_queue.put({"type": "done", "msg": "Sync complete!"})

    def flush_queue(self) -> None:
        """
        Translates queue messages into UI State.
        This is completely separated from Tkinter's .after() method.
        """
        try:
            while True:
                msg = self.task_queue.get_nowait()
                if msg["type"] == "progress":
                    self.progress_var.set(msg["value"])
                elif msg["type"] == "done":
                    self.status_message_var.set(msg["msg"])
                    self.status_color_var.set("green")
                    self.is_processing_var.set(False)
        except queue.Empty:
            pass
```

### 3. The App / Bootstrapper (The Orchestrator)
In professional MVVM, the root container acts as the **Infrastructure Layer**. It marries the OS event loop (Tkinter) to your application's architecture.

```python
class App(tk.Tk):
    """
    Root Window and Application Bootstrapper.
    Acts as the Dispatcher bridging the Tkinter event loop to ViewModel queues.
    """
    def __init__(self) -> None:
        super().__init__()
        self.title("Pure MVVM Threading")
        
        # 1. Boot up ViewModels
        self.viewmodel = EmployeeViewModel()
        
        # 2. Boot up Views
        self.main_container = MainContainerView(self, self.viewmodel)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # 3. Setup App-Level Dispatcher
        self._setup_dispatcher()

    def _setup_dispatcher(self) -> None:
        """
        The App monitors all ViewModels. When a ViewModel is processing, 
        the App orchestrates the Tkinter event loop to flush the queue.
        """
        self.viewmodel.is_processing_var.trace_add("write", self._on_processing_state_changed)

    def _on_processing_state_changed(self, *args: Any) -> None:
        """Triggered when the ViewModel signals it has started/stopped a thread."""
        if self.viewmodel.is_processing_var.get():
            self._poll_viewmodels()

    def _poll_viewmodels(self) -> None:
        """
        The framework-specific polling loop.
        Safely flushes cross-thread queues on the main UI thread.
        """
        # Ask ViewModel to handle its queue
        self.viewmodel.flush_queue()
        
        # If it's still running, schedule the next tick
        if self.viewmodel.is_processing_var.get():
            self.after(50, self._poll_viewmodels)
```

### Why this is the ultimate architecture:
1. **Views are pure UIs:** The Views don't know that threads or queues even exist. They just display the `progress_var`.
2. **ViewModels are pure logic:** The ViewModel doesn't know about `tk.Tk` or `.after()`. You could easily unit test `EmployeeViewModel` using `pytest` without booting up an application window. You just call `start_long_running_task()` and check the contents of `task_queue`.
3. **App acts as the framework bridge:** By giving the responsibility of `.after()` to the `App` class, you respect the fact that `App` *owns* the Tkinter event loop (`mainloop()`). It naturally makes sense that the App is the object responsible for scheduling tasks within that loop. If you ever add a `CustomerViewModel` or `SettingsViewModel`, your `App` dispatcher can handle polling all of them centrally!