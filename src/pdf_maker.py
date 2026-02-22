##
# PDF Maker
#
import os
from typing import List

from fpdf import FPDF
from fpdf import enums as FPDFEnums
from datetime import datetime
from src.models import ReportItem


CONST_FONTS_DIR = os.path.join("fonts")
if not os.path.exists(CONST_FONTS_DIR):
    raise Exception("Missing resource fonts.")

CONST_FONTS: dict = {
    # "Normal": { "name": "DejaVu", "filename": "DejaVuSans.ttf", "file_path": os.path.join(CONST_FONTS_DIR, "DejaVuSans.ttf") },
    # "Bold": { "name": "DejaVu-Bold", "filename": "DejaVuSans-Bold.ttf", "file_path": os.path.join(CONST_FONTS_DIR, "DejaVuSans-Bold.ttf")},
    # "Italic": { "name": "DejaVu-Oblique", "filename": "DejaVuSans-Oblique.ttf", "file_path": os.path.join(CONST_FONTS_DIR, "DejaVuSans-Oblique.ttf")},
    # "BoldItalic": { "name": "DejaVu-BoldOblique", "filename": "DejaVuSans-BoldOblique.ttf", "file_path": os.path.join(CONST_FONTS_DIR, "DejaVuSans-BoldOblique.ttf")},
    "Normal": {"name": "Arial Unicode MS", "filename": "Arial-Unicode-Regular.ttf", "file_path": os.path.join(CONST_FONTS_DIR, "Arial-Unicode-Regular.ttf")},
    "Bold": {"name": "Arial Unicode MS Bold", "filename": "Arial-Unicode-Bold.ttf", "file_path": os.path.join(CONST_FONTS_DIR, "Arial-Unicode-Bold.ttf")},
    "Italic": {"name": "Arial Unicode MS Italic", "filename": "Arial-Unicode-Italic.ttf", "file_path": os.path.join(CONST_FONTS_DIR, "Arial-Unicode-Italic.ttf")},
    "BoldItalic": {"name": "Arial-Unicode-Bold-Italic.ttf", "filename": "Arial-Unicode-Bold-Italic.ttf", "file_path": os.path.join(CONST_FONTS_DIR, "Arial-Unicode-Bold-Italic.ttf")},
}

FONT_NORMAL = CONST_FONTS["Normal"]["name"]
FONT_BOLD = CONST_FONTS["Bold"]["name"]
FONT_ITALIC = CONST_FONTS["Italic"]["name"]
FONT_BOLD_ITALIC = CONST_FONTS["BoldItalic"]["name"]


