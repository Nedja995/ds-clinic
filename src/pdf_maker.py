"""
pdf_maker.py — PDF report generation for DSClinic.

Owns all FPDF2 layout logic: fonts, header, patient info, findings table,
therapy table, chat responses, footer, and watermark.
Reads all clinic identity from brand_config (AD-20) — never hardcodes
clinic name, logo path, colors, or footer text.
Does NOT own data validation or AI output parsing.
"""
import logging
import os
import sys
from datetime import datetime

from fpdf import FPDF
from fpdf import enums as FPDFEnums
from models import MedicalReport, MedicalReportModel, MedicalCriticalFindingModel, MedicalTherapyModel
from models.brand import brand_config
from npy.core import utils
from npy.core.logger import setup_logger

logger = setup_logger()

########################  FONTS  ############################

FONTS_DIR = utils.get_resource_dirpath("fonts")
logger.info(f"Fonts directory: {FONTS_DIR}")
if not os.path.exists(FONTS_DIR):
    raise Exception(f"Missing resource fonts directory at: '{FONTS_DIR}'.")

CONST_FONTS: dict[str, dict[str, str]] = {
    "Normal":     {"name": "Arial Unicode MS",              "filename": "Arial-Unicode-Regular.ttf"     },
    "Bold":       {"name": "Arial Unicode MS Bold",         "filename": "Arial-Unicode-Bold.ttf"        },
    "Italic":     {"name": "Arial Unicode MS Italic",       "filename": "Arial-Unicode-Italic.ttf"      },
    "BoldItalic": {"name": "Arial-Unicode-Bold-Italic.ttf", "filename": "Arial-Unicode-Bold-Italic.ttf" },
}

FONT_NORMAL     = CONST_FONTS["Normal"]["name"]
FONT_BOLD       = CONST_FONTS["Bold"]["name"]
FONT_ITALIC     = CONST_FONTS["Italic"]["name"]
FONT_BOLD_ITALIC = CONST_FONTS["BoldItalic"]["name"]


class HolisticReport(FPDF):
    def __init__(self, *args, **kwargs):
        logger.info("Initializing PDF generator...")
        super().__init__(orientation="p", unit="mm", format="A4", *args, **kwargs)

        logger.info("  - Configuring Unicode Fonts...")
        self.add_font(FONT_NORMAL,     "", os.path.join(FONTS_DIR, CONST_FONTS["Normal"]["filename"]))
        self.add_font(FONT_BOLD,       "", os.path.join(FONTS_DIR, CONST_FONTS["Bold"]["filename"]))
        self.add_font(FONT_ITALIC,     "", os.path.join(FONTS_DIR, CONST_FONTS["Italic"]["filename"]))
        self.add_font(FONT_BOLD_ITALIC,"", os.path.join(FONTS_DIR, CONST_FONTS["BoldItalic"]["filename"]))
        self.set_font(FONT_NORMAL, "", 10)

        self.add_page()

    def draw_header(self) -> None:
        """
        Draws the branded clinic header. All identity strings and colors come
        from brand_config — no hardcoded clinic name or color values (AD-20).
        """
        row_height_mm = 20
        primary_r, primary_g, primary_b = brand_config.primary_color_rgb()

        # Clinic name — sourced from BrandConfig, not hardcoded
        self.set_font(FONT_BOLD, "", 16)
        self.set_text_color(primary_r, primary_g, primary_b)
        self.set_fill_color(235, 235, 235)
        self.cell(
            0, row_height_mm, brand_config.clinic_name,
            align="C", ln=True, new_x="LMARGIN", new_y="NEXT", fill=False,
        )

        # Optional subtitle line below clinic name
        if brand_config.report_header_text:
            self.set_font(FONT_ITALIC, "", 10)
            self.set_text_color(80, 80, 80)
            self.cell(0, 6, brand_config.report_header_text, align="C", ln=True, new_x="LMARGIN", new_y="NEXT")

        # Logo — resolved at render time; skipped gracefully when path is absent
        logo_abs_path = brand_config.resolved_logo_path()
        if logo_abs_path:
            logo_size_mm = 28.0
            logo_x = logo_size_mm / 2
            logo_y = self.get_y() - logo_size_mm - 1
            self.image(logo_abs_path, x=logo_x, y=logo_y, w=logo_size_mm, h=logo_size_mm, keep_aspect_ratio=True)

        # Horizontal rule
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.4)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(8)

    def draw_patient_info(self, name: str = "/", date: str = "/") -> None:
        """Draws the patient's name and the report date on the PDF."""
        self.set_font(FONT_BOLD, "", 11)
        self.set_text_color(0, 0, 0)

        curr_y = self.get_y()
        self.set_xy(10, curr_y)
        self.cell(100, 5, f"Pacijent: {name.upper()}")

        self.set_xy(10, curr_y)
        self.cell(190, 5, f"Datum: {date}", align="R", ln=True)
        self.ln(8)

    def draw_table_foundings(self, data: list[MedicalCriticalFindingModel] | None = []) -> None:
        """
        Draws a table of medical critical findings.
        Table header fill uses brand_config secondary_color (AD-20).
        """
        col1_width   = 85
        col2_width   = 105
        header_height = 10
        line_height  = 5

        secondary_r, secondary_g, secondary_b = brand_config.secondary_color_rgb()

        self.set_font(FONT_BOLD, "", 10)
        self.set_fill_color(secondary_r, secondary_g, secondary_b)
        self.set_draw_color(50, 50, 50)

        self.cell(col1_width, header_height, " Ekspertsko mišljenje", border=1, fill=True)
        self.cell(col2_width, header_height, " Parametar aparata (Original)", border=1, fill=True, ln=True)

        self.set_font(FONT_NORMAL, "", 10)
        c_margin = getattr(self, "c_margin", 1)

        def get_lines(text, max_w: float) -> list[int]:
            if not text:
                return 1
            lines = 0
            for paragraph in text.split('\n'):
                words = paragraph.split(' ')
                current_line = ""
                for word in words:
                    if current_line == "":
                        current_line = word
                    else:
                        test_line = current_line + " " + word
                        if self.get_string_width(test_line) > max_w:
                            lines += 1
                            current_line = word
                        else:
                            current_line = test_line
                lines += 1
            return lines

        for item in data:
            misljenje = f"{item.expertsko_misljenje}"
            parametar = f"{item.parametar_and_value}"

            lines1 = get_lines(misljenje, col1_width - 2 * c_margin - 1)
            lines2 = get_lines(parametar, col2_width - 2 * c_margin - 1)
            max_lines = max(lines1, lines2)
            row_height = max_lines * line_height + 4

            page_bottom = getattr(self, "page_break_trigger", self.h - self.b_margin)
            if self.get_y() + row_height > page_bottom:
                self.add_page()

            x = self.get_x()
            y = self.get_y()

            self.rect(x, y, col1_width, row_height)
            self.rect(x + col1_width, y, col2_width, row_height)

            self.set_xy(x, y + 2)
            self.multi_cell(col1_width, line_height, misljenje, border=0, align="L")

            self.set_xy(x + col1_width, y + 2)
            self.multi_cell(col2_width, line_height, parametar, border=0, align="L")

            self.set_xy(x, y + row_height)

        self.ln(10)

    def draw_recommended_therapy_section(self, terapija_i_savet: str) -> None:
        """Draws the recommended therapy and advice section."""
        self.set_font(FONT_BOLD, "", 12)
        self.set_text_color(160, 0, 0)
        self.cell(0, 10, "PREPORUCENA TERAPIJA I SAVET:", ln=True)

        self.set_font(FONT_NORMAL, "", 11)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, terapija_i_savet)
        self.ln(6)

    def draw_table_therapy(self, data: list[MedicalTherapyModel] | None = []) -> None:
        """
        Draws the therapy table.
        Table header fill uses brand_config secondary_color (AD-20).
        """
        col1_width   = 85
        col2_width   = 105
        header_height = 10
        line_height  = 5

        secondary_r, secondary_g, secondary_b = brand_config.secondary_color_rgb()

        self.set_font(FONT_BOLD, "", 12)
        self.set_text_color(160, 0, 0)
        self.cell(0, 10, "TERAPIJA:", ln=True)
        self.set_text_color(0, 0, 0)

        self.set_font(FONT_BOLD, "", 10)
        self.set_fill_color(secondary_r, secondary_g, secondary_b)
        self.set_draw_color(50, 50, 50)

        self.cell(col1_width, header_height, " Naziv Artikla", border=1, fill=True)
        self.cell(col2_width, header_height, " Primena Terapije", border=1, fill=True, ln=True)

        self.set_font(FONT_NORMAL, "", 10)
        c_margin = getattr(self, "c_margin", 1)

        def get_lines(text, max_w: float) -> list[int]:
            if not text:
                return 1
            lines = 0
            for paragraph in text.split('\n'):
                words = paragraph.split(' ')
                current_line = ""
                for word in words:
                    if current_line == "":
                        current_line = word
                    else:
                        test_line = current_line + " " + word
                        if self.get_string_width(test_line) > max_w:
                            lines += 1
                            current_line = word
                        else:
                            current_line = test_line
                lines += 1
            return lines

        for item in data:
            misljenje = f"{item.article}"
            parametar = f"{item.using_instructions}"

            lines1 = get_lines(misljenje, col1_width - 2 * c_margin - 1)
            lines2 = get_lines(parametar, col2_width - 2 * c_margin - 1)
            max_lines = max(lines1, lines2)
            row_height = max_lines * line_height + 4

            page_bottom = getattr(self, "page_break_trigger", self.h - self.b_margin)
            if self.get_y() + row_height > page_bottom:
                self.add_page()

            x = self.get_x()
            y = self.get_y()

            self.rect(x, y, col1_width, row_height)
            self.rect(x + col1_width, y, col2_width, row_height)

            self.set_xy(x, y + 2)
            self.multi_cell(col1_width, line_height, misljenje, border=0, align="L")

            self.set_xy(x + col1_width, y + 2)
            self.multi_cell(col2_width, line_height, parametar, border=0, align="L")

            self.set_xy(x, y + row_height)

        self.ln(10)

    def draw_chat_responses(self, chat_responses: list[str]) -> None:
        """Draws additional AI chat responses appended after the main report."""
        self.set_font(FONT_BOLD, "", 12)
        self.set_text_color(160, 0, 0)
        self.cell(0, 10, "DODATNA ANALIZA:", ln=True)

        self.set_font(FONT_NORMAL, "", 11)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, "\n".join(chat_responses))
        self.ln(6)

    def draw_footer_section(self) -> None:
        """
        Draws the consent and disclaimer footer.
        Text sourced from brand_config — white-label deployments supply
        jurisdiction-appropriate wording via brand.json (AD-20).
        """
        self.set_font(FONT_ITALIC, "", 10)
        self.multi_cell(0, 6, brand_config.report_consent_text)
        self.ln(4)

        self.set_font(FONT_ITALIC, "", 9)
        self.multi_cell(0, 5, brand_config.report_footer_text)

        # Signature line — right-aligned
        self.ln(20)
        line_start = 140
        line_end   = 195
        curr_y = self.get_y()
        self.line(line_start, curr_y, line_end, curr_y)

        self.set_x(line_start)
        self.set_font(FONT_ITALIC, "", 9)
        self.cell(line_end - line_start, 8, "M.P. Potpis terapeuta", align="C")

    def draw_watermark(self) -> None:
        """
        Renders a diagonal "TRIAL" stamp across the page center.
        Called on every page when the subscription tier does not allow
        the no_watermark feature (AD-20, v2.11.2).
        FPDF2 has no true alpha channel; light gray approximates transparency.
        """
        self.set_font(FONT_BOLD, "", 60)
        self.set_text_color(220, 220, 220)
        with self.rotation(45, x=self.w / 2, y=self.h / 2):
            self.text(x=self.w / 2 - 60, y=self.h / 2, txt="TRIAL")
        # Reset text color so subsequent drawing is unaffected
        self.set_text_color(0, 0, 0)


######################### PDF Output Functions ########################

def create_report_pdf(report: MedicalReport) -> HolisticReport:
    """
    Creates a fully branded PDF report from a MedicalReport object.
    Watermark is applied when the subscription tier denies no_watermark (AD-20).
    """
    pdf = HolisticReport()

    pdf.draw_header()
    pdf.draw_patient_info(report.content.patient_name, report.report_date)

    if len(report.content.critical_findings) > 0:
        pdf.draw_table_foundings(report.content.critical_findings)

    if len(report.content.recommended_therapy_and_advice) > 0:
        pdf.draw_recommended_therapy_section(report.content.recommended_therapy_and_advice)

    if len(report.therapies) > 0:
        pdf.draw_table_therapy(report.therapies)

    pdf.draw_footer_section()

    if len(report.chat_responses) > 0:
        pdf.draw_chat_responses(report.chat_responses)

    # Trial tier: stamp every page with a watermark after content is laid out
    if not brand_config.is_feature_allowed("no_watermark"):
        for page_num in range(1, pdf.page + 1):
            pdf.page = page_num
            pdf.draw_watermark()
        # Restore cursor to last page so .output() / .buffer works correctly
        pdf.page = pdf.pages

    return pdf


def create_report_pdf_bytes(report: MedicalReport) -> bytes:
    """Creates a PDF report and returns it as bytes."""
    pdf = create_report_pdf(report)
    data = pdf.buffer
    logger.info(f"Report generated (bytes): {len(data)}")
    return data


def generate_report_pdf_at_filepath(report: MedicalReport, output_filename: str = "report.pdf") -> None:
    """Generates a PDF report and saves it to a file."""
    pdf = create_report_pdf(report)
    pdf.output(output_filename)
    logger.info(f"Report generated: {output_filename}")


# --- Example Usage ---
if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)

    data_input = [
        MedicalCriticalFindingModel(misljenje="Povećan očni pritisak (Glaukom) i jos neki poremecaj da bude sto duzi text ovde blab bla htrh rh rthrh rh r.",
                   parametar="02.06.25 Glaucoma / glaucoma ( GLC1A gene) D=1,433"),
        MedicalCriticalFindingModel(misljenje="Manjak vitamina B2",
                   parametar="02.06.25 Vitamin B2, riboflavin D=1,452"),
        MedicalCriticalFindingModel(misljenje="Poremecaj funkcije debelog creva (Moguci Kolitis)",
                   parametar="02.06.25 Large Intestine ( DD ) D=1,419"),
        MedicalCriticalFindingModel(misljenje="Upalni procesi besike",
                   parametar="02.06.25 Bladder Meridian (BL) D=1,409 a i ovde za parametar da probamo sa dugackim texto neki nesto hhahahfd dsfsdfsd fs sd."),
        MedicalCriticalFindingModel(misljenje="Deficit vitamina B12 (Rizik od anemije)",
                   parametar="02.06.25 Vitamin B12 , cobalamin D=1,400"),
    ]

    output_path = os.path.join('.', f"sample_output_report_{datetime.now().strftime('%Y%m%d_%H-%M')}.pdf")

    generate_report_pdf_at_filepath(MedicalReport(
        patient_name="DRAGAN STAMENOVIĆ",
        report_date="12.02.2026",
        terapija_i_saveti="Nastaviti sa biljnim kapima po dogovoru. Kontrola za 3 nedelje.",
        critical_findings=data_input
    ), output_filename=output_path)
