import os
import sys
import argparse
from npy.core.logger import setup_logger
from npy.core import utils
import config
from dsclinic import MedicalReport, MedicalReportModel, get_initial_analysis_report, write_report_pdf
# from api_claude import client as api_claude_client
# from api_claude import utils as api_claude_utils
# from models import ClaudeAIServiceConfig, ClaudeModelConfig
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
        #formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Dodavanje argumenata
    parser.add_argument("-i", "--input", type=str, default="ULAZ", help="Putanja do foldera sa ulaznim fajlovima")
    parser.add_argument("-o", "--output", type=str, default="IZVESTAJI", help="Putanja do foldera za čuvanje PDF izveštaja")
    parser.add_argument("-v", "--verbose", action="store_true", help="Prikaži detaljne (DEBUG) logove u konzoli")
    parser.add_argument("-dr", "--debug-response", action="store_true", help="Pokreni u debug modu (čita lokalni JSON umesto API poziva)")
    parser.add_argument("-de", "--debug-export-response", action="store_true", help="Izvezi dobijeni JSON odgovor u fajl.")
    parser.add_argument("-mn", "--model-name", type=str, default=config.AI_MODEL_NAME, help="Naziv AI modela koji će se koristiti za analizu")

    return parser.parse_args()


def main():
    # 
    args = parse_arguments()

    log_level = config.APP_LOG_LEVEL #logging.DEBUG if args.verbose else logging.INFO
    # Inicijalizacija loggera
    logger = setup_logger(level=log_level)

    # Podešavanje logovanja na osnovu argumenata
    logger.setLevel(log_level)

    # App start message
    logger.info("="*60)
    logger.info(f" DSClinic v{config.APP_VERSION} run with parameters:\n")
    # Pravljenje apsolutnih putanja pomoću PyInstaller-safe funkcije
    base_dir = utils.get_base_dir_path()
    logger.info(f"{' ' * 3}- Root directory: {base_dir}.")
    logger.info(f"{' ' * 3}- Run arguments: {args}.")
    logger.info("="*60)
    
    input_dir = os.path.join(base_dir, args.input)
    output_dir = os.path.join(base_dir, args.output)
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    
    #
    report: MedicalReport = None
    response_json = {}
    report_model: MedicalReportModel = None
    debug_response = config.APP_DEBUG_RESPONSE
    debug_export_response = False if debug_response else config.APP_DEBUG_EXPORT_RESPONSE
    
    ## With Gemini
    #
    if not debug_response:
        ## Run gemini analyzis
        report = get_initial_analysis_report(input_dir, args.model_name)
    
        if debug_export_response and response_json:
            # DEBUG: STORE JSON RESPONSE
            fileutils.write_response_json(report.content.patient_name, response_json, os.path.join(output_dir, "DEBUG"))
    else:
        # DEBUG: Čita iz lokalnog fajla
        response_json = fileutils.read_debug_sample_response_json()
        report_content = MedicalReportModel.model_validate(response_json)
        report = MedicalReport(content=report_content)
    # 
    write_report_pdf(report, output_dir)
    #
    fileutils.open_file_from_filepath(output_dir)
    
    ## With Claude
    #
    # client_config = ClaudeAIServiceConfig(
    #     api_key=config.ANTHROPIC_API_KEY,
    #     model_settings=ClaudeModelConfig(model_name=config.CLAUDE_MODEL_NAME)
    # )

    # claude_client = api_claude_client.ClaudeAnalyzerClient(config=client_config)
    
    # # Load docs — same call, different return type (dict vs Part), same interface:
    # input_files = find_input_documents(input_dir)
    # input_documents_parts = [api_claude_utils.load_document_from_file(fp) for fp in input_files]
    
    # # Same downstream call:
    # report = claude_client.initial_analysis_report_from_chat_stream(input_documents_parts, "".join(config.AI_TASK_DESCRIPTION))
    # logger.info(report)



if __name__ == "__main__":
    main()
    print("Enter to exit...")
    input()
    sys.exit(0)
