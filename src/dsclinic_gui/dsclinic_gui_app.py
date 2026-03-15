import tkinter as tk
from tkinter import ttk, scrolledtext
import tkinter.messagebox
from logger import setup_logger
from dsclinic import process_documents

logger = setup_logger()

# --- MODEL ---
class DSClinicModel:
    def __init__(self, initial_data=None):
        self.data = initial_data or {}

    def get_data(self):
        return self.data

    def set_data(self, data):
        self.data = data

# --- VIEW ---
class DSClinicView:
    def __init__(self, root):
        self.root = root
        self.root.title("DS Clinic Analiza")
        self.root.geometry("950x800")
        
        self.nalazi_rows = []
        
        self._setup_ui()

    def _setup_ui(self):
        # 1. TOP TOOLBAR
        self.top_frame = ttk.Frame(self.root)
        self.top_frame.pack(side="top", fill="x", padx=5, pady=5)

        self.status_var = tk.StringVar(value="STATUS: Idle")
        self.lbl_status = tk.Label(
            self.top_frame, textvariable=self.status_var, font=("Arial", 14, "bold"),
            bg="#ff8f81", relief="sunken", width=20, anchor="w", padx=5
        )
        self.lbl_status.pack(side="left", padx=(0, 15))

        self.btn_analyze = ttk.Button(self.top_frame, text="POKRENI ANALIZU")
        self.btn_analyze.pack(side="left", padx=5)
        
        self.btn_submit = ttk.Button(self.top_frame, text="SAČUVAJ PDF IZVEŠTAJ", state="enabled")
        self.btn_submit.pack(side="left", padx=5)

        self.btn_full_report = ttk.Button(self.top_frame, text="Cela analiza", state="disabled")
        self.btn_full_report.pack(side="left", padx=5)

        self.btn_settings = ttk.Button(self.top_frame, text="Podešavanja")
        self.btn_settings.pack(side="left", padx=5)
        
        # 2. FOOTER
        self.footer_frame = ttk.Frame(self.root)
        self.footer_frame.pack(side="bottom", fill="x")

        self.lbl_footer_status = tk.Label(
            self.footer_frame, text="STATUS:", font=("Arial", 12, "bold"), fg="red"
        )
        self.lbl_footer_status.pack(side="left", padx=(10, 5), pady=5, fill="y")

        self.lbl_status_details = tk.Label(
            self.footer_frame, text="IDLE - ADD DOCUMENTS AND START ANALYSIS",
            font=("Arial", 12, "normal"), fg="black", anchor="w"
        )
        self.lbl_status_details.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=5)
        
        ttk.Separator(self.root, orient='horizontal').pack(fill='x', pady=0, side=tk.BOTTOM)

        # 3. CENTRAL CANVAS
        self.main_canvas = tk.Canvas(self.root)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.main_canvas)

        ttk.Separator(self.scrollable_frame, orient='horizontal').pack(fill='x', pady=0)
        
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

        # Okvir za Ime i Datum
        self.header_row = ttk.Frame(self.scrollable_frame)
        self.header_row.pack(fill="x", **paddings)

        ttk.Label(self.header_row, text="Ime pacijenta:", font=font_label).pack(side="left", padx=(0, 5))
        self.ent_ime = ttk.Entry(self.header_row, width=35)
        self.ent_ime.pack(side="left", padx=(0, 25))

        ttk.Label(self.header_row, text="Datum:", font=font_label).pack(side="left", padx=(0, 5))
        self.ent_datum = ttk.Entry(self.header_row, width=15)
        self.ent_datum.pack(side="left")

        # Terapija
        ttk.Label(self.scrollable_frame, text="PREPORUČENA TERAPIJA I SAVET:", font=font_label).pack(anchor="w", **paddings)
        self.txt_terapija = scrolledtext.ScrolledText(self.scrollable_frame, width=50, height=10, font=("Arial", 10))
        self.txt_terapija.pack(anchor="w", padx=10, pady=5)

        # Sekcija Nalazi
        ttk.Separator(self.scrollable_frame, orient='horizontal').pack(fill='x', pady=15)
        ttk.Label(self.scrollable_frame, text="NALAZI:", font=font_label).pack(anchor="w", padx=10)
        
        self.nalazi_container = ttk.Frame(self.scrollable_frame)
        self.nalazi_container.pack(fill="x", padx=10, pady=5)

        self.btn_dodaj_nalaz = ttk.Button(self.scrollable_frame, text="+ Dodaj novi nalaz")
        self.btn_dodaj_nalaz.pack(anchor="w", padx=10)

    def add_finding_row(self, misljenje="", parametar=""):
        row_frame = ttk.Frame(self.nalazi_container)
        row_frame.pack(fill="x", pady=2)

        # --- ZAMENJEN REDOSLED: MIŠLJENJE LEVO ---
        lbl_m = ttk.Label(row_frame, text="Mišljenje:")
        lbl_m.pack(side="left")
        ent_m = ttk.Entry(row_frame, width=45)
        ent_m.insert(0, misljenje)
        ent_m.pack(side="left", padx=5)

        # --- PARAMETAR DESNO ---
        lbl_p = ttk.Label(row_frame, text="Parametar:")
        lbl_p.pack(side="left")
        ent_p = ttk.Entry(row_frame, width=20)
        ent_p.insert(0, parametar)
        ent_p.pack(side="left", padx=5)

        btn_ukloni = ttk.Button(row_frame, text="X", width=3)
        btn_ukloni.config(command=lambda rf=row_frame: self.remove_finding_row(rf))
        btn_ukloni.pack(side="left")

        # Čuvanje u listu kao instance variables objekti unutar rečnika
        self.nalazi_rows.append({
            "frame": row_frame, 
            "parametar": ent_p, 
            "misljenje": ent_m,
            "btn_ukloni": btn_ukloni,
            "lbl_p": lbl_p,
            "lbl_m": lbl_m
        })

    def remove_finding_row(self, frame):
        for i, row in enumerate(self.nalazi_rows):
            if row["frame"] == frame:
                row["frame"].destroy()
                self.nalazi_rows.pop(i)
                break

    def get_user_input(self):
        rezultat = {
            "ime_pacijenta": self.ent_ime.get(),
            "datum": self.ent_datum.get(),
            "terapija_i_savet": self.txt_terapija.get("1.0", tk.END).strip(),
            "nalazi": []
        }
        for row in self.nalazi_rows:
            p_val = row["parametar"].get()
            m_val = row["misljenje"].get()
            if p_val or m_val:
                rezultat["nalazi"].append({"parametar_aparata": p_val, "misljenje": m_val})
        return rezultat

    def set_display_data(self, data):
        self.ent_ime.delete(0, tk.END)
        self.ent_ime.insert(0, data.get("ime_pacijenta", ""))
        self.ent_datum.delete(0, tk.END)
        self.ent_datum.insert(0, data.get("datum", ""))
        self.txt_terapija.delete("1.0", tk.END)
        self.txt_terapija.insert("1.0", data.get("terapija_i_savet", ""))
        
        for n in data.get("nalazi", []):
            self.add_finding_row(misljenje=n.get("misljenje", ""), parametar=n.get("parametar_aparata", ""))

    def update_status(self, header_text, details_text):
        self.status_var.set(f"STATUS: {header_text}")
        self.lbl_status_details.config(text=details_text)

# --- CONTROLLER ---
class DSClinicController:
    def __init__(self, root, model, view):
        self.root = root
        self.model = model
        self.view = view
        
        self._bind_events()
        self._initialize_view()

    def _bind_events(self):
        self.view.btn_analyze.config(command=self._handle_analyze_click)
        self.view.btn_submit.config(command=self._handle_export_click)
        self.view.btn_settings.config(command=self._handle_settings_click)
        self.view.btn_dodaj_nalaz.config(command=self.view.add_finding_row)

    def _initialize_view(self):
        data = self.model.get_data()
        if data:
            self.view.set_display_data(data)
        else:
            self.view.add_finding_row()

    def _handle_analyze_click(self):
        if self.view.btn_analyze["text"] == "POKRENI ANALIZU":
            self.view.btn_analyze.config(text="PREKINI ANALIZU")
            self.view.update_status("Running", "ANALYSIS IN PROGRESS...")
            self.view.btn_full_report.config(state="normal")
        else:
            self.view.btn_analyze.config(text="POKRENI ANALIZU")
            self.view.update_status("Idle", "IDLE - ADD DOCUMENTS AND START ANALYSIS")
            self.view.btn_full_report.config(state="disabled")

    def _handle_export_click(self):
        data = self.view.get_user_input()
        self.model.set_data(data)
        
        print("Sakupljeni podaci:")
        import pprint
        pprint.pprint(data)
        
        self.view.update_status("Saved", "DATA SAVED SUCCESSFULLY!")
        tkinter.messagebox.showinfo("Uspeh", "Podaci su spremni za vašu PDF funkciju.")

    def _handle_settings_click(self):
        print(f"Kliknuto na: Podešavanja")
        self.view.update_status("Settings Open", "ADJUSTING SETTINGS...")

# --- FACADE ---
class DSClinicAppGUI:
    def __init__(self, root, inicijalni_podaci=None):
        self.model = DSClinicModel(inicijalni_podaci)
        self.view = DSClinicView(root)
        self.controller = DSClinicController(root, self.model, self.view)

if __name__ == "__main__":
    # import logging
    # logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # logging.getLogger('fontTools').setLevel(logging.WARNING)
    test_podaci = {
        "ime_pacijenta": "Marko Marković",
        "datum": "24.05.2024.",
        "terapija_i_savet": "Smanjiti fizički napor.",
        "nalazi": [{"parametar_aparata": "Puls", "misljenje": "75 bpm"}]
    }

    root = tk.Tk()
    app = DSClinicAppGUI(root, inicijalni_podaci=test_podaci)
    root.mainloop()