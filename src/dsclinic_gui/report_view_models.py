import threading
import queue
import time
import tkinter as tk
import os
import datetime
from tkinter import filedialog, messagebox

from npy.core.logger import setup_logger
from npy.core import utils, fileutils
import config
from models import MedicalReport, MedicalReportModel, MedicalCriticalFindingModel, WorkerStatus
from dsclinic import get_initial_analysis_report
from pdf_maker import export_medical_report_pdf
from examples import blocking_cpu_task
#
logger = setup_logger()

#
QUEUE_POLL_INTERVAL_MS: int = 1000
logger.info(f"QUEUE_POLL_INTERVAL_MS: {QUEUE_POLL_INTERVAL_MS}")

##
#


class DSClinicViewModel:
    def __init__(self, app: tk.Tk, model: MedicalReport):
        self.app = app
        self.model = model

        # --- Observable UI State ---
        self.patient_name = tk.StringVar(value=model.content.patient_name)
        self.report_date = tk.StringVar(value=model.report_date)
        self.therapy_text_content = model.content.recommended_therapy_and_advice  # Handled manually for Text widgets

        self.findings: list[MedicalCriticalFindingModel] = model.content.critical_findings

        # Status & Progress
        self.status_title = tk.StringVar(value="IDLE")
        self.status_detail = tk.StringVar(value="Ready")
        self.progress_value = tk.DoubleVar(value=0.0)
        self.is_analyzing = tk.BooleanVar(value=False)
        self.btn_analyze_text = tk.StringVar(value="Analyze")

        # Threading
        self._output_queue: queue.Queue = queue.Queue()
        self._cancel_event: threading.Event = threading.Event()
        self._worker_thread: threading.Thread | None = None

        # Start polling for async tasks
        self._check_queue_loop()

    # --- Logic: Analysis ---

    def toggle_analysis(self):
        if not self.is_analyzing.get():
            self._start_analysis()
        else:
            self._cancel_analysis()

    def _start_analysis(self):
        self.is_analyzing.set(True)
        self.btn_analyze_text.set("Cancel")
        self.status_title.set("Running")
        self.status_detail.set("Running heavy task...")
        self.progress_value.set(0)
        self._cancel_event.clear()

        self._worker_thread = threading.Thread(target=self._run_task_initial_analyzis,
                                               daemon=True)
        self._worker_thread.start()

    def _cancel_analysis(self):
        self.status_title.set("Cancelling")
        self.status_detail.set("Cancelling analysis...")
        self._cancel_event.set()

    # def _run_task_initial_analyzis(self):
    #     input_dir = utils.get_input_data_dirpath()
    #     try:
    #         report: MedicalReport = get_initial_analysis_report(
    #             input_dir=input_dir,
    #             model_name=config.AI_MODEL_NAME)
    #         self._output_queue.put({"status": "complete", "result": report.model_dump(mode='json')})
    #     except Exception as e:
    #         logger.critical(f"Error during analysis: {str(e)}", exc_info=True)
    #         self._output_queue.put({"status": "failed", "result": str(e)})
    
    def _run_task_initial_analyzis(self):
        try:
            blocking_cpu_task(5)
            self._output_queue.put({"status": "complete", "result": self.model.model_dump(mode='json')})
        except Exception as e:
            logger.critical(f"Error during analysis: {str(e)}", exc_info=True)
            self._output_queue.put({"status": "failed", "result": str(e)})
            

    def _check_queue_loop(self):
        try:
            msg = self._output_queue.get_nowait()
            progress = 0

            # self._update_view(event_status=msg["status"],
            #     status_detail=msg["result"],
            #     result=msg["result"])
            logger.debug(f"Received message from worker thread: {msg}")
            if msg["status"] == "cancelled":
                self.status_title.set("Cancelled")
                self.status_detail.set("Analysis was Cancelled.")
            elif msg["status"] == "complete":
                self.is_analyzing.set(False)
                self.btn_analyze_text.set("Analyze")
                self.progress_value.set(100)
                self.status_title.set("Finished")
                self.status_detail.set("Analysis completed successfully.")

                # Update Model and Notify View (by updating observables)
                new_report = MedicalReport(**msg["result"])
                self.model = new_report
                self._update_vm_from_model()
            elif msg["status"] == "processing":
                self.status_title.set("Processing...")

                self.status_detail.set(f"status: {msg['status']}, result: {msg['result']}")
            elif msg["status"] == "failed":
                self.is_analyzing.set(False)
                self.btn_analyze_text.set("Analyze")
                self.status_title.set("Failed")
                self.status_detail.set(msg["result"])
            else:
                self.status_title.set("Finished")
                self.status_detail.set(f"status: {msg['status']}, result: {msg['result']}")
                self.progress_value.set(100)
                self.btn_analyze_text.set("Analyze")
        except queue.Empty:
            pass
        finally:
            self.app.after(QUEUE_POLL_INTERVAL_MS, self._check_queue_loop)

    def _update_view(self,
                     event_status: str = None,
                     status_detail: str = None,
                     result: str | int | MedicalReport = None):
        #
        is_analyzing = [True if event_status == "cancelled" or event_status == "processing" or event_status == "failed" or event_status == "complete" else False]
        #
        btn_analyze_text = ["Analyze" if not is_analyzing else "Cancel"]
        #
        progress: int = [result if isinstance(result, int) else None]

        if event_status:
            self.status_title.set(event_status)
        if status_detail:
            self.status_detail.set(status_detail)
        if is_analyzing:
            self.is_analyzing.set(is_analyzing)
        if progress:
            self.progress_value.set(progress)
        if btn_analyze_text:
            self.btn_analyze_text.set(btn_analyze_text)
        if event_status == "complete" and result and isinstance(result, MedicalReportModel):
            self.model.content = result
            self._update_vm_from_model()

    def _update_vm_from_model(self):
        self.patient_name.set(self.model.content.patient_name)
        self.report_date.set(self.model.report_date)
        self.therapy_text_content = self.model.content.recommended_therapy_and_advice
        self.findings = self.model.content.critical_findings

    # --- Logic: Data Management ---

    def add_finding(self):
        """Adds a blank finding to the list."""
        self.findings.append(MedicalCriticalFindingModel())
        self._update_vm_from_model()
        self.app.event_generate("<<VM_DataChanged>>")
        
    def remove_finding(self, index: int):
        if 0 <= index < len(self.findings):
            self.findings.pop(index)
            self._update_vm_from_model()
            self.app.event_generate("<<VM_DataChanged>>")

    def save_report(self):
        """Handles PDF Export logic."""
        # Note: The View must have already synced its ScrolledText data to VM before calling this.

        # 1. Sync Observables to Model
        self.model.content.patient_name = self.patient_name.get()
        self.model.report_date = self.report_date.get()
        self.model.content.recommended_therapy_and_advice = self.therapy_text_content
        self.model.content.critical_findings = self.findings

        # 2. Export
        patient_slug = self.patient_name.get().replace(".", " ").replace("/", "")
        timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        default_name = f"NALAZ_{patient_slug}_{timestamp_str}.pdf"
        output_dir = utils.get_output_data_dirpath()

        output_filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialdir=output_dir,
            initialfile=default_name
        )

        if not output_filepath:
            return

        self.status_title.set("Exporting")
        self.status_detail.set(f"Generating PDF at {output_filepath}...")

        try:
            export_medical_report_pdf(self.model, output_filename=output_filepath)
            self.status_title.set("Saved")
            self.status_detail.set("PDF Saved Successfully")

            if messagebox.askyesno("Success", "Report generated. Open file?"):
                fileutils.open_file_from_filepath(output_filepath)

        except Exception as e:
            logger.error(e)
            self.status_title.set("Error")
            self.status_detail.set("Failed to generate PDF")
            messagebox.showerror("Error", str(e))
