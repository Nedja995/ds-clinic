from operator import index
import threading
import queue
import time
import tkinter as tk
import os
import datetime
from typing import Optional, Any, Callable
from dataclasses import dataclass

from dsclinic_gui.settings.settings_view_model import SettingsViewModel
from npy.core.logger import setup_logger
from npy.core import utils, fileutils
import config
from models import MedicalReport, MedicalReportModel, MedicalCriticalFindingModel
# from dsclinic import get_initial_analysis_report, ask_followup_question
from dsclinic import DSClinic
from pdf_maker import generate_report_pdf_at_filepath
from npy.core.event_emitter import EventEmitter, ErrorMessageEvent
from models import TaskStatus, ProgressEvent
#
from dsclinic_gui.constants import QUEUE_POLL_INTERVAL_MS
# from hard_worker import run_hardwork
# from examples import blocking_cpu_task


#
logger = setup_logger()


# ── Events ─────────────────────────────────────────────────────────────

@dataclass
class ExportRequest:
    """Payload emitted by the ViewModel when a PDF export is ready to proceed."""
    default_filename: str
    default_dir: str
    



class DSClinicViewModel:

    def __init__(self,
                 schedule_poll_fn: callable[[int, callable], Any], 
                 model: Optional[MedicalReport] = None
                 ) -> None:
        # Assign arguments to local variables
        self.schedule_poll_fn = schedule_poll_fn
        # Make default / empty model if not provided
        self._model: MedicalReport = model or MedicalReport()

        # --- Report data ---
        self.var_patient_name = tk.StringVar(value=self._model.content.patient_name)
        self.var_report_date = tk.StringVar(value=self._model.report_date) 
         # Handled manually for Text widgets
        self.therapy_text_content = self._model.content.recommended_therapy_and_advice 
        self.findings: list[MedicalCriticalFindingModel] = self._model.content.critical_findings

        # Chat session (TODO: get rid of these)
        self.var_initial_question = tk.StringVar(value="")
        self.var_response = tk.StringVar(value="")

        # Analysis Status & Progress
        self.var_status_title = tk.StringVar(value="IDLE")
        self.var_status_detail = tk.StringVar(value="Ready")
        self.var_progress_value = tk.DoubleVar(value=0.0)
        self.var_is_analyzing = tk.BooleanVar(value=False)
        self.var_btn_analyze_text = tk.StringVar(value="Analyze")

        # Threading
        self._output_queue: queue.Queue[ProgressEvent] = queue.Queue()
        self._cancel_event: threading.Event = threading.Event()
        self._worker_thread: threading.Thread | None = None
        
        # Events (View subscribes to these)
        self.on_vm_data_changed: EventEmitter = EventEmitter()  # emits no payload, just a signal that "data changed, update view"
        self.on_show_error_message: EventEmitter = EventEmitter() # emits ErrorMessageEvent
        self.on_export_requested: EventEmitter = EventEmitter()  # emits ExportRequest
        self.on_export_succeeded: EventEmitter = EventEmitter()  # emits output_filepath: str
        
        # Main DSClinic App Logic Handler
        self.dsclinicapp = DSClinic(model_name=config.AI_MODEL_NAME)


    def _update_viewmodel_from_model(self):
        logger.debug("Updating ViewModel from Model...")
        # Sync Model to Observables
        self.therapy_text_content = self._model.content.recommended_therapy_and_advice
        self.findings = self._model.content.critical_findings
        self.var_patient_name.set(self._model.content.patient_name)
        self.var_report_date.set(self._model.report_date)

        #self.app.event_generate("<<VM_DataChanged>>")
        
    def _update_model_from_viewmodel(self):
        logger.debug("Updating Model from ViewModel...")
        # Sync Observables to Model
        self._model.content.patient_name = self.var_patient_name.get()
        self._model.report_date = self.var_report_date.get()
        self._model.content.recommended_therapy_and_advice = self.therapy_text_content
        self._model.content.critical_findings = self.findings


    # --- Logic: Data Management ---

    def add_finding(self):
        """Adds a blank finding to the list."""
        logger.debug("Adding new finding...")
        self.findings.append(MedicalCriticalFindingModel())
        #self._update_viewmodel_from_model()
        #self.app.event_generate("<<VM_DataChanged>>")
        
    def remove_finding(self, index: int):
        """Removes a finding at the specified index."""
        logger.debug(f"Removing finding at index {index}...")
        if 0 <= index < len(self.findings):
            self.findings.pop(index)

    # --- Logic: Analysis ---

    def toggle_analysis(self):
        if not self.var_is_analyzing.get():
            self._start_analysis()
        else:
            self._cancel_analysis()

    def _start_analysis(self):
        self.var_is_analyzing.set(True)
        self.var_btn_analyze_text.set("Cancel")
        self.var_status_title.set("Running")
        self.var_status_detail.set("Running heavy task...")
        self.var_progress_value.set(0)
        self._cancel_event.clear()

        self._worker_thread = threading.Thread(
            target=self._run_task_initial_analyzis,
            args=( self._output_queue, self._cancel_event),
            daemon=True,
            name="dsclinic-gemini-thread")
        
        self._worker_thread.start()
        # Kick off the polling loop. The ViewModel owns this entirely —
        # no external dispatcher needed.
        self.schedule_poll_fn(QUEUE_POLL_INTERVAL_MS, self._poll_result_queue)

    def _reset_task_state(self) -> None:
        self._cancel_event.clear()
        self._output_queue = queue.Queue()
        self.var_is_analyzing.set(False)
        self.var_status_title.set("Cancelling")
        self.var_status_detail.set("Cancelling analysis...")
        
    def _cancel_analysis(self):
        self._reset_task_state()
        self._cancel_event.set()

    def _run_task_initial_analyzis(self, output_queue: queue.Queue[ProgressEvent], cancel_event: threading.Event):
        try:
            report: MedicalReport = self.dsclinicapp.get_initial_analysis_report()
            output_queue.put(ProgressEvent(status=TaskStatus.FINISHED, message="Analysis complete", result=report))
        except Exception as e:
            logger.critical(f"Error during analysis: {str(e)}", exc_info=True)
            output_queue.put(ProgressEvent(
                status=TaskStatus.FAILED,
                message="Task failed",
                result=str(e)
            ))

    def followup_question_submit(self):
        question = self.var_initial_question.get()
        logger.debug(f"Follow-up question submitted: {question}")
        self.var_initial_question.set("")
        answer = self.dsclinicapp.ask_followup_question(question)
        self.var_response.set(answer)


    def _poll_result_queue(self) -> None:
        """Drain the queue and update observable state.  Scheduled via `after`."""
        task_still_running = True
 
        try:
            while True:
                progress_event: ProgressEvent = self._output_queue.get_nowait()
                task_still_running = self._apply_progress_event(progress_event)
        except queue.Empty:
            pass
 
        if task_still_running:
            self.schedule_poll_fn(QUEUE_POLL_INTERVAL_MS, self._poll_result_queue)
 
    def _apply_progress_event(self, progress_event: ProgressEvent) -> bool:
        """Apply one ProgressEvent to observable vars.
 
        Returns:
            True  → task is still running; keep polling.
            False → task has ended; stop polling.
        """
        logger.debug(f"Applying ProgressEvent: {progress_event}")
        match progress_event.status:
            case TaskStatus.RUNNING:
                self.var_status_title.set("Starting analysis...")
                self.var_status_detail.set(f"Task: {progress_event.message}")
                self.var_progress_value.set(0)  # Example: progress based on elapsed time
                #
                return True
            
            case TaskStatus.PROGRESS:
                self.var_status_title.set("Analyzing...")
                self.var_status_detail.set(f"progress: {progress_event.message}, elapsed_seconds: {progress_event.elapsed_seconds}")
                self.var_progress_value.set((progress_event.elapsed_seconds / 10) * 100)  # Example: progress based on elapsed time
                #
                return True
 
            case TaskStatus.FINISHED:            
                # Update Model and Notify View (by updating observables)
                if progress_event.result and isinstance(progress_event.result, MedicalReport):
                    logger.info("Analysis completed with a MedicalReport result. Updating model and viewmodel...")
                    # Update the ViewModel's model with the new report
                    self._model = progress_event.result
                    self._update_viewmodel_from_model()
                    
                    # Update status vars BEFORE emitting data change to ensure View sees the unlocked state
                    self.var_progress_value.set(100)
                    self.var_status_detail.set("Analysis completed successfully.")
                    self.var_is_analyzing.set(False)
                    self.var_btn_analyze_text.set("Analyze")

                    self.on_vm_data_changed.emit()  # Notify the view to refresh based on new data
                else:
                    # This shouldn't happen - if the task finished successfully, we expect a MedicalReport result. Log an error if not.
                    error_msg = f"Unexpected result type in ProgressEvent: {type(progress_event.result)}. Expected MedicalReport. Details: {progress_event.result}"
                    logger.error(error_msg)
                    self.show_error_message("Error", error_msg)
                    self.var_status_title.set("Finished")
                    self.var_progress_value.set(50)
                    self.var_status_detail.set(f"Analysis Failed with error: 'Unexpected result type. Results={progress_event.result}'.")
                    self.var_is_analyzing.set(False)
                    self.var_btn_analyze_text.set("Analyze")
                #
                return False
            case TaskStatus.CANCELED:
                self.var_is_analyzing.set(False)
                self.var_status_title.set("Cancelled")
                self.var_status_detail.set(f"✖ " + progress_event.message)            
                #
                return False
            case TaskStatus.FAILED:
                # Reset ViewModel state
                self.var_is_analyzing.set(False)
                self.var_btn_analyze_text.set("Analyze")
                # Set Status
                error_msg = f"Analysis failed with error: {progress_event.result}"
                logger.error(error_msg)
                self.var_status_title.set("Failed")
                self.var_status_detail.set("✖ " + progress_event.message)
                self.on_show_error_message.emit(ErrorMessageEvent(
                    title="Analysis Failed", 
                    message=error_msg if error_msg else "An unknown error occurred during analysis."))
                #            
                return False
            case _:
                error_msg = f"Received ProgressEvent with unknown status: {progress_event.status}"
                logger.error(error_msg)
                self.on_show_error_message.emit(ErrorMessageEvent(
                    title="Error", 
                    message=error_msg))
                #
                return True
            
    # Logic: View Updates
    
    def update_view_from_viewmodel(self):
        logger.debug("Updating View from ViewModel...")
        self.on_vm_data_changed.emit()
            
    # Logic: Error Handling
            
    def show_error_message(self, title: str, message: str) -> None:
        logger.debug(f"Emitting error message: {title} - {message}")
        self.on_show_error_message.emit(ErrorMessageEvent(title=title, message=message))
        
    # Logic: Export        
    
    def prepare_export(self) -> None:
        """
        Step 1 of the export flow (ViewModel side).
        Syncs observables → model, builds a suggested filename + output dir,
        then fires on_export_requested so the View can show the file dialog.
        The ViewModel never touches filedialog or messagebox.
        """
        self._update_model_from_viewmodel()

        patient_slug = self.var_patient_name.get().replace(".", " ").replace("/", "")
        timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        default_name = f"NALAZ_{patient_slug}_{timestamp_str}.pdf"
        output_dir = utils.get_output_data_dirpath()

        self.on_export_requested.emit(ExportRequest(
            default_filename=default_name,
            default_dir=output_dir,
        ))

    def execute_export(self, output_filepath: str) -> None:
        """
        Step 2 of the export flow (ViewModel side).
        Called by the View after the user confirms a filepath in the dialog.
        Performs the actual PDF generation and updates status observables.
        Raises on failure so the View can show an appropriate error dialog.
        """
        self.var_status_title.set("Exporting")
        self.var_status_detail.set(f"Generating PDF at {output_filepath}...")

        generate_report_pdf_at_filepath(self._model, output_filename=output_filepath)

        self.var_status_title.set("Saved")
        self.var_status_detail.set("PDF Saved Successfully")
        self.on_export_succeeded.emit(output_filepath)
