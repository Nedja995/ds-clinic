import os
import datetime
from fpdf import FPDF
 
def sredi_slova(text):
    mape = {"č": "c", "ć": "c", "ž": "z", "š": "s", "đ": "dj", "Č": "C", "Ć": "C", "Ž": "Z", "Š": "S", "Đ": "Dj"}
    for k, v in mape.items(): text = text.replace(k, v)
    return text


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

    def draw_table(self, data):
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
        for row in data:
            # Calculate height based on multi-cell content
            h = 10
            # Basic version for simplicity; fpdf2 would handle wrapping better
            self.cell(w[0], h, f" {row[0]}", 1, 0, 'L')
            self.cell(w[1], h, f" {row[1]}", 1, 1, 'L')

def create_report(patient_name: str = "NEPOZNATO", 
                  birthdate: str = "NEPOZNATO", 
                  advice: str = "NEMA SAVETA",
                  dijagnoze_i_objasenjenja: dict = {}, 
                  protocols_found: list = [],
                  output_dir: str = ""):
    '''
    Exports protocols to PDF report.
    
    Protocols should be in format: [{"nalaz": str, "terapija": list, "napomena": str}, ...]
    
    :param document_name: Description
    :type document_name: str
    :param protocols_found: Description
    :type protocols_found: list
    :param output_dir: Description
    :type output_dir: str
    '''
    text_pacijent: str = f"Pacijent: {patient_name}"
    text_datum: str = birthdate
    text_savet: str = "NEMA SAVETA" if not advice else advice
    # nalazi = [
    # ("Povecan ocni pritisak (Glaukom)", "02.06.25 Glaucoma / glaucoma ( GLC1A gene) D=1,433"),
    # ("Manjak vitamina B2", "02.06.25 Vitamin B2, riboflavin D=1,452"),
    # ]
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    output_path = os.path.join(output_dir, f"NALAZ_{patient_name}_{timestamp_str}.pdf")
    
    # Output dir
    os.makedirs(output_dir, exist_ok=True)

    pdf = ReportPDF()
    # font_path = "~/Library/Fonts/Arial Unicode.ttf" # Update with actual path to Arial Unicode font on your system
    # pdf.add_font("Arial_Unicode", "", font_path, uni=True) 
    # pdf.set_font("Arial_Unicode", "", 12)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Patient Info
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(100, 10, text_pacijent, 0, 0)
    pdf.cell(90, 10, text_datum, 0, 1, 'R')
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
    pdf.multi_cell(0, 6, text_savet)
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
    
    pdf.output(output_path)
    print(f"PDF generated successfully: {output_path}")


def generate_report_pdf(document_name: str, protocols_found: list = [], output_dir: str = ""):
    '''
    Exports protocols to PDF report.
    
    Protocols should be in format: [{"nalaz": str, "terapija": list, "napomena": str}, ...]
    
    :param document_name: Description
    :type document_name: str
    :param protocols_found: Description
    :type protocols_found: list
    :param output_dir: Description
    :type output_dir: str
    '''
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

    pdf_novi.output(output_path)

    print(f"GOTOVO: {output_path}")
