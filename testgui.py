import tkinter as tk
from tkinter import ttk, scrolledtext
import tkinter.messagebox

class MedicinskaApp:
    def __init__(self, root, inicijalni_podaci=None):
        self.root = root
        self.root.title("Medicinski Izveštaj - Unos Podataka")
        self.root.geometry("900x800")

        # --- TOP TOOLBAR (Gornji panel sa kontrolama) ---
        self.top_frame = ttk.Frame(root)
        self.top_frame.pack(side="top", fill="x", padx=10, pady=10)

        # 1. STATUS LABELA (Skroz levo, fiksne širine 120 kako bi stalo "STATUS: ...")
        self.status_var = tk.StringVar(value="STATUS: Idle")
        self.lbl_status = tk.Label(
            self.top_frame, 
            textvariable=self.status_var, 
            font=("Arial", 9, "bold"),
            bg="#e0e0e0",
            relief="sunken",
            width=20,     # Širina u karakterima (otprilike 150px)
            anchor="w",   # Tekst poravnat levo unutar labele
            padx=5
        )
        self.lbl_status.pack(side="left", padx=(0, 15))

        # 2. DUGMIĆI (Nastavljaju se nakon statusa)
        self.btn_pokreni = ttk.Button(self.top_frame, text="Pokreni analizu", command=self.toggle_analiza)
        self.btn_pokreni.pack(side="left", padx=5)

        self.btn_cela = ttk.Button(self.top_frame, text="Cela analiza", state="disabled")
        self.btn_cela.pack(side="left", padx=5)

        self.btn_settings = ttk.Button(
            self.top_frame, 
            text="Podešavanja", 
            command=lambda: self.btn_clicked(self.btn_settings)
        )
        self.btn_settings.pack(side="left", padx=5)

        # --- CENTRALNI DEO (Skrolabilna forma) ---
        self.main_canvas = tk.Canvas(root)
        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.main_canvas)

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

    # --- FUNKCIJE ZA UPRAVLJANJE STANJEM ---

    def change_app_state(self, text):
        """ Menja tekst u statusnom polju. Automatski dodaje prefiks STATUS: """
        self.status_var.set(f"STATUS: {text}")

    def btn_cela_analiza_enable(self, enabled: bool = True):
        """ Omogućava ili onemogućava dugme 'Cela analiza' """
        stanje = "normal" if enabled else "disabled"
        self.btn_cela.config(state=stanje)

    def btn_clicked(self, button: ttk.Button):
        """ Prazna funkcija za Podešavanja """
        print(f"Kliknuto na: {button['text']}")
        self.change_app_state("Settings Open")

    def toggle_analiza(self):
        """ Logika za Pokreni/Prekini dugme """
        if self.btn_pokreni["text"] == "Pokreni analizu":
            self.btn_pokreni.config(text="Prekini analizu")
            self.change_app_state("Running")
            self.btn_cela_analiza_enable(True)
        else:
            self.btn_pokreni.config(text="Pokreni analizu")
            self.change_app_state("Idle")
            self.btn_cela_analiza_enable(False)

    # --- INTERFEJS FORME ---

    def _kreiraj_interfejs_forme(self):
        paddings = {'padx': 10, 'pady': 10}
        font_label = ("Arial", 10, "bold")

        # Red za Ime i Datum
        header_row = ttk.Frame(self.scrollable_frame)
        header_row.pack(fill="x", **paddings)

        ttk.Label(header_row, text="Ime pacijenta:", font=font_label).pack(side="left", padx=(0, 5))
        self.ent_ime = ttk.Entry(header_row, width=35)
        self.ent_ime.pack(side="left", padx=(0, 25))

        ttk.Label(header_row, text="Datum:", font=font_label).pack(side="left", padx=(0, 5))
        self.ent_datum = ttk.Entry(header_row, width=15)
        self.ent_datum.pack(side="left")

        # Terapija
        ttk.Label(self.scrollable_frame, text="PREPORUČENA TERAPIJA I SAVET:", font=font_label).pack(anchor="w", **paddings)
        self.txt_terapija = scrolledtext.ScrolledText(self.scrollable_frame, width=85, height=10, font=("Arial", 10))
        self.txt_terapija.pack(anchor="w", padx=10, pady=5)

        # Sekcija Nalazi
        ttk.Separator(self.scrollable_frame, orient='horizontal').pack(fill='x', pady=15)
        ttk.Label(self.scrollable_frame, text="NALAZI:", font=font_label).pack(anchor="w", padx=10)
        
        self.nalazi_container = ttk.Frame(self.scrollable_frame)
        self.nalazi_container.pack(fill="x", padx=10, pady=5)

        ttk.Button(self.scrollable_frame, text="+ Dodaj novi nalaz", command=self.dodaj_red_za_nalaz).pack(anchor="w", padx=10)
        
        ttk.Separator(self.scrollable_frame, orient='horizontal').pack(fill='x', pady=15)
        ttk.Button(self.scrollable_frame, text="SAČUVAJ PODATKE", command=self.prikupi_i_prosledi).pack(pady=20)

    def dodaj_red_za_nalaz(self, misljenje="", parametar=""):
        row_frame = ttk.Frame(self.nalazi_container)
        row_frame.pack(fill="x", pady=2)

        ttk.Label(row_frame, text="Parametar:").pack(side="left")
        ent_p = ttk.Entry(row_frame, width=20)
        ent_p.insert(0, parametar)
        ent_p.pack(side="left", padx=5)

        ttk.Label(row_frame, text="Mišljenje:").pack(side="left")
        ent_m = ttk.Entry(row_frame, width=45)
        ent_m.insert(0, misljenje)
        ent_m.pack(side="left", padx=5)

        ttk.Button(row_frame, text="X", width=3, command=lambda rf=row_frame: self.ukloni_red_za_nalaz(rf)).pack(side="left")
        self.nalazi_rows.append({"frame": row_frame, "parametar": ent_p, "misljenje": ent_m})

    def ukloni_red_za_nalaz(self, frame):
        for i, row in enumerate(self.nalazi_rows):
            if row["frame"] == frame:
                row["frame"].destroy()
                self.nalazi_rows.pop(i)
                break

    def popuni_podatke(self, data):
        self.ent_ime.insert(0, data.get("ime_pacijenta", ""))
        self.ent_datum.insert(0, data.get("datum", ""))
        self.txt_terapija.insert("1.0", data.get("terapija_i_savet", ""))
        for n in data.get("nalazi", []):
            self.dodaj_red_za_nalaz(misljenje=n.get("misljenje", ""), parametar=n.get("parametar_aparata", ""))

    def prikupi_i_prosledi(self):
        rezultat = {
            "ime_pacijenta": self.ent_ime.get(),
            "datum": self.ent_datum.get(),
            "terapija_i_savet": self.txt_terapija.get("1.0", tk.END).strip(),
            "nalazi": []
        }
        for row in self.nalazi_rows:
            p_val, m_val = row["parametar"].get(), row["misljenje"].get()
            if p_val or m_val:
                rezultat["nalazi"].append({"parametar_aparata": p_val, "misljenje": m_val})
        
        print("Finalni podaci za PDF:")
        import pprint
        pprint.pprint(rezultat)
        self.change_app_state("Saved")
        tkinter.messagebox.showinfo("Uspeh", "Podaci su prikupljeni u dictionary.")

if __name__ == "__main__":
    test_podaci = {
        "ime_pacijenta": "Jovan Jovanović",
        "datum": "24.05.2024.",
        "terapija_i_savet": "Kontrola za mesec dana.",
        "nalazi": [{"parametar_aparata": "Pritisak", "misljenje": "120/80"}]
    }

    root = tk.Tk()
    app = MedicinskaApp(root, inicijalni_podaci=test_podaci)
    root.mainloop()