import os
import pdfplumber
from fpdf import FPDF

## SCRIPT PARAMETERS
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

## APP PARAMETERS
DATA_DIR = ROOT_DIR
INPUT_DIR = os.path.join(DATA_DIR, "ULAZ")
OUTPUT_DIR = os.path.join(DATA_DIR, "IZVESTAJI")

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