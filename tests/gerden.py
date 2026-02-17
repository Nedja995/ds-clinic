import os
import pdfplumber
from fpdf import FPDF
import warnings

# Gasi upozorenja
warnings.filterwarnings("ignore")

# --- TVOJA BAZA KOJU ĆEŠ RUČNO DOPUNJAVATI ---
PROTOKOLI = {
    "GARDNERELLA VAGINALIS": {
        "nalaz": "Detektovana Gardnerella vaginalis (Bakterijska vaginoza).",
        "terapija": [
            "GARDIA 1 (Antibiotik): 3x20 kapi (Beli luk/Origano) - POSLE jela.",
            "GARDIA 2 (Regeneracija): 3x30 kapi u GARDIA CAJU - PRE jela.",
            "GARDIA 3 (Probiotik): Enterobiotik koji OBAVEZNO sadrzi Lactobacillus.",
            "GARDIA CAJ: Piti 1 litar dnevno (Majcina dusica, Neven, Hajducka trava...)"
        ],
        "napomena": "Terapija traje 21 dan. Izbaciti secere iz ishrane."
    }
    # Ovde ces sam dodavati nove stavke po istom principu
}

def sredi_slova(tekst):
    """Sredjuje nasa slova za PDF"""
    mape = {"č": "c", "ć": "c", "ž": "z", "š": "s", "đ": "dj", "Č": "C", "Ć": "C", "Ž": "Z", "Š": "S", "Đ": "Dj"}
    for k, v in mape.items(): tekst = tekst.replace(k, v)
    return tekst

def pokreni_analizu():
    staza = os.path.dirname(os.path.abspath(__file__))
    ulaz = os.path.join(staza, "ULAZ")
    izlaz = os.path.join(staza, "IZVESTAJI")
    
    if not os.path.exists(izlaz): os.makedirs(izlaz)
    if not os.path.exists(ulaz): os.makedirs(ulaz)
    
    fajlovi = [f for f in os.listdir(ulaz) if f.lower().endswith('.pdf')]
    
    for fajl in fajlovi:
        pronadjeno = []
        try:
            # 1. Citanje PDF-a
            with pdfplumber.open(os.path.join(ulaz, fajl)) as pdf:
                sadrzaj = " ".join([strana.extract_text() or "" for strana in pdf.pages]).upper()
            
            # 2. Provera da li je bakterija u tekstu
            for kljuc, podaci in PROTOKOLI.items():
                if kljuc in sadrzaj:
                    pronadjeno.append(podaci)

            # 3. Pravljenje PDF izvestaja
            pdf_novi = FPDF()
            pdf_novi.add_page()
            
            pdf_novi.set_font("Helvetica", 'B', 16)
            pdf_novi.cell(0, 10, "HOLISTICKI CENTAR DAR PRIRODE", align='C', ln=True)
            pdf_novi.ln(10)
            
            if pronadjeno:
                for stavka in pronadjeno:
                    # Naslov nalaza
                    pdf_novi.set_font("Helvetica", 'B', 12)
                    pdf_novi.multi_cell(0, 10, sredi_slova(f"NALAZ: {stavka['nalaz']}"))
                    pdf_novi.ln(2)
                    
                    # Terapija
                    pdf_novi.set_font("Helvetica", '', 11)
                    for red in stavka['terapija']:
                        pdf_novi.cell(10) # indent
                        pdf_novi.cell(0, 8, f"- {sredi_slova(red)}", ln=True)
                    
                    # Napomena
                    pdf_novi.ln(4)
                    pdf_novi.set_font("Helvetica", 'I', 10)
                    pdf_novi.multi_cell(0, 8, sredi_slova(f"NAPOMENA: {stavka['napomena']}"))
                    pdf_novi.ln(10)
            else:
                pdf_novi.set_font("Helvetica", '', 11)
                pdf_novi.cell(0, 10, "Specificne bakterije nisu pronadjene u ovom nalazu.", ln=True)

            pdf_novi.output(os.path.join(izlaz, f"NALAZ_{fajl}"))
            print(f"Zavrsen PDF: NALAZ_{fajl}")

        except Exception as e:
            print(f"Greska: {str(e)}")

    if os.name == 'nt': os.startfile(izlaz)


def main():
    pokreni_analizu()

if __name__ == "__main__":
    pokreni_analizu()