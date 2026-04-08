# DSClinic v2 - critical architecture issues

---

## MVVM Violations in `dsclinic_gui` and `settings`

---

### 2. Double polling — the ViewModel and the App both reschedule `_poll_result_queue`

**Files:** `dsclinic_gui_app.py` + `report_view_models.py`

`_poll_result_queue` reschedules itself internally via `self.schedule_poll_fn(...)`. But `DSClinicAppGUI._poll_viewmodels()` **also** calls `self.view_model._poll_result_queue()` and reschedules **itself** via `self.after(...)`. Every polling interval, the queue is drained **twice**. The first drain might consume the `FINISHED` event, so the second drain sees an empty queue and does nothing — but it still runs every tick for the lifetime of the task. This is a latent bug that becomes obvious the moment you add a second `ProgressEvent`.

The established pattern — injecting `schedule_poll_fn` into the ViewModel so it self-schedules — was the right solution. The `_setup_dispatcher` in the App is a redundant layer that contradicts it.

---

### 3. `followup_question_submit` is a synchronous blocking call on the main thread

**File:** `report_view_models.py`

```python
def followup_question_submit(self):
    answer = self.dsclinicapp.ask_followup_question(question)  # blocks!
    self.var_response.set(answer)
```

This freezes the entire Tkinter event loop while the Gemini API call is in flight. Every pattern established for `_start_analysis` (thread + queue + `ProgressEvent`) is completely skipped here. A chat reply call can take 2–10 seconds; the window will be unresponsive for all of it.

---

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

### 7. `_row_parity` is never reset before a row rebuild

**File:** `report_view.py`

```python
def update_view_from_viewmodel(self):
    for w in self.critical_finding_widgets:
        w["frame"].destroy()
    self.critical_finding_widgets.clear()
    # _row_parity is NOT reset here
    for i, finding in enumerate(self.view_model.findings):
        self._render_finding_row(i, finding)   # _row_parity += 1 inside
```

`_row_parity` accumulates across every rebuild. After two rebuilds of 3 rows each, it reaches 6 — so the alternating row color pattern is wrong from the second rebuild onward. Fix: `self._row_parity = 0` before the loop.

---

### 8. `therapy_text_content` is a plain string attribute — no observable, no EventEmitter

**File:** `report_view_models.py`

```python
self.therapy_text_content = self._model.content.recommended_therapy_and_advice
```

This is a plain `str` attribute. There's no `tk.StringVar` and no `EventEmitter` on it. The View must manually call `update_viewmodel_from_view()` before every operation that needs it up-to-date, and manually call `update_view_from_viewmodel()` to push it back. If either call is missed — for example before `save_report()` is triggered via keyboard shortcut rather than the export button — the therapy content silently lags behind what the user typed.

The correct approach is either a `tk.StringVar` (with the `ScrolledText ↔ StringVar` bidirectional sync pattern already demonstrated in `settings_view.py` via `_sync_text_widget`) or an `EventEmitter` that fires on focus-out.

---

### 9. `_on_save` in `SettingsWindow` is a no-op — ViewModel commands are stubs

**File:** `settings/settings_view.py`

```python
def _on_save(self) -> None:
    if not self.view_model.validate_email():
        return
    # TODO: persist settings to JSON
    self.destroy()
```

Settings are validated but never written back to `config` or to `settings.ini`. The ViewModel's own command stubs (`on_send_logs`, `on_show_logs_folder`) are also `pass`. The ViewModel's command layer exists in name only, breaking the contract that the ViewModel owns all application logic.

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

- How should `save_report()` be refactored so the ViewModel emits an event and the View owns the `filedialog`/`messagebox` interactions?
- What is the cleanest fix to eliminate the double polling problem — should the `_setup_dispatcher` in `DSClinicAppGUI` be removed entirely, or should the ViewModel stop self-scheduling?
- How should `followup_question_submit` be refactored to use the existing `thread + queue + ProgressEvent` pattern, and should chat history state live in the same ViewModel or a dedicated `ChatSessionViewModel`?
- How should `SettingsViewModel` be constructed and shared so that saving settings actually updates the live `DSClinicViewModel`'s `dsclinicapp` instance?
