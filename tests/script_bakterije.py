import os
import pdfplumber
from fpdf import FPDF
import warnings

warnings.filterwarnings("ignore")

# ==========================================================
# CENTRALNA BAZA PODATAKA (Ovde samo dodaješ, ništa ne brišeš)
# ==========================================================
VELIKA_BAZA = {
    # --- GRUPA: BAKTERIJE ---
    "GARDNERELLA VAGINALIS": {
        "nalaz": "Bakterijska vaginoza (Gardnerella)",
        "terapija": ["GARDIA 1", "GARDIA 2", "GARDIA 3", "GARDIA CAJ"],
        "napomena": "Terapija 21 dan uz probiotik sa laktobacilusom."
    },
    "ESCHERICHIA COLI": {
        "nalaz": "Escherichia coli (Eserihija)",
        "terapija": ["Caj od uve i brusnice", "D-Manoza (2g dnevno)", "Povecati unos vode"],
        "napomena": "Izbaciti secer jer on hrani Eserihiju."
    },

    # --- GRUPA: GLJIVICE ---
    "CANDIDA ALBICANS": {
        "nalaz": "Kandida (Gljivicna infekcija)",
        "terapija": ["GARDIA 1 (Pojacano)", "Anti-kandida dijeta", "Probiotik"],
        "napomena": "Stroga dijeta bez kvasca i belog brasna."
    },

    # --- GRUPA: VIRUSI ---
    "EPSTEIN-BARR VIRUS": {
        "nalaz": "Epstajn-Bar virus (Mononukleoza)",
        "terapija": ["Vitamin C (visoke doze)", "Cink", "Antivirusne biljne kapi"],
        "napomena": "Potreban odmor i podrska jetri."
    },
    "ROTAVIRUS": {
        "nalaz": "Rotavirus (Digestivna infekcija)",
        "terapija": ["Rehidratacija (elektroliti)", "Probiotik", "Laki obroci"],
        "napomena": "Kljucno je spreciti dehidrataciju organizma."
    },

    # --- GRUPA: PARAZITI I CRVI ---
    "HELMINTHS": {
        "nalaz": "Prisustvo parazita (Gliste i crvi)",
        "terapija": ["Antiparazitni program (Crni orah, Pelin, Karanfilic)"],
        "napomena": "Tretirati sve clanove domacinstva istovremeno."
    },
    "ASCARIS": {
        "nalaz": "Ascaris (Velika decija glista)",
        "terapija": ["Tinktura belog luka", "Caj od pelina"],
        "napomena": "Redovna higijena ruku je obavezna."
    },

    # <<< OVDE MOŽEŠ DODATI NOVU STAVKU PO ISTOM ŠABLONU >>>
}

def sredi_slova(tekst):
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
        nadjenih_protokola = []
        try:
            with pdfplumber.open(os.path.join(ulaz, fajl)) as pdf:
                tekst_pdfa = " ".join([s.extract_text() or "" for s in pdf.pages]).upper()
            
            for kljuc, podaci in VELIKA_BAZA.items():
                if kljuc.upper() in tekst_pdfa:
                    nadjenih_protokola.append(podaci)

            # GENERISANJE PDF-A
            pdf_novi = FPDF()
            pdf_novi.add_page()
            pdf_novi.set_font("Helvetica", 'B', 16)
            pdf_novi.cell(0, 10, "HOLISTICKI CENTAR DAR PRIRODE", align='C', ln=True)
            pdf_novi.ln(10)

            if nadjenih_protokola:
                pdf_novi.set_font("Helvetica", 'B', 12)
                pdf_novi.cell(0, 10, "PRONADJENA STANJA I TERAPIJE:", ln=True)
                pdf_novi.ln(5)

                for p in nadjenih_protokola:
                    pdf_novi.set_font("Helvetica", 'B', 11)
                    pdf_novi.cell(0, 10, sredi_slova(f"NALAZ: {p['nalaz']}"), ln=True)
                    
                    pdf_novi.set_font("Helvetica", '', 10)
                    for t in p['terapija']:
                        pdf_novi.cell(10)
                        pdf_novi.cell(0, 7, f"- {sredi_slova(t)}", ln=True)
                    
                    pdf_novi.set_font("Helvetica", 'I', 9)
                    pdf_novi.multi_cell(0, 7, sredi_slova(f"Vazno: {p['napomena']}"))
                    pdf_novi.ln(5)
            else:
                pdf_novi.cell(0, 10, "Nisu detektovani specificni patogeni iz baze.", ln=True)

            pdf_novi.output(os.path.join(izlaz, f"NALAZ_{fajl}"))
            print(f"GOTOVO: {fajl}")

        except Exception as e:
            print(f"Greska: {str(e)}")

    if os.name == 'nt': os.startfile(izlaz)


def main():
    pokreni_analizu()

if __name__ == "__main__":
    pokreni_analizu()
