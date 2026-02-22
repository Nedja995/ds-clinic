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