##
#
#
import os
#
from fpdf import FPDF
#
from src import word_utils
 

class ReportPDF(FPDF):
    def header(self):
        # Title
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(0, 51, 102) # Dark Blue
        self.cell(0, 10, 'HOLISTICKI CENTAR DAR PRIRODE', 0, 1, 'C')
        self.ln(5)
        
        # Border line
        self.set_draw_color(180, 180, 180)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(10)

    def draw_table(self, data: dict = {}):
        # Column widths
        w = [95, 95]
        
        # Header
        self.set_font('Helvetica', 'B', 10)
        self.set_fill_color(240, 240, 240)
        self.set_text_color(0, 0, 0)
        self.cell(w[0], 10, ' Ekspertsko misljenje', 1, 0, 'L', True)
        self.cell(w[1], 10, ' Parametar aparata (Original)', 1, 1, 'L', True)
        
        # Rows
        self.set_font('Helvetica', '', 9)
        for k, v in data.items():
            # Calculate height based on multi-cell content
            h = 10
            # Basic version for simplicity; fpdf2 would handle wrapping better
            self.cell(w[0], h, f" {k}", 1, 0, 'L')
            self.cell(w[1], h, f" {v}", 1, 1, 'L')

def create_report(ime_pacijenta: str = "NEPOZNATO", 
                  date: str = "NEPOZNATO", 
                  preporucena_terapija_i_savet: str = "NEMA SAVETA",
                  dijagnoza_summarized: str = "NEPOZNATA DIJAGNOZA",
                  dijagnoza: str = None,
                  dijagnoze_i_objasenjenja: dict = {}, 
                  protocols_found: list = [],
                  output_dir: str = "") -> FPDF:
    
    text_pacijent: str = f"Pacijent: {ime_pacijenta}"
    # nalazi = [
    # ("Povecan ocni pritisak (Glaukom)", "02.06.25 Glaucoma / glaucoma ( GLC1A gene) D=1,433"),
    # ("Manjak vitamina B2", "02.06.25 Vitamin B2, riboflavin D=1,452"),
    # ]

    pdf = ReportPDF()
    # font_path = "~/Library/Fonts/Arial Unicode.ttf" # Update with actual path to Arial Unicode font on your system
    # pdf.add_font("Arial_Unicode", "", font_path, uni=True) 
    # pdf.add_font("Arial_Unicode", uni=True)
    # pdf.set_font("Arial_Unicode", "", 12)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Patient Info
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(100, 10, text_pacijent, 0, 0)
    pdf.cell(90, 10, date, 0, 1, 'R')
    pdf.ln(5)
    
    # Table of findings
    pdf.draw_table(dijagnoze_i_objasenjenja)
    pdf.ln(10)
    
    # Recommendations section
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(200, 0, 0) # Reddish
    pdf.cell(0, 10, 'PREPORUCENA TERAPIJA I SAVET:', 0, 1)
    
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 6, preporucena_terapija_i_savet)
    pdf.ln(10)

     # Dijagnoza summarized section
    if dijagnoza:
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(200, 0, 0) # Reddish
        pdf.cell(0, 10, 'DIJAGNOZA:', 0, 1)
        
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 6, dijagnoza)
        pdf.ln(10)

    # Dijagnoza section
    if dijagnoza_summarized:
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(200, 0, 0) # Reddish
        pdf.cell(0, 10, 'DIJAGNOZA 2:', 0, 1)
        
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 6, dijagnoza_summarized)
        pdf.ln(10)
    
    # Consent
    pdf.set_font('Helvetica', 'I', 9)
    pdf.multi_cell(0, 5, "SAGLASNOST: Pacijent je upoznat sa metodom, preporucenom terapijom i istu u potpunosti prihvata.")
    pdf.ln(5)
    
    # Note
    pdf.set_font('Helvetica', 'I', 9)
    pdf.multi_cell(0, 5, "NAPOMENA: Rezultati su holisticki uvid. Za medicinske dijagnoze konsultujte svog lekara.")
    
    # Signature
    pdf.ln(20)
    curr_y = pdf.get_y()
    pdf.line(140, curr_y, 195, curr_y)
    pdf.set_xy(140, curr_y + 2)
    pdf.set_font('Helvetica', 'I', 8)
    pdf.cell(55, 5, 'M.P. Potpis terapeuta', 0, 0, 'C')
    
    return pdf

def write_report_file(pdf: FPDF, output_path: str = ""):
    #pdf.output(output_path)
    #print(f"PDF generated successfully: {output_path}")
    
    # CLOSE FILE FIX
    pdf_bytes = pdf.output(dest='S').encode('latin-1') # Returns bytes 

    with open(output_path, "wb") as f:
        f.write(pdf_bytes)

    # Optional: Verify file exists using os utils
    if os.path.exists(output_path):
        print(f"PDF generated successfully: {output_path}")
        



def generate_report_pdf(document_name: str, protocols_found: list = [], output_dir: str = ""):
    output_path = os.path.join(output_dir, f"NALAZ_{document_name}.pdf")
    
    # Output dir
    os.makedirs(output_dir, exist_ok=True)

    ## PDF GENERATION
    pdf_novi = ReportPDF()
    pdf_novi.set_auto_page_break(auto=True, margin=15)
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
            pdf_novi.cell(0, 10, word_utils.sredi_slova(f"NALAZ: {p['nalaz']}"), ln=True)

            # Column 2 - TERAPIJA
            pdf_novi.set_font("Helvetica", '', 10)
            for t in p['terapija']:
                pdf_novi.cell(10)
                pdf_novi.cell(0, 7, f"- {word_utils.sredi_slova(t)}", ln=True)

            # Column 3 - NAPOMENA
            pdf_novi.set_font("Helvetica", 'I', 9)
            pdf_novi.multi_cell(0, 7, word_utils.sredi_slova(f"Vazno: {p['napomena']}"))
            pdf_novi.ln(5)
    else:
        ## NEMA PRONADJENIH PROTOKOLA
        #
        pdf_novi.cell(0, 10, "Nisu detektovani specificni patogeni iz baze.", ln=True)

    pdf_novi.output(output_path)

    print(f"GOTOVO: {output_path}")
