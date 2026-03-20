import threading
import queue
import time
import tkinter as tk
import os
import datetime
from tkinter import filedialog, messagebox

from npy.core.logger import setup_logger
from npy.core import utils
import config
from models import MedicalReport, MedicalReportModel, MedicalCriticalFindingModel
from dsclinic import get_initial_analysis_report
from pdf_maker import export_medical_report_pdf

logger = setup_logger()

class DSClinicViewModel:
    def __init__(self, root: tk.Tk, model: MedicalReport):
        self.root = root
        self.model = model

        # --- Observable UI State ---
        self.patient_name = tk.StringVar(value=model.content.patient_name)
        self.report_date = tk.StringVar(value=model.report_date)
        self.therapy_text_content = model.content.recommended_therapy_and_advice # Handled manually for Text widgets
        
        self.findings: list[MedicalCriticalFindingModel] = model.content.critical_findings
        
        # Status & Progress
        self.status_title = tk.StringVar(value="IDLE")
        self.status_detail = tk.StringVar(value="Ready")
        self.progress_value = tk.DoubleVar(value=0.0)
        self.is_analyzing = tk.BooleanVar(value=False)
        self.btn_analyze_text = tk.StringVar(value="Analyze")

        # Threading
        self.output_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.worker_thread = None

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
        self.stop_event.clear()
        self.status_title.set("Running")
        self.status_detail.set("Running heavy task...")
        self.progress_value.set(0)
        
        self.worker_thread = threading.Thread(target=self._task_initial_analyzis, daemon=True)
        self.worker_thread.start()

    def _cancel_analysis(self):
        self.status_title.set("Cancelling")
        self.status_detail.set("Cancelling analysis...")
        self.stop_event.set()

    def _task_initial_analyzis(self):
        input_dir = utils.get_input_data_dirpath()
        try:
            report = get_initial_analysis_report(input_dir=input_dir,
                                                 model_name=config.AI_MODEL_NAME, 
                                                 debug_export_response=False,
                                                 debug_response=True)
            self.output_queue.put({"status": "complete", "data": report.model_dump()})
        except Exception as e:
            logger.critical(f"Error during analysis: {str(e)}", exc_info=True)
            self.output_queue.put({"status": "failed", "result": str(e)})

    def _check_queue_loop(self):
        try:
            while True:
                msg = self.output_queue.get_nowait()
                if msg["status"] == "complete":
                    self.is_analyzing.set(False)
                    self.btn_analyze_text.set("Analyze")
                    self.progress_value.set(100)
                    self.status_title.set("Finished")
                    self.status_detail.set("Analysis completed successfully.")
                    
                    # Update Model and Notify View (by updating observables)
                    new_report = MedicalReportModel(**msg["data"])
                    self.model.content = new_report
                    self._update_vm_from_model()
                    
                    # Signal View to refresh complex widgets (rows, text)
                    self.root.event_generate("<<VM_DataChanged>>")
                    
                elif msg["status"] == "failed":
                    self.is_analyzing.set(False)
                    self.btn_analyze_text.set("Analyze")
                    self.status_title.set("Failed")
                    self.status_detail.set(msg["result"])
                
        except queue.Empty:
            pass
        finally:
            self.root.after(500, self._check_queue_loop)

    def _update_vm_from_model(self):
        self.patient_name.set(self.model.content.patient_name)
        self.report_date.set(self.model.report_date)
        self.therapy_text_content = self.model.content.recommended_therapy_and_advice
        self.findings = self.model.content.critical_findings

    # --- Logic: Data Management ---
    
    def add_finding(self):
        """Adds a blank finding to the list."""
        self.findings.append(MedicalCriticalFindingModel())
        self.root.event_generate("<<VM_DataChanged>>")

    def remove_finding(self, index: int):
        if 0 <= index < len(self.findings):
            self.findings.pop(index)
            self.root.event_generate("<<VM_DataChanged>>")

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
                utils.open_file_from_filepath(output_filepath)
                
        except Exception as e:
            logger.error(e)
            self.status_title.set("Error")
            self.status_detail.set("Failed to generate PDF")
            messagebox.showerror("Error", str(e))