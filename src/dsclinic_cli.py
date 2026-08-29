import os
import sys
import argparse
from npy.core.logger import setup_logger
from npy.core import utils
from models import app_settings, MedicalReport, MedicalReportModel
from dsclinic import DSClinic, write_report_pdf
from npy.core import fileutils as fileutils

def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments for the DSClinic application.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="DSClinic AI - Alat za analizu medicinskih izveštaja (Laboratorija i NLS)",
        epilog=
        """
        Primer korišćenja:\n
        DSClinic.exe --input ./ULAZ --output ./IZVESTAJI -d (za pokretanje u debug modu)
        """,
    )

    # Dodavanje argumenata
    parser.add_argument("-i", "--input", type=str, default="ULAZ", help="Putanja do foldera sa ulaznim fajlovima")
    parser.add_argument("-o", "--output", type=str, default="IZVESTAJI", help="Putanja do foldera za čuvanje PDF izveštaja")
    parser.add_argument("-v", "--verbose", action="store_true", help="Prikaži detaljne (DEBUG) logove u konzoli")
    parser.add_argument("-dr", "--debug-response", action="store_true", help="Pokreni u debug modu (čita lokalni JSON umesto API poziva)")
    parser.add_argument("-de", "--debug-export-response", action="store_true", help="Izvezi dobijeni JSON odgovor u fajl.")
    parser.add_argument("-mn", "--model-name", type=str, default=app_settings.ai_model_name, help="Naziv AI modela koji će se koristiti za analizu")

    return parser.parse_args()


def main():
    args = parse_arguments()

    log_level = app_settings.app_log_level
    # Inicijalizacija loggera
    logger = setup_logger(level=log_level)

    # Podešavanje logovanja na osnovu argumenata
    logger.setLevel(log_level)

    # App start message
    logger.info("="*60)
    logger.info(f" DSClinic running with parameters:\n")
    # Pravljenje apsolutnih putanja pomoću PyInstaller-safe funkcije
    base_dir = utils.get_base_dir_path()
    logger.info(f"{' ' * 3}- Root directory: {base_dir}.")
    logger.info(f"{' ' * 3}- Run arguments: {args}.")
    logger.info("="*60)
    
    input_dir = os.path.join(base_dir, args.input)
    output_dir = os.path.join(base_dir, args.output)
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    
    report: MedicalReport = None
    response_json = {}
    report_model: MedicalReportModel = None
    debug_response = app_settings.app_debug_response or args.debug_response
    debug_export_response = False if debug_response else (app_settings.app_debug_export_response or args.debug_export_response)
    
    ## With Gemini
    if not debug_response:
        ## Run gemini analysis
        dsclinic = DSClinic(model_name=args.model_name)
        report = dsclinic.get_initial_analysis_report()
    
        if debug_export_response and response_json:
            # DEBUG: STORE JSON RESPONSE
            fileutils.write_response_json(report.content.patient_name, response_json, os.path.join(output_dir, "DEBUG"))
    else:
        # DEBUG: Čita iz lokalnog fajla
        response_json = fileutils.read_debug_sample_response_json()
        report_content = MedicalReportModel.model_validate(response_json)
        report = MedicalReport(content=report_content)
    
    write_report_pdf(report, output_dir)
    fileutils.open_file_from_filepath(output_dir)


if __name__ == "__main__":
    main()
    print("Enter to exit...")
    input()
    sys.exit(0)
