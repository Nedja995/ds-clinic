import os
import pdfplumber
from fpdf import FPDF
from utils import BASE_SYNDROMS
from utils import api_gemini

#import warnings
#warnings.filterwarnings("ignore")

## SCRIPT PARAMETERS
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

## APP PARAMETERS
DATA_DIR = ROOT_DIR
INPUT_DIR = os.path.join(DATA_DIR, "ULAZ")
OUTPUT_DIR = os.path.join(DATA_DIR, "IZVESTAJI")


## UTILITIES

def sredi_slova(text):
    mape = {"č": "c", "ć": "c", "ž": "z", "š": "s", "đ": "dj", "Č": "C", "Ć": "C", "Ž": "Z", "Š": "S", "Đ": "Dj"}
    for k, v in mape.items(): text = text.replace(k, v)
    return text

# TRAZI DIJAGNOZE
def analyze_content(text: str = "", BASE_DICT: dict = {}) -> list:
    protocols_found : list = []

    for kljuc, podaci in BASE_DICT.items():
        if kljuc.upper() in text:
            protocols_found.append(podaci)

    return protocols_found

def generate_report_pdf(document_name: str, protocols_found: list = [], output_path: str = ""):
    # Output path correction
    if not output_path: output_path = os.path.join(OUTPUT_DIR, f"NALAZ_{document_name}")

    ## PDF GENERATION
    pdf_novi = FPDF()
    pdf_novi.add_page()

    # Page Title
    pdf_novi.set_font("Helvetica", 'B', 16)
    pdf_novi.cell(0, 10, "HOLISTICKI CENTAR DAR PRIRODE", align='C', ln=True)
    pdf_novi.ln(10)

    if protocols_found:
        ## PRONADJENI PROTOKOLI
        #
        # Table header
        pdf_novi.set_font("Helvetica", 'B', 12)
        pdf_novi.cell(0, 10, "PRONADJENA STANJA I TERAPIJE:", ln=True)
        pdf_novi.ln(5)

        # Table content
        for p in protocols_found:
            # Column 1 - NALAZ
            pdf_novi.set_font("Helvetica", 'B', 11)
            pdf_novi.cell(0, 10, sredi_slova(f"NALAZ: {p['nalaz']}"), ln=True)

            # Column 2 - TERAPIJA
            pdf_novi.set_font("Helvetica", '', 10)
            for t in p['terapija']:
                pdf_novi.cell(10)
                pdf_novi.cell(0, 7, f"- {sredi_slova(t)}", ln=True)

            # Column 3 - NAPOMENA
            pdf_novi.set_font("Helvetica", 'I', 9)
            pdf_novi.multi_cell(0, 7, sredi_slova(f"Vazno: {p['napomena']}"))
            pdf_novi.ln(5)
    else:
        ## NEMA PRONADJENIH PROTOKOLA
        #
        pdf_novi.cell(0, 10, "Nisu detektovani specificni patogeni iz baze.", ln=True)

    pdf_novi.output(os.path.join(OUTPUT_DIR, f"NALAZ_{document_name}"))

    print(f"GOTOVO: {pdf_novi}")


def pokreni_analizu():
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    if not os.path.exists(INPUT_DIR): os.makedirs(INPUT_DIR)
    
    # PRONALAZAK PDF FAJLOVA U FOLDERU
    doc_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.pdf')]
    
    for document in doc_files:
        text = ""
        # Citanje PDF-a
        try:
            with pdfplumber.open(os.path.join(INPUT_DIR, document)) as pdf:
                text = " ".join([s.extract_text() or "" for s in pdf.pages]).upper()
        except Exception as e:
            print(f"Greska: {str(e)}")

        # ANALIZA TEXTA I NALAZAK PROTOKOLA
        protokoli = analyze_content(text, BASE_SYNDROMS.VELIKA_BAZA)

        # GHENERISANJE IZVESTAJA
        generate_report_pdf(document, protokoli, OUTPUT_DIR)

    if os.name == 'nt': os.startfile(OUTPUT_DIR)

def pokreni_analizu_gemini():
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    if not os.path.exists(INPUT_DIR): os.makedirs(INPUT_DIR)
    
    # PRONALAZAK PDF FAJLOVA U FOLDERU
    documents_names = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.pdf')]
    documents_filepaths = [os.path.join(INPUT_DIR, f) for f in documents_names]

    try:
        gemini_client = api_gemini.gemini_client_connect()
        res = api_gemini.analyze_lab_result_docs(gemini_client, documents_filepaths[0], documents_filepaths[1])
        print(f"SUCCESS - RESPONSE: {res}")
    except Exception as e:
        print(f"ERROR - GOOGLE SERVICE: {str(e)}")

    # ANALIZA TEXTA I NALAZAK PROTOKOLA
    #protokoli = analyze_content(text, BASE_SYNDROMS.VELIKA_BAZA)

    # GHENERISANJE IZVESTAJA
    #generate_report_pdf(document, protokoli, OUTPUT_DIR)

    if os.name == 'nt': os.startfile(OUTPUT_DIR)



def main():
    # pokreni_analizu()
    pokreni_analizu_gemini()

if __name__ == "__main__":
    main()