class HolisticReport(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 2. Configure Unicode Fonts
        self.add_font(FONT_NORMAL, "", CONST_FONTS["Normal"]["file_path"])
        self.add_font(FONT_BOLD, "", CONST_FONTS["Bold"]["file_path"])
        self.add_font(FONT_ITALIC, "", CONST_FONTS["Italic"]["file_path"])
        self.add_font(FONT_BOLD_ITALIC, "", CONST_FONTS["BoldItalic"]["file_path"])
        self.set_font(FONT_NORMAL, "", 10)

        self.add_page()
        # self.set_auto_page_break(auto=True, margin=15)

    def draw_header(self):
        # Top Title
        self.set_font(FONT_BOLD, "", 16)
        self.set_text_color(0, 51, 102)
        self.cell(0, 15, "HOLISTIČKI CENTAR DAR PRIRODE", align="C", ln=True, new_x="LMARGIN", new_y="NEXT")

        # Horizontal Line
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.4)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(8)  # Razmak nakon linije do pacijenta

    def draw_patient_info(self, name: str, date: str):
        self.set_font(FONT_BOLD, "", 11)
        self.set_text_color(0, 0, 0)

        # Pacijent i Datum u istom redu sa minimalnim razmakom
        curr_y = self.get_y()
        self.set_xy(10, curr_y)
        self.cell(100, 5, f"Pacijent: {name.upper()}")

        self.set_xy(10, curr_y)
        self.cell(190, 5, f"Datum: {date}", align="R", ln=True)
        self.ln(8)  # Razmak do tabele

    def draw_table(self, data: List[ReportItem] = []):
        # Definicija širina kolona (ukupno 190mm za A4)
        col1_width = 85
        col2_width = 105
        row_height = 10  # Povećana visina ćelije prema vašem zahtevu

        # --- ZAGLAVLJE TABELE ---
        self.set_font(FONT_BOLD, "", 10)
        self.set_fill_color(235, 235, 235)  # Svetlo siva boja
        self.set_draw_color(50, 50, 50)    # Boja ivica

        self.cell(col1_width, row_height, " Ekspertsko mišljenje", border=1, fill=True)
        self.cell(col2_width, row_height, " Parametar aparata (Original)", border=1, fill=True, ln=True)

        # --- PODACI TABELE ---
        self.set_font(FONT_NORMAL, "", 10)
        i = 0
        for item in data:
            # if i == 0:
            #     i = i + 2
            #     item.misljenje = "fsdfsd fs sdf sfsd fsd fsd fsdfsd sd sd fsdf sdf s fsd sd sd fsdf sdf sdf sdfsdf sdfsdsfsdf sdf sdf dsfssdfsdf sdfsdfsdf sdf sddsfsdfsd"
            # Koristimo cell za fiksnu visinu ili multi_cell ako je tekst predugačak
            # Ovde koristimo cell jer su podaci kratki, ali sa paddingom
            if len(item.misljenje) > 50: item.misljenje = item.misljenje[:50]
            if len(item.parametar) > 50: item.parametar = item.parametar[:50]
                # x = self.get_x()
                # y = self.get_y()
                # # Move to top right of the first cell
                # #self.set_xy(x + col1_width, y)
                # self.multi_cell(0, 0, f" {item.misljenje}", border=1, ln=3)
                # # 3. Reset position for the second cell
                # # Move X to (start + width of first cell) and Y back to start
                # self.set_xy(x + col1_width, y)
                # self.multi_cell(0, 6, f" {item.parametar}", border=1, ln=2)
            #else:
            self.cell(col1_width, row_height, f" {item.misljenje}", border=1)
            self.cell(col2_width, row_height, f" {item.parametar}", border=1, ln=True)

        self.ln(10)

    def draw_footer_section(self, terapija_i_savet: str):
        # Preporuka (Crvena boja)
        self.set_font(FONT_BOLD, "", 12)
        self.set_text_color(160, 0, 0)
        self.cell(0, 10, "PREPORUCENA TERAPIJA I SAVET:", ln=True)

        # Tekst terapije
        self.set_font(FONT_NORMAL, "", 11)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, terapija_i_savet)
        self.ln(6)

        # Saglasnost (Italic)
        self.set_font(FONT_ITALIC, "", 10)
        self.multi_cell(0, 6, "SAGLASNOST: Pacijent je upoznat sa metodom, preporucenom terapijom i istu u potpunosti prihvata.")
        self.ln(4)

        # Napomena (Italic)
        self.set_font(FONT_ITALIC, "", 9)
        self.multi_cell(0, 5, "NAPOMENA: Rezultati su holisticki uvid. Za medicinske dijagnoze konsultujte svog lekara.")

        # Potpis na dnu desno
        self.ln(20)
        line_start = 140
        line_end = 195
        curr_y = self.get_y()
        self.line(line_start, curr_y, line_end, curr_y)

        self.set_x(line_start)
        self.set_font(FONT_ITALIC, "", 9)
        self.cell(line_end - line_start, 8, "M.P. Potpis terapeuta", align="C")


def generate_report_pdf(
    patient_name: str = "NEPOZNATO IME PACIJENTA",
    report_date: str = "NEPOZNAT DATUM",
    terapija_i_saveti: str = "NEPOZNATA TERAPIJA I SAVET",
    table_data: List[ReportItem] = [],
    output_filename: str = "report.pdf"
):
    # Initialize PDF
    pdf = HolisticReport(orientation="P", unit="mm", format="A4")
    pdf.draw_header()
    pdf.draw_patient_info(patient_name, report_date)
    pdf.draw_table(table_data)
    pdf.draw_footer_section(terapija_i_saveti)

    # Output
    pdf.output(output_filename)
    print(f"Report generated: {output_filename}")


# --- Example Usage ---
if __name__ == "__main__":
    # Sample Data Input
    data_input = [
        ReportItem(misljenje="Povećan očni pritisak (Glaukom)",
                   parametar="02.06.25 Glaucoma / glaucoma ( GLC1A gene) D=1,433"),
        ReportItem(misljenje="Manjak vitamina B2",
                   parametar="02.06.25 Vitamin B2, riboflavin D=1,452"),
        ReportItem(misljenje="Poremecaj funkcije debelog creva (Moguci Kolitis)",
                   parametar="02.06.25 Large Intestine ( DD ) D=1,419"),
        ReportItem(misljenje="Upalni procesi besike",
                   parametar="02.06.25 Bladder Meridian (BL) D=1,409"),
        ReportItem(misljenje="Deficit vitamina B12 (Rizik od anemije)",
                   parametar="02.06.25 Vitamin B12 , cobalamin D=1,400"),
    ]

    output_path = os.path.join(
        '.', f"sample_output_report_{datetime.now().strftime("%Y%m%d_%H-%M")}.pdf")

    generate_report_pdf(
        patient_name="DRAGAN STAMENKOVIĆ",
        report_date="12.02.2026",
        terapija_i_saveti="Nastaviti sa biljnim kapima po dogovoru. Kontrola za 3 nedelje.",
        table_data=data_input,
        output_filename="report.pdf"
    )
