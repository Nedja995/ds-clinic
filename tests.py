import os
import pdfplumber
from fpdf import FPDF

## SCRIPT PARAMETERS
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

## APP PARAMETERS
DATA_DIR = ROOT_DIR
INPUT_DIR = os.path.join(DATA_DIR, "ULAZ")
OUTPUT_DIR = os.path.join(DATA_DIR, "IZVESTAJI")

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
                print(f"\n\n------------------\nText extracted from document {document}: {str(text)}")
        except Exception as e:
            print(f"Greska: {str(e)}")
        
        # ANALIZA TEXTA I NALAZAK PROTOKOLA
        #protokoli = analyze_content(text, BASE_SYNDROMS.VELIKA_BAZA)

        # GHENERISANJE IZVESTAJA
        #generate_report_pdf(document, protokoli, OUTPUT_DIR)
        # print(f"\n\n------------------\nText extracted from document {document}: {str(text)}")


    if os.name == 'nt': os.startfile(OUTPUT_DIR)

def main():
    # pokreni_analizu()
    pokreni_analizu()

if __name__ == "__main__":
    main()