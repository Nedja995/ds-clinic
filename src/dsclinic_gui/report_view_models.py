import threading
import queue
import tkinter as tk
import os
import datetime
from typing import Optional, Any, Callable
from dataclasses import dataclass
import multiprocessing

from dsclinic_gui.settings.settings_view_model import SettingsViewModel
from npy.core.logger import setup_logger
from npy.core import utils, fileutils
from models import app_settings, MedicalReport, MedicalReportModel, MedicalCriticalFindingModel, MedicalTherapyModel
from dsclinic import DSClinic
from pdf_maker import generate_report_pdf_at_filepath
from npy.core.event_emitter import EventEmitter, ErrorMessageEvent
from models import TaskStatus, ProgressEvent
from dsclinic_gui.constants import QUEUE_POLL_INTERVAL_MS

logger = setup_logger()


# ── Events ─────────────────────────────────────────────────────────────

@dataclass
class ExportRequest:
    """Payload emitted by the ViewModel when a PDF export is ready to proceed."""
    default_filename: str
    default_dir: str


class DSClinicViewModel:

    def __init__(
        self,
        schedule_poll_fn: Callable[[int, Callable[[], None]], Any],
        model: Optional[MedicalReport] = None,
    ) -> None:
        self.schedule_poll_fn = schedule_poll_fn
        self._model: MedicalReport = model or MedicalReport()

        # Handled manually for Text widgets
        self.therapy_text_content = self._model.content.recommended_therapy_and_advice
        self.findings: list[MedicalCriticalFindingModel] = self._model.content.critical_findings
        self.therapy_data: list[MedicalTherapyModel] = self._model.therapies

        # Observable data — Report
        self.var_patient_name = tk.StringVar(value=self._model.content.patient_name)
        self.var_report_date = tk.StringVar(value=self._model.report_date)
        self.var_input_dir = tk.StringVar(value=self._model.input_dir)

        # Chat session (TODO: get rid of these)
        self.var_initial_question = tk.StringVar(value="")
        self.var_response = tk.StringVar(value="")

        # Analysis Status & Progress
        self.var_status_title = tk.StringVar(value="IDLE")
        self.var_status_detail = tk.StringVar(value="Ready")
        self.var_progress_value = tk.DoubleVar(value=0.0)
        self.var_is_analyzing = tk.BooleanVar(value=False)
        self.var_btn_analyze_text = tk.StringVar(value=_("Analyze"))  # type: ignore[name-defined]

        # Threading
        self._output_queue: queue.Queue[ProgressEvent] = queue.Queue()
        self._cancel_event: threading.Event = threading.Event()
        self._worker_thread: threading.Thread | None = None

        # Events (View subscribes to these)
        self.on_vm_data_changed:    EventEmitter = EventEmitter()
        self.on_show_error_message: EventEmitter = EventEmitter()
        self.on_export_requested:   EventEmitter = EventEmitter()
        self.on_export_succeeded:   EventEmitter = EventEmitter()

        self.dsclinicapp = DSClinic(model_name=app_settings.ai_model_name)

    def _update_viewmodel_from_model(self) -> None:
        logger.debug("Updating ViewModel from Model...")
        self.therapy_text_content = self._model.content.recommended_therapy_and_advice
        self.findings             = self._model.content.critical_findings
        self.var_patient_name.set(self._model.content.patient_name)
        self.var_report_date.set(self._model.report_date)
        self.var_input_dir.set(self._model.input_dir)

    def _update_model_from_viewmodel(self) -> None:
        logger.debug("Updating Model from ViewModel...")
        self._model.content.patient_name                   = self.var_patient_name.get()
        self._model.report_date                            = self.var_report_date.get()
        self._model.input_dir                              = self.var_input_dir.get()
        self._model.content.recommended_therapy_and_advice = self.therapy_text_content
        self._model.content.critical_findings              = self.findings
        self._model.therapies                              = self.therapy_data

    # --- Logic: Data Management ---

    def add_finding(self) -> None:
        """Adds a blank finding to the list."""
        logger.debug("Adding new finding...")
        self.findings.append(MedicalCriticalFindingModel())

    def remove_finding(self, index: int) -> None:
        """Removes a finding at the specified index."""
        logger.debug(f"Removing finding at index {index}...")
        if 0 <= index < len(self.findings):
            self.findings.pop(index)

    def add_therapy(self) -> None:
        """Adds a blank therapy to the list."""
        logger.debug("Adding new therapy...")
        self.therapy_data.append(MedicalTherapyModel())

    def remove_therapy(self, index: int) -> None:
        """Removes a therapy at the specified index."""
        logger.debug(f"Removing therapy at index {index}...")
        if 0 <= index < len(self.therapy_data):
            self.therapy_data.pop(index)

    # --- Logic: Chat ---

    def append_chat_response(self, text: str) -> None:
        """Appends a bot response string to the model's chat history.
        Called by the View after rendering a bot bubble — the View must never
        mutate self._model directly.
        """
        self._model.chat_responses.append(text)

    # --- Logic: Analysis ---

    def toggle_analysis(self) -> None:
        """Toggles the analysis process."""
        if not self.var_is_analyzing.get():
            self._start_analysis()
        else:
            self._cancel_analysis()

    def _reset_task_state(self) -> None:
        """Resets ViewModel state for an ongoing task."""
        self._cancel_event.clear()
        self._output_queue = queue.Queue()
        self.var_is_analyzing.set(False)
        self.var_status_title.set("Cancelling")
        self.var_status_detail.set("Cancelling analysis...")

    def _start_analysis(self) -> None:
        """Starts analysis in a background thread."""
        self.var_is_analyzing.set(True)
        self.var_btn_analyze_text.set("Cancel")
        self.var_status_title.set("Running")
        self.var_status_detail.set("Running heavy task...")
        self.var_progress_value.set(0)
        self._cancel_event.clear()

        self._worker_thread = threading.Thread(
            target=self._run_task_initial_analyzis,
            args=(self._output_queue, self._cancel_event),
            daemon=True,
            name="dsclinic-gemini-thread",
        )
        self._worker_thread.start()
        self.schedule_poll_fn(QUEUE_POLL_INTERVAL_MS, self._poll_result_queue)

    def _cancel_analysis(self) -> None:
        self._reset_task_state()
        self._cancel_event.set()

    def _run_task_initial_analyzis(
        self,
        output_queue: queue.Queue[ProgressEvent],
        cancel_event: threading.Event,
    ) -> None:
        try:
            output_queue.put(ProgressEvent(status=TaskStatus.RUNNING, message="Finding local medical files..."))

            input_dir = self.var_input_dir.get()
            from npy.core.fileutils import find_input_documents
            documents_filepaths = find_input_documents(input_dir)

            scrubbed_files_map: dict[str, str] = {}
            anonymization_enabled = app_settings.anonymization_on

            if documents_filepaths and anonymization_enabled:
                output_queue.put(ProgressEvent(status=TaskStatus.RUNNING, message="Initializing local privacy layers..."))

                mp_input_queue: multiprocessing.Queue[Any] = multiprocessing.Queue()
                mp_output_queue: multiprocessing.Queue[Any] = multiprocessing.Queue()

                from dsclinic_gui.redaction_worker import redaction_worker_process
                worker = multiprocessing.Process(
                    target=redaction_worker_process,
                    args=(mp_input_queue, mp_output_queue),
                    daemon=True,
                )
                worker.start()

                for doc_path in documents_filepaths:
                    parent_dir = os.path.dirname(doc_path)
                    filename = os.path.basename(doc_path)
                    base, ext = os.path.splitext(filename)

                    anonymized_subfolder = os.path.join(parent_dir, "ANONIMIZOVANO")
                    if not os.path.exists(anonymized_subfolder):
                        os.makedirs(anonymized_subfolder, exist_ok=True)
                        logger.info(f"Created dedicated debug subfolder: {anonymized_subfolder}")

                    scrubbed_path = os.path.join(anonymized_subfolder, f"{base}_scrubbed{ext}")
                    scrubbed_files_map[doc_path] = scrubbed_path
                    mp_input_queue.put({"input_path": doc_path, "output_path": scrubbed_path})

                files_processed = 0
                scrubbed_text_data_list: list[str] = []

                while files_processed < len(documents_filepaths) and not cancel_event.is_set():
                    try:
                        process_result = mp_output_queue.get(timeout=0.2)

                        if process_result.get("status") == "DOWNLOADING_MODELS":
                            download_msg = process_result.get("message")
                            output_queue.put(ProgressEvent(status=TaskStatus.RUNNING, message=download_msg))
                            continue

                        if process_result.get("status") == "ERROR":
                            raise Exception(f"Local Scrub Failure: {process_result.get('error_message')}")

                        if process_result.get("status") == "SUCCESS":
                            if "sanitized_text" in process_result:
                                scrubbed_text_data_list.append(process_result["sanitized_text"])
                            files_processed += 1
                            output_queue.put(ProgressEvent(
                                status=TaskStatus.RUNNING,
                                message=f"Locally scrubbed {files_processed}/{len(documents_filepaths)} files...",
                            ))

                    except queue.Empty:
                        continue

                mp_input_queue.put(None)
                worker.join()

            elif documents_filepaths and not anonymization_enabled:
                logger.info("Local anonymization is disabled. Bypassing scrub pipeline.")
                output_queue.put(ProgressEvent(status=TaskStatus.RUNNING, message="Bypassing local data obfuscation layer..."))

            if cancel_event.is_set():
                output_queue.put(ProgressEvent(status=TaskStatus.CANCELED, message="Analysis cancelled."))
                return

            output_queue.put(ProgressEvent(
                status=TaskStatus.PROGRESS,
                message="Sending safely anonymized data to Gemini...",
                elapsed_seconds=2,
            ))

            report: MedicalReport = self.dsclinicapp.get_initial_analysis_report(
                scrubbed_files_map=scrubbed_files_map
            )
            output_queue.put(ProgressEvent(status=TaskStatus.FINISHED, message="Analysis complete", result=report))

        except Exception as e:
            logger.critical(f"Error during analysis: {str(e)}", exc_info=True)
            output_queue.put(ProgressEvent(status=TaskStatus.FAILED, message="Task failed", result=str(e)))

    def followup_question_submit(self) -> None:
        logger.debug("Submitting followup question...")
        question = self.var_initial_question.get().strip()
        if not question or self.var_is_analyzing.get():
            return

        logger.debug(f"Follow-up question submitted: {question}")
        self.var_initial_question.set("")
        self.var_is_analyzing.set(True)
        self.var_status_title.set("Chatting")
        self.var_status_detail.set("Waiting for AI response...")
        self.var_progress_value.set(0)

        self._worker_thread = threading.Thread(
            target=self._run_task_followup_question,
            args=(question, self._output_queue),
            daemon=True,
            name="dsclinic-chat-thread",
        )
        self._worker_thread.start()
        self.schedule_poll_fn(QUEUE_POLL_INTERVAL_MS, self._poll_result_queue)

    def _run_task_followup_question(
        self, question: str, output_queue: queue.Queue[ProgressEvent]
    ) -> None:
        try:
            answer = self.dsclinicapp.ask_followup_question(question)
            output_queue.put(ProgressEvent(status=TaskStatus.FINISHED, result=answer))
        except Exception as e:
            logger.error(f"Error in chat followup: {e}", exc_info=True)
            output_queue.put(ProgressEvent(status=TaskStatus.FAILED, message=str(e), result=str(e)))

    def _poll_result_queue(self) -> None:
        """Drain the queue and update observable state. Scheduled via `after`."""
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
                self.var_progress_value.set(0)
                return True

            case TaskStatus.PROGRESS:
                self.var_status_title.set("Analyzing...")
                self.var_status_detail.set(
                    f"progress: {progress_event.message}, elapsed_seconds: {progress_event.elapsed_seconds}"
                )
                self.var_progress_value.set((progress_event.elapsed_seconds / 10) * 100)
                return True

            case TaskStatus.FINISHED:
                if progress_event.result and isinstance(progress_event.result, MedicalReport):
                    logger.info("Analysis completed with a MedicalReport result.")
                    self._model = progress_event.result
                    self._update_viewmodel_from_model()
                    self.var_progress_value.set(100)
                    self.var_status_detail.set("Analysis completed successfully.")
                    self.var_is_analyzing.set(False)
                    self.var_btn_analyze_text.set(_("Analyze"))  # type: ignore[name-defined]
                    self.on_vm_data_changed.emit()
                elif isinstance(progress_event.result, str):
                    self.var_response.set(progress_event.result)
                    self.var_is_analyzing.set(False)
                    self.var_status_title.set("Ready")
                    self.var_status_detail.set("Chat response received.")
                    self.var_progress_value.set(100)
                else:
                    error_msg = (
                        f"Unexpected result type in ProgressEvent: "
                        f"{type(progress_event.result)}. Expected MedicalReport."
                    )
                    logger.error(error_msg)
                    self.show_error_message("Error", error_msg)
                    self.var_status_title.set("Finished")
                    self.var_progress_value.set(50)
                    self.var_status_detail.set("Analysis Failed with error: 'Unexpected result type.'")
                    self.var_is_analyzing.set(False)
                    self.var_btn_analyze_text.set(_("Analyze"))  # type: ignore[name-defined]
                return False

            case TaskStatus.CANCELED:
                self.var_is_analyzing.set(False)
                self.var_status_title.set("Cancelled")
                self.var_status_detail.set("✖ " + progress_event.message)
                return False

            case TaskStatus.FAILED:
                self.var_is_analyzing.set(False)
                self.var_btn_analyze_text.set(_("Analyze"))  # type: ignore[name-defined]
                error_msg = f"Analysis failed with error: {progress_event.result}"
                logger.error(error_msg)
                self.var_status_title.set("Failed")
                self.var_status_detail.set("✖ " + progress_event.message)
                self.on_show_error_message.emit(ErrorMessageEvent(
                    title="Analysis Failed",
                    message=error_msg if error_msg else "An unknown error occurred during analysis.",
                ))
                return False

            case _:
                error_msg = f"Received ProgressEvent with unknown status: {progress_event.status}"
                logger.error(error_msg)
                self.on_show_error_message.emit(ErrorMessageEvent(title="Error", message=error_msg))
                return True

    # Logic: View Updates

    def update_view_from_viewmodel(self) -> None:
        logger.debug("Updating View from ViewModel...")
        self.on_vm_data_changed.emit()

    # Logic: Error Handling

    def show_error_message(self, title: str, message: str) -> None:
        logger.debug(f"Emitting error message: {title} - {message}")
        self.on_show_error_message.emit(ErrorMessageEvent(title=title, message=message))

    # Logic: Export

    def prepare_export(self) -> None:
        """Step 1 of the export flow — emits ExportRequest so View shows file dialog."""
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
        """Step 2 of the export flow — generates PDF, emits error on failure."""
        self.var_status_title.set("Exporting")
        self.var_status_detail.set(f"Generating PDF at {output_filepath}...")

        try:
            generate_report_pdf_at_filepath(self._model, output_filename=output_filepath)
        except Exception as e:
            error_msg = f"PDF export failed: {e}"
            logger.error(error_msg, exc_info=True)
            self.var_status_title.set("Export Failed")
            self.var_status_detail.set("✖ PDF generation error.")
            self.on_show_error_message.emit(ErrorMessageEvent(
                title="Export Failed",
                message=error_msg,
            ))
            return

        self.var_status_title.set("Saved")
        self.var_status_detail.set("PDF Saved Successfully")
        self.on_export_succeeded.emit(output_filepath)
