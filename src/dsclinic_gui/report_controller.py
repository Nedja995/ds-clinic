import datetime
import os
import threading
import queue
import time
import tkinter as tk
from tkinter import filedialog
import tkinter.messagebox
from logger import setup_logger
from models import MedicalReportModel, MedicalCriticalFindingModel
from dsclinic import process_documents
from pdf_maker import export_medical_report_pdf
from dsclinic_gui.report_view import DSClinicView
from dsclinic_gui.widgets.dialogs import CustomMessageBox
import utils


logger = setup_logger()

class DSClinicController:
    def __init__(self, root: tk.Tk, model: MedicalReportModel, view: DSClinicView):
        self.root = root
        #self.root.withdraw()
        self.model: MedicalReportModel = model
        self.view: DSClinicView = view
        
        # 1. Threading Control
        self.output_queue = queue.Queue()
        self.stop_event = threading.Event()  # The "Cancel" Signal
        self.worker_thread = None

        self._bind_events()
        self._initialize_view()

        # Start the polling loop
        self.check_queue()

    def _bind_events(self):
        self.view.btn_analyze.config(command=self._handle_analyze_click)
        self.view.btn_submit.config(command=self._handle_export_click)
        self.view.btn_settings.config(command=self._handle_settings_click)
        self.view.btn_dodaj_nalaz.config(command=self.view.add_finding_row)

    def _initialize_view(self):
        data: MedicalReportModel = self.model
        if data:
            self.view.set_display_data(data)
        else:
            self.view.add_finding_row()

    def _handle_analyze_click(self):
        if self.view.var_btn_analyze.get() == "Analyze":
            self.view.var_btn_analyze.set("Cancel")
            #self.view.btn_analyze.config(text="Cancel")
            process_config_str = f"Analiziraj dokumente: 'Presek glave.pdf', 'Lab.pdf'. Task: 'Analiziraj i ukazi na kriticne simptome.'. Model: 'gemini-3-pro'."
            logger.info(process_config_str)
            self.view.update_status("Analysing", process_config_str)
            self.start_task()
            #self.view.btn_full_report.config(state="normal")
        else:
            self.view.var_btn_analyze.set("Analyze")
            #self.view.btn_analyze.config(text="POKRENI ANALIZU")
            logger.info("Analiza je prekinuta.")
            self.view.update_status("IDLE", "Analiza je prekinuta")
            self.view.btn_full_report.config(state="disabled")
            self.cancel_task()

    def _handle_export_click(self):
        data: MedicalReportModel = self.view.get_user_input()
        self.model = data
        
        logger.info("Clicked: Export to PDF")
        logger.debug("Collected data:")
        logger.debug(data)

        patient_name = data.patient_name.replace(".", " ").replace("/", "")
        timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        output_filename = f"NALAZ_{patient_name}_{timestamp_str}.pdf"
        
        output_dir = utils.get_output_data_dirpath()
        os.makedirs(output_dir, exist_ok=True)

        #output_filepath = os.path.join(output_dir, output_filename)
        output_filepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")], initialdir=output_dir, initialfile=output_filename)
        logger.debug(f"User choosed output filepath: '{output_filepath}'.")
        if not output_filepath: # User cancelled the save dialog
            logger.info("Report export cancelled by user.")
            return
        self.view.update_status("Exporting report", f"Generating PDF at filepath: '{output_filepath}'...")

        try:
            export_medical_report_pdf(data, output_filename=output_filepath)
            self.view.update_status("Izvestaj sacuvan", f"PDF izvestaj je uspesno sacuvan na putanji: '{output_filepath}'.")
            #tkinter.messagebox.showinfo("Uspeh", "Medicinski izveštaj je uspešno generisan.")
            msgBox = CustomMessageBox(self.root, 
                                      "Izveštaj je uspešno generisan", 
                                      "Da li želite da otvorite izveštaj?", 
                                      button_texts=["Da", "Ne", "Otvori fasciklu"]
                                      )
            if msgBox.choice == "Da":
                logger.info("Opening report...")
                utils.open_file_from_filepath(output_filepath)
            elif msgBox.choice == "Ne":
                logger.info("Not opening report...")
            elif msgBox.choice == "Otvori fasciklu":
                logger.info("Opening report directory...")
                utils.open_file_from_filepath(output_dir)
            else:
                logger.error(f"Unknown choice: {msgBox.choice}")
        except Exception as e:
            logger.exception(e)
            self.view.update_status("Export failed", "Generisanje PDF izveštaja nije uspelo. Proverite log za više detalja.")
            tkinter.messagebox.showerror("Greška", "Došlo je do greške prilikom generisanja PDF dokumenta.", detail=str(e))
            
    def _handle_settings_click(self):
        logger.debug(f"Kliknuto na: Podešavanja")
        self.view.update_status("Settings Open", "ADJUSTING SETTINGS...")

    def start_task(self):
        """Initializes and starts the background worker."""
        self.stop_event.clear() # Reset the cancel signal
        self.view.var_btn_analyze.set("Cancel")
        self.view.update_status("Running", "Running heavy task...")
        self.view.progress_bar['value'] = 0

        self.worker_thread = threading.Thread(target=self.heavy_work_logic, daemon=True)
        self.worker_thread.start()

    def cancel_task(self):
        """Sets the event to tell the thread to stop."""
        self.view.update_status("Cancelling", "Cancelling analysis...")
        self.view.var_btn_analyze.set("Analyze")
        self.stop_event.set()

    def heavy_work_logic(self):
        """The worker loop that respects the stop_event."""
        for i in range(1, 101):
            # 2. THE CHECK: Does the UI want us to stop?
            if self.stop_event.is_set():
                self.output_queue.put({"status": "cancelled"})
                return # Exit the thread immediately

            time.sleep(0.05) # Simulate work
            
            # Periodic Progress Update
            if i % 10 == 0:
                self.output_queue.put({"status": "processing", "result": f"{str(i)}"})
                self.root.after(0, lambda v=i: self.view.progress_bar.configure(value=v))

        # Task completed fully
        self.output_queue.put({"status": "complete", "result": "Success!"})

    def check_queue(self):
        """Listen for thread exit signals."""
        try:
            msg = self.output_queue.get_nowait()
            if msg["status"] == "cancelled":
                self.view.update_status("Cancelled", "Task was Cancelled.")
            elif msg["status"] == "complete":
                self.view.progress_bar['value'] = 100
                self.view.update_status("Analiza zavrsena", "Analiza je zavrsena.")
                self.view.var_btn_analyze.set("Analyze")
            elif msg["status"] == "processing":
                #self.view.progress_bar['value'] = int(msg["result"])
                self.view.update_status("Analysing", f"Processing step {msg['result']}%")
            else:
                self.view.update_status("Finished", f"Finished: {msg['result']}")
                self.view.var_btn_analyze.set("Analyze")
            
            #self.view.var_btn_analyze.set("Analyze")
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.check_queue)