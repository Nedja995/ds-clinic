import os
import sys
import argparse
from npy.core.logger import setup_logger
from npy.core import utils
import config
from dsclinic import analyze_inputs_and_export_report
from api_claude import client as api_claude_client
from api_claude import utils as api_claude_utils
from models import ClaudeAIServiceConfig, ClaudeModelConfig
from npy.core.fileutils import find_input_documents, make_output_filepath, read_debug_sample_response_json, write_response_json


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
    logger.info("="*60)
    
    input_dir = os.path.join(base_dir, args.input)
    output_dir = os.path.join(base_dir, args.output)

    try:
        # Pozivamo glavnu logiku iz dsclinic.py
        # analyze_inputs_and_export_report(
        #     input_dir=input_dir,
        #     output_dir=output_dir,
        #     model_name=config.AI_MODEL_NAME,
        #     debug_response=args.debug_response,
        # )
        
        client_config = ClaudeAIServiceConfig(
            api_key=config.ANTHROPIC_API_KEY,
            model_settings=ClaudeModelConfig(model_name=config.CLAUDE_MODEL_NAME)
        )
        claude_client = api_claude_client.ClaudeAnalyzerClient(config=client_config)

        # Load docs — same call, different return type (dict vs Part), same interface:
        input_files = find_input_documents(input_dir)
        input_documents_parts = [api_claude_utils.load_document_from_file(fp) for fp in input_files]

        # Same downstream call:
        report = claude_client.initial_analysis_report_from_chat_stream(input_documents_parts, "".join(config.AI_TASK_DESCRIPTION))
        logger.info(report)

    except Exception as e:
        logger.critical(f"Greška tokom izvršavanja: {str(e)}", exc_info=True)
        print("Enter to exit...")
        input()  # Dodato da se konzola ne zatvori odmah
        sys.exit(1)


if __name__ == "__main__":
    main()
    print("Enter to exit...")
    input()
    sys.exit(0)
