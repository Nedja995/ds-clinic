from operator import index
import threading
import queue
import time
import tkinter as tk
import os
import datetime
from typing import Optional, Any
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

class DSClinicViewModel:
    def __init__(self, model: Optional[MedicalReport] = None) -> None:
        self._model: MedicalReport = model or MedicalReport()

        # --- Observable UI State ---
        self.var_patient_name = tk.StringVar(value=self._model.content.patient_name)
        self.var_report_date = tk.StringVar(value=self._model.report_date) 
        self.therapy_text_content = self._model.content.recommended_therapy_and_advice  # Handled manually for Text widgets
        
        self.findings: list[MedicalCriticalFindingModel] = self._model.content.critical_findings

        self.var_initial_question = tk.StringVar(value="")
        self.var_response = tk.StringVar(value="")

        # Status & Progress
        self.var_status_title = tk.StringVar(value="IDLE")
        self.var_status_detail = tk.StringVar(value="Ready")
        self.var_progress_value = tk.DoubleVar(value=0.0)
        self.var_is_analyzing = tk.BooleanVar(value=False)
        self.var_btn_analyze_text = tk.StringVar(value="Analyze")

        # Threading
        self._output_queue: queue.Queue = queue.Queue()
        self._cancel_event: threading.Event = threading.Event()
        self._worker_thread: threading.Thread | None = None

        # Start polling for async tasks
        #self._check_queue_loop()


    def _update_viewmodel_from_model(self):
        logger.debug("Updating ViewModel from Model...")
        self.var_patient_name.set(self._model.content.patient_name)
        self.var_report_date.set(self._model.report_date)
        self.therapy_text_content = self._model.content.recommended_therapy_and_advice
        self.findings = self._model.content.critical_findings
        
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
            #self._update_viewmodel_from_model()
            #self.app.event_generate("<<VM_DataChanged>>")

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

        self._worker_thread = threading.Thread(target=self._run_task_initial_analyzis,
                                               daemon=True)
        self._worker_thread.start()

    def _cancel_analysis(self):
        self.var_status_title.set("Cancelling")
        self.var_status_detail.set("Cancelling analysis...")
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
            self._output_queue.put({"status": "complete", "result": self._model.model_dump(mode='json')})
        except Exception as e:
            logger.critical(f"Error during analysis: {str(e)}", exc_info=True)
            self._output_queue.put({"status": "failed", "result": str(e)})
            

    def _check_queue_loop(self):
        pass
        return
        try:
            msg = self._output_queue.get_nowait()
            progress = 0

            # self._update_view(event_status=msg["status"],
            #     status_detail=msg["result"],
            #     result=msg["result"])
            logger.debug(f"Received message from worker thread: {msg}")
            if msg["status"] == "cancelled":
                self.var_status_title.set("Cancelled")
                self.var_status_detail.set("Analysis was Cancelled.")
            elif msg["status"] == "complete":
                self.var_is_analyzing.set(False)
                self.var_btn_analyze_text.set("Analyze")
                self.var_progress_value.set(100)
                self.var_status_title.set("Finished")
                self.var_status_detail.set("Analysis completed successfully.")

                # Update Model and Notify View (by updating observables)
                new_report = MedicalReport(**msg["result"])
                self._model = new_report
                self._update_viewmodel_from_model()
            elif msg["status"] == "processing":
                self.var_status_title.set("Processing...")

                self.var_status_detail.set(f"status: {msg['status']}, result: {msg['result']}")
            elif msg["status"] == "failed":
                self.var_is_analyzing.set(False)
                self.var_btn_analyze_text.set("Analyze")
                self.var_status_title.set("Failed")
                self.var_status_detail.set(msg["result"])
            else:
                self.var_status_title.set("Finished")
                self.var_status_detail.set(f"status: {msg['status']}, result: {msg['result']}")
                self.var_progress_value.set(100)
                self.var_btn_analyze_text.set("Analyze")
        except queue.Empty:
            pass
        finally:
            pass
            #self.app.after(QUEUE_POLL_INTERVAL_MS, self._check_queue_loop)

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
            self.var_status_title.set(event_status)
        if status_detail:
            self.var_status_detail.set(status_detail)
        if is_analyzing:
            self.var_is_analyzing.set(is_analyzing)
        if progress:
            self.var_progress_value.set(progress)
        if btn_analyze_text:
            self.var_btn_analyze_text.set(btn_analyze_text)
        if event_status == "complete" and result and isinstance(result, MedicalReportModel):
            self._model.content = result
            self._update_viewmodel_from_model()
            
    def save_report(self):
        """Handles PDF Export logic."""
        # Note: The View must have already synced its ScrolledText data to VM before calling this.
        ls = self._model.content.critical_findings
        # 1. Sync Observables to Model
        self._update_model_from_viewmodel()

        # 2. Export
        patient_slug = self.var_patient_name.get().replace(".", " ").replace("/", "")
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

        self.var_status_title.set("Exporting")
        self.var_status_detail.set(f"Generating PDF at {output_filepath}...")

        try:
            export_medical_report_pdf(self._model, output_filename=output_filepath)
            self.var_status_title.set("Saved")
            self.var_status_detail.set("PDF Saved Successfully")

            if messagebox.askyesno("Success", "Report generated. Open file?"):
                fileutils.open_file_from_filepath(output_filepath)

        except Exception as e:
            logger.error(e)
            self.var_status_title.set("Error")
            self.var_status_detail.set("Failed to generate PDF")
            messagebox.showerror("Error", str(e))