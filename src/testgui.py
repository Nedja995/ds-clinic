import tkinter as tk
from tkinter import ttk, scrolledtext
import tkinter.messagebox
from logger import setup_logger
from dsclinic import analyze_inputs_and_export_report

logger = setup_logger()

class DSClinicAppGUI:
    def __init__(self, root, inicijalni_podaci=None):
        self.root = root
        self.root.title("DS Clinic Analiza")
        self.root.geometry("950x800")

        # --- 1. TOP TOOLBAR (Gornji panel) ---
        self.top_frame = ttk.Frame(self.root)
        self.top_frame.pack(side="top", fill="x", padx=5, pady=5)

        # Status Labela (Instance variable)
        self.status_var = tk.StringVar(value="STATUS: Idle")
        self.lbl_status = tk.Label(
            self.top_frame, 
            textvariable=self.status_var, 
            font=("Arial", 14, "bold"),
            bg="#ff8f81",
            relief="sunken",
            width=20,
            anchor="w",
            padx=5
        )
        self.lbl_status.pack(side="left", padx=(0, 15))

        # Dugmad na vrhu
        self.btn_analyze = ttk.Button(self.top_frame, text="POKRENI ANALIZU", command=self._clicked_btn_analyze)
        self.btn_analyze.pack(side="left", padx=5)
        
        #  Dugme Sačuvaj podatke
        self.btn_submit = ttk.Button(self.top_frame, text="SAČUVAJ PDF IZVEŠTAJ", state="enabled", command=self._clicked_btn_export_pdf)
        self.btn_submit.pack(side="left", padx=5)

        self.btn_full_report = ttk.Button(self.top_frame, text="Cela analiza", state="disabled")
        self.btn_full_report.pack(side="left", padx=5)

        self.btn_settings = ttk.Button(
            self.top_frame, 
            text="Podešavanja", 
            command=lambda: self._clicked_button(self.btn_settings)
        )
        self.btn_settings.pack(side="left", padx=5)
        
        # --- 2. FOOTER (Donji panel) ---
        # NOTE: Packed before the main_canvas so it stays fixed to the absolute bottom
        self.footer_frame = ttk.Frame(self.root)
        self.footer_frame.pack(side="bottom", fill="x")

        self.lbl_footer_status = tk.Label(
            self.footer_frame,
            text="STATUS:",
            font=("Arial", 12, "bold"),
            fg="red"
        )
        self.lbl_footer_status.pack(side="left", padx=(10, 5), pady=5, fill="y")

        self.lbl_status_details = tk.Label(
            self.footer_frame,
            text="ADD DOCUMENTS AND START ANALYSIS",
            font=("Arial", 12, "normal"),
            fg="black",
            anchor="w"
        )
        self.lbl_status_details.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=5)
        
        self.sep_footer = ttk.Separator(self.root, orient='horizontal')
        self.sep_footer.pack(fill='x', pady=0, side=tk.BOTTOM)

        # --- 3. CENTRALNI DEO (Skrolabilna forma) ---
        self.main_canvas = tk.Canvas(self.root)
        
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.main_canvas)

        self.sep_header = ttk.Separator(self.scrollable_frame, orient='horizontal')
        self.sep_header.pack(fill='x', pady=0)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )

        self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.nalazi_rows = []
        self._kreiraj_interfejs_forme()

        if inicijalni_podaci:
            self.popuni_podatke(inicijalni_podaci)
        else:
            self.dodaj_red_za_nalaz()

    def _kreiraj_interfejs_forme(self):
        paddings = {'padx': 10, 'pady': 10}
        font_label = ("Arial", 10, "bold")

        # Okvir za Ime i Datum
        self.header_row = ttk.Frame(self.scrollable_frame)
        self.header_row.pack(fill="x", **paddings)

        self.lbl_ime_tag = ttk.Label(self.header_row, text="Ime pacijenta:", font=font_label)
        self.lbl_ime_tag.pack(side="left", padx=(0, 5))
        self.ent_ime = ttk.Entry(self.header_row, width=35)
        self.ent_ime.pack(side="left", padx=(0, 25))

        self.lbl_datum_tag = ttk.Label(self.header_row, text="Datum:", font=font_label)
        self.lbl_datum_tag.pack(side="left", padx=(0, 5))
        self.ent_datum = ttk.Entry(self.header_row, width=15)
        self.ent_datum.pack(side="left")

        # Terapija
        self.lbl_terapija_tag = ttk.Label(self.scrollable_frame, text="PREPORUČENA TERAPIJA I SAVET:", font=font_label)
        self.lbl_terapija_tag.pack(anchor="w", **paddings)
        self.txt_terapija = scrolledtext.ScrolledText(self.scrollable_frame, width=50, height=10, font=("Arial", 10))
        self.txt_terapija.pack(anchor="w", padx=10, pady=5)

        # Sekcija Nalazi
        self.sep_1 = ttk.Separator(self.scrollable_frame, orient='horizontal')
        self.sep_1.pack(fill='x', pady=15)
        self.lbl_nalazi_tag = ttk.Label(self.scrollable_frame, text="NALAZI:", font=font_label)
        self.lbl_nalazi_tag.pack(anchor="w", padx=10)
        
        self.nalazi_container = ttk.Frame(self.scrollable_frame)
        self.nalazi_container.pack(fill="x", padx=10, pady=5)

        self.btn_dodaj_nalaz = ttk.Button(self.scrollable_frame, text="+ Dodaj novi nalaz", command=self.dodaj_red_za_nalaz)
        self.btn_dodaj_nalaz.pack(anchor="w", padx=10)

    def dodaj_red_za_nalaz(self, misljenje="", parametar=""):
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

        btn_ukloni = ttk.Button(row_frame, text="X", width=3, command=lambda rf=row_frame: self.ukloni_red_za_nalaz(rf))
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

    def ukloni_red_za_nalaz(self, frame):
        for i, row in enumerate(self.nalazi_rows):
            if row["frame"] == frame:
                row["frame"].destroy()
                self.nalazi_rows.pop(i)
                break

    def change_app_state(self, text):
        self.status_var.set(f"{text}")

    def set_app_state_details(self, text):
        self.lbl_status_details.config(text=text)

    def set_btn_analyze_enabled(self, enabled: bool = True):
        state = "normal" if enabled else "disabled"
        self.btn_full_report.config(state=state)

    def _clicked_button(self, button: ttk.Button):
        print(f"Kliknuto na: {button['text']}")
        self.change_app_state("Settings Open")
        self.set_app_state_details("ADJUSTING SETTINGS...")

    def _clicked_btn_analyze(self):
        if self.btn_analyze["text"] == "POKRENI ANALIZU":
            self.btn_analyze.config(text="PREKINI ANALIZU")
            self.change_app_state("Running")
            self.set_app_state_details("ANALYSIS IN PROGRESS...")
            self.set_btn_analyze_enabled(True)
        else:
            self.btn_analyze.config(text="POKRENI ANALIZU")
            self.change_app_state("Idle")
            self.set_app_state_details("IDLE - ADD DOCUMENTS AND START ANALYSIS")
            self.set_btn_analyze_enabled(False)

    def _clicked_btn_export_pdf(self):
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
        
        print("Sakupljeni podaci:")
        import pprint
        pprint.pprint(rezultat)
        self.change_app_state("Saved")
        self.set_app_state_details("DATA SAVED SUCCESSFULLY!")
        tkinter.messagebox.showinfo("Uspeh", "Podaci su spremni za vašu PDF funkciju.")

    def popuni_podatke(self, data):
        self.ent_ime.insert(0, data.get("ime_pacijenta", ""))
        self.ent_datum.insert(0, data.get("datum", ""))
        self.txt_terapija.insert("1.0", data.get("terapija_i_savet", ""))
        for n in data.get("nalazi", []):
            self.dodaj_red_za_nalaz(misljenje=n.get("misljenje", ""), parametar=n.get("parametar_aparata", ""))


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