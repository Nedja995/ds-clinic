import tkinter as tk
from tkinter import messagebox, scrolledtext
from fpdf import FPDF
from datetime import datetime

class ReportApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Generator Izvestaja - Holisticki Centar")
        self.root.geometry("800x700")

        # --- Podaci za tabelu ---
        self.table_rows = []

        # --- UI Elementi ---
        
        # Pacijent
        tk.Label(root, text="Ime i prezime pacijenta:", font=("Arial", 10, "bold")).pack(pady=(10, 0))
        self.ent_pacijent = tk.Entry(root, width=50)
        self.ent_pacijent.pack(pady=5)

        # Tabela (Naslovi)
        table_frame = tk.Frame(root)
        table_frame.pack(pady=10)
        
        tk.Label(table_frame, text="Ekspertsko misljenje", width=30, relief="solid").grid(row=0, column=0)
        tk.Label(table_frame, text="Parametar aparata (Original)", width=40, relief="solid").grid(row=0, column=1)

        # Polja za unos u tabelu (7 redova kao na slici)
        for i in range(7):
            e1 = tk.Entry(table_frame, width=30)
            e1.grid(row=i+1, column=0)
            e2 = tk.Entry(table_frame, width=40)
            e2.grid(row=i+1, column=1)
            self.table_rows.append((e1, e2))

        # Terapija i savet
        tk.Label(root, text="PREPORUcENA TERAPIJA I SAVET:", font=("Arial", 10, "bold"), fg="red").pack(pady=(10, 0))
        self.txt_terapija = scrolledtext.ScrolledText(root, width=80, height=8)
        self.txt_terapija.pack(pady=5)

        # Dugme za generisanje
        self.btn_generate = tk.Button(root, text="GENERIsI PDF", command=self.generate_pdf, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), padx=20, pady=10)
        self.btn_generate.pack(pady=20)

    def generate_pdf(self):
        pacijent = self.ent_pacijent.get()
        terapija = self.txt_terapija.get("1.0", tk.END).strip()
        datum = datetime.now().strftime("%d.%m.%Y")

        if not pacijent:
            messagebox.showwarning("Greska", "Unesite ime pacijenta!")
            return

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Header - Naslov
        pdf.set_font("Arial", 'B', 16)
        pdf.set_text_color(0, 51, 153) # Tamno plava
        pdf.cell(0, 15, "HOLISTIcKI CENTAR DAR PRIRODE", ln=True, align='C')
        
        # Linija ispod naslova
        pdf.set_draw_color(200, 200, 200)
        pdf.line(10, 25, 200, 25)
        pdf.ln(10)

        # Pacijent i Datum
        pdf.set_font("Arial", 'B', 10)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(100, 10, f"Pacijent: {pacijent}")
        pdf.cell(0, 10, f"{datum}", align='R', ln=True)
        pdf.ln(5)

        # Tabela - Zaglavlje
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(90, 10, " Ekspertsko misljenje", border=1, fill=True)
        pdf.cell(100, 10, " Parametar aparata (Original)", border=1, fill=True, ln=True)

        # Tabela - Sadržaj
        pdf.set_font("Arial", '', 10)
        for e1, e2 in self.table_rows:
            val1 = e1.get()
            val2 = e2.get()
            if val1 or val2: # Dodaj red samo ako nije prazan
                pdf.cell(90, 8, f" {val1}", border=1)
                pdf.cell(100, 8, f" {val2}", border=1, ln=True)

        pdf.ln(10)

        # Terapija - Naslov
        pdf.set_font("Arial", 'B', 11)
        pdf.set_text_color(200, 0, 0) # Crvena
        pdf.cell(0, 10, "PREPORUCENA TERAPIJA I SAVET:", ln=True)
        
        # Terapija - Tekst
        pdf.set_font("Arial", '', 10)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 6, terapija)
        pdf.ln(10)

        # Saglasnost i Napomena
        pdf.set_font("Arial", 'I', 9)
        pdf.multi_cell(0, 5, "SAGLASNOST: Pacijent je upoznat sa metodom, preporucenom terapijom i istu u potpunosti prihvata.")
        pdf.ln(2)
        pdf.multi_cell(0, 5, "NAPOMENA: Rezultati su holisticki uvid. Za medicinske dijagnoze konsultujte svog lekara.")

        # Potpis (Donji desni ugao)
        pdf.ln(20)
        pdf.set_font("Arial", 'I', 8)
        pdf.cell(120) # Pomeraj udesno
        pdf.cell(70, 0, "", border="T", ln=True) # Linija za potpis
        pdf.cell(120)
        pdf.cell(70, 5, "M.P. Potpis terapeuta", align='C')

        # cuvanje fajla
        filename = f"Izvestaj_{pacijent.replace(' ', '_')}.pdf"
        try:
            pdf.output(filename)
            messagebox.showinfo("Uspeh", f"PDF izvestaj je uspesno generisan: {filename}")
        except Exception as e:
            messagebox.showerror("Greska", f"Doslo je do greske: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ReportApp(root)
    root.mainloop()