# DSClinic v2 - critical architecture issues

---

## MVVM Violations in `dsclinic_gui` and `settings`

---

### 5. `SettingsWindow` creates its own ViewModel — no dependency injection

**File:** `settings/settings_view.py`

```python
def __init__(self, master: tk.Misc, **kwargs) -> None:
    ...
    self.view_model = SettingsViewModel(self)   # View owns VM creation
```

Every time `open_settings()` is called, a fresh `SettingsViewModel` is constructed by reading `config` module globals. This means:

- Any runtime state not yet flushed to `config` is silently dropped
- You cannot inject a shared or pre-populated ViewModel
- You cannot test the View with a mock ViewModel

The ViewModel should be constructed once (in `DSClinicAppGUI` or a dedicated factory) and injected: `SettingsWindow(master, view_model=settings_vm)`.

---

### 6. `update_view_from_viewmodel()` is triggered by status changes and destroys all finding rows

**File:** `report_view.py`

```python
self.view_model.var_status_title.trace_add("write", lambda *args: self.update_view_from_viewmodel())
self.view_model.var_is_analyzing.trace_add("write", lambda *args: self.update_view_from_viewmodel())
```

`update_view_from_viewmodel()` performs a **full teardown and rebuild** of every finding row widget. During an analysis run, `var_status_title` changes through "Running" → "Analyzing…" → "Finished" — each transition destroys and recreates the entire findings list. If the user was typing inside a finding row when the status changed, their input is silently discarded. Status display is already correctly handled by `textvariable=` bindings on the footer labels; those traces triggering a full rebuild are purely destructive.

The findings list should have its own dedicated observable or `EventEmitter` that fires only when findings data actually changes.


---

### 10. `RootContainerView` in `app_container.py` is dead code

**File:** `app_container.py`

`RootContainerView` is defined but never instantiated anywhere in the application. `MainContainerView` is used instead. This is a leftover from an earlier architecture that was not cleaned up.

---

### Summary Table

| #   | File                       | Violation                                        | Severity |
| --- | -------------------------- | ------------------------------------------------ | -------- |
| 1   | `report_view_models.py`    | ViewModel calls `filedialog`/`messagebox`        | Critical |
| 2   | `dsclinic_gui_app.py` + VM | Double polling — queue drained twice per tick    | High     |
| 3   | `report_view_models.py`    | `followup_question_submit` blocks main thread    | High     |
| 4   | `settings_view_model.py`   | ViewModel takes `tk.Misc` root — untestable      | Medium   |
| 5   | `settings_view.py`         | View creates its own ViewModel — no DI           | Medium   |
| 6   | `report_view.py`           | Status trace triggers full row rebuild           | Medium   |
| 7   | `report_view.py`           | `_row_parity` not reset on rebuild               | Low      |
| 8   | `report_view_models.py`    | `therapy_text_content` plain str, not observable | Medium   |
| 9   | `settings_view.py`         | `_on_save` is a no-op TODO                       | Low      |
| 10  | `app_container.py`         | `RootContainerView` is dead code                 | Low      |

### Follow-up Questions

- How should `followup_question_submit` be refactored to use the existing `thread + queue + ProgressEvent` pattern, and should chat history state live in the same ViewModel or a dedicated `ChatSessionViewModel`?
- How should `SettingsViewModel` be constructed and shared so that saving settings actually updates the live `DSClinicViewModel`'s `dsclinicapp` instance?
