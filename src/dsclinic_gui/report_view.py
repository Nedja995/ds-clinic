import tkinter as tk
from tkinter import ttk, scrolledtext
from logger import setup_logger
from models import MedicalReportModel, MedicalCriticalFindingModel


logger = setup_logger()


class DSClinicView:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("DS Clinic Analiza")
        self.root.minsize(600, 500)
        # Set centered window
        window_width = 950
        window_height = 800
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_cordinate = int((screen_width/2) - (window_width/2))
        y_cordinate = int((screen_height/2) - (window_height/2))
        self.root.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

        self.nalazi_rows = []

        self.s = ttk.Style()
        self.s.configure('DebugRed.TFrame', background="#FF000008")
        self.s.configure('DebugGreen.TFrame', background="#00FF000E")
        self.s.configure('DebugBlue.TFrame', background="#0000FF11")
        self.s.configure('DebugYellow.TFrame', background="#FFFF000E")
        
        self._setup_ui()

    def _setup_ui(self):
        # 1. TOP TOOLBAR
        self.top_frame = ttk.Frame(self.root)
        self.top_frame.pack(side="top", fill="x", padx=2, pady=2)

        ttk.Separator(self.top_frame, orient='horizontal').pack(fill='x', pady=2, side=tk.BOTTOM)

        self.var_btn_analyze = tk.StringVar(value="Analyze")
        self.btn_analyze = ttk.Button(self.top_frame, textvariable=self.var_btn_analyze)
        self.btn_analyze.pack(side="left", padx=(0, 2))
        
        self.btn_submit = ttk.Button(self.top_frame, text="Export", state="enabled")
        self.btn_submit.pack(side="left", padx=2)

        self.btn_full_report = ttk.Button(self.top_frame, text="Details", state="disabled")
        self.btn_full_report.pack(side="left", padx=2)

        self.btn_settings = ttk.Button(self.top_frame, text="Settings")
        self.btn_settings.pack(side="left", padx=2)
        
        # 2. FOOTER
        self.footer_frame = ttk.Frame(self.root)
        self.footer_frame.pack(side="bottom", fill="x")

        ttk.Separator(self.footer_frame, orient='horizontal').pack(fill='x', pady=0, side=tk.TOP)

        progress_bar_frame = ttk.Frame(self.footer_frame, height=15) 
        progress_bar_frame.pack(expand=False, fill='x', side=tk.TOP, padx=2, pady=0)
        progress_bar_frame.pack_propagate(False) # Prevents the frame from resizing to fit the progressbar
        self.progress_bar = ttk.Progressbar(progress_bar_frame, mode='determinate', value=25)
        self.progress_bar.pack(fill="x", padx=0, pady=0)

        self.lbl_footer_status = tk.Label(self.footer_frame, text="STATUS:", font=("Arial", 10, "bold"), fg="red")
        self.lbl_footer_status.pack(side="left", padx=(5, 0), pady=0)

        self.var_status = tk.StringVar(value="Idle")
        self.lbl_status_details = tk.Label(self.footer_frame, textvariable=self.var_status, font=("Arial", 10, "normal"), fg="black", anchor="w")
        self.lbl_status_details.pack(side="left", fill="both", expand=True, padx=(0, 0), pady=0)
        
        # 3. CENTRAL CANVAS
        self.main_canvas = tk.Canvas(self.root)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.main_canvas)

        #ttk.Separator(self.scrollable_frame, orient='horizontal').pack(fill='x', pady=0)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )

        self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self._create_form_interface()

    def _create_form_interface(self):
        paddings = {'padx': 10, 'pady': 10}
        font_label = ("Arial", 10, "bold")

        ## Frame for Ime i Datum (Horizontal)
        self.header_row = ttk.Frame(self.scrollable_frame)
        self.header_row.pack(side="top", fill="x", expand=True, **paddings)

        ttk.Label(self.header_row, text="Ime pacijenta:", font=font_label).pack(side="left", padx=(0, 5))
        self.ent_ime = ttk.Entry(self.header_row, width=35)
        self.ent_ime.pack(side="left", padx=(0, 15))

        ttk.Label(self.header_row, text="Datum:", font=font_label).pack(side="left", padx=(0, 5))
        self.ent_datum = ttk.Entry(self.header_row, width=15)
        self.ent_datum.pack(side="left")

        ## Frame for critical founding (Vertical)
        self.report_form_frame = ttk.Frame(self.scrollable_frame)
        self.report_form_frame.pack(side="top", fill="x", **paddings)

        # Terapija
        ttk.Label(self.report_form_frame, text="PREPORUČENA TERAPIJA I SAVET:", font=font_label).pack(side="top", fill="x", **paddings)
        self.txt_terapija = scrolledtext.ScrolledText(self.report_form_frame, width=50, height=10, font=("Arial", 10))
        self.txt_terapija.pack(side="top", fill="x", pady=5)

        # SEPARATOR
        ttk.Separator(self.report_form_frame, orient='horizontal').pack(fill='x', pady=15)

        # Sekcija Nalazi
        ttk.Label(self.report_form_frame, text="NALAZI:", font=font_label).pack(side="top", fill="x", **paddings)
        
        self.nalazi_container = ttk.Frame(self.report_form_frame)
        self.nalazi_container.pack(side="top", fill="x", pady=5)

        # TABLE HEADER FRAME
        table_header_frame = ttk.Frame(self.nalazi_container, height=20)
        table_header_frame.pack(side="top", fill="x", pady=2)
        lbl_m = ttk.Label(table_header_frame, text="Mišljenje")
        lbl_m.place(relx=0.0, rely=0.0, relwidth=0.6, relheight=1.0)
        lbl_p = ttk.Label(table_header_frame, text="Parametar")
        lbl_p.place(relx=0.61, rely=0.0, relwidth=0.3, relheight=1.0)

        self.btn_dodaj_nalaz = ttk.Button(self.report_form_frame, text="+ Dodaj novi nalaz")
        self.btn_dodaj_nalaz.pack(side="top", fill="x")



    def add_finding_row(self, misljenje: str = "", parametar: str = ""):
        row_frame = ttk.Frame(self.nalazi_container, height=60)
        row_frame.pack(fill="x", pady=2)

        # --- MIŠLJENJE LEVO ---
        ent_m = scrolledtext.ScrolledText(row_frame, font=("Arial", 10), )
        ent_m.insert("1.0", misljenje)
        ent_m.place(relx=0.0, rely=0.0, relwidth=0.6, relheight=1.0)

        # --- PARAMETAR DESNO ---
        ent_p = scrolledtext.ScrolledText(row_frame, font=("Arial", 10))
        ent_p.insert("1.0", parametar)
        ent_p.place(relx=0.61, rely=0.0, relwidth=0.3, relheight=1.0)

        btn_ukloni = ttk.Button(row_frame, text="X")
        btn_ukloni.config(command=lambda rf=row_frame: self.remove_finding_row(rf))
        btn_ukloni.place(relx=0.92, rely=0.0, relwidth=0.08, relheight=1.0)

        # Čuvanje u listu kao instance variables objekti unutar rečnika
        self.nalazi_rows.append({
            "frame": row_frame, 
            "parametar": ent_p, 
            "misljenje": ent_m,
            "btn_ukloni": btn_ukloni
        })

    def remove_finding_row(self, frame: ttk.Frame):
        for i, row in enumerate(self.nalazi_rows):
            if row["frame"] == frame:
                row["frame"].destroy()
                self.nalazi_rows.pop(i)
                break

    def get_user_input(self) -> MedicalReportModel:
        rezultat: MedicalReportModel = MedicalReportModel(
            patient_name=self.ent_ime.get(),
            report_date=self.ent_datum.get(),
            preporucena_terapija_i_savet=self.txt_terapija.get("1.0", tk.END).strip(),
            nalazi=[]
        )
        for row in self.nalazi_rows:
            p_val = row["parametar"].get("1.0", tk.END).strip()
            m_val = row["misljenje"].get("1.0", tk.END).strip()
            if p_val or m_val:
                rezultat.nalazi.append(MedicalCriticalFindingModel(
                    expertsko_misljenje=m_val, 
                    parametar_i_vrednost=p_val
                ))
        return rezultat

    def set_display_data(self, data: MedicalReportModel):
        self.ent_ime.delete(0, tk.END)
        self.ent_ime.insert(0, data.patient_name)
        self.ent_datum.delete(0, tk.END)
        self.ent_datum.insert(0, data.report_date)
        self.txt_terapija.delete("1.0", tk.END)
        self.txt_terapija.insert("1.0", data.preporucena_terapija_i_savet)
        
        for n in data.nalazi:
            self.add_finding_row(misljenje=n.expertsko_misljenje, parametar=n.parametar_i_vrednost)

    def update_status(self, header_text: str = "UNKNOWN", details_text: str = "/"):
        self.var_status.set(f"{header_text} | {details_text}")
        #self.lbl_status_details.config(text=details_text)