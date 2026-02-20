##
#
#
import os, sys, datetime
from typing import List
#
import src.api_gemini as api_gemini
import src.exporter as exporter
from src import word_utils
#
#import warnings
#warnings.filterwarnings("ignore")
#sys.stdout.reconfigure(encoding='utf-8')


## PROGRAM PARAMETERS
SCRIPT_FILE = sys.argv[0] #sys.executable #resource_path(".") #__file__
ROOT_DIR = os.path.dirname(os.path.abspath(SCRIPT_FILE))
# Data paths
DATA_DIR = ROOT_DIR
INPUT_DIR = os.path.join(DATA_DIR, "ULAZ")
OUTPUT_DIR = os.path.join(DATA_DIR, "IZVESTAJI")

print(f"\n---------- |DSCLINIC| Run programm with parameters: --------------")
print(f"\n---------- ROOT_DIR: ${ROOT_DIR}.")


def find_input_documents() -> List[str]:
    documents_names = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.pdf') or f.lower().endswith('.jpg') or f.lower().endswith('.jpeg') or f.lower().endswith('.png')]
    documents_filepaths = [os.path.join(INPUT_DIR, f) for f in documents_names]
    return documents_filepaths


def pokreni_analizu_gemini():
    documents_filepaths = find_input_documents()
  
    # Call Gemini API to analyze lab result documents
    results_dict: dict = api_gemini.analyze_docs(documents_filepaths=documents_filepaths)

    #map(lambda x: word_utils.sredi_slova(x), res)

    print(f"\n---------- |GEMINI| - Analysis success. --------------\n")
    print(f"{results_dict}")
    print(f"\n-------------------------------------------------------------------\n")
      
    # GHENERISANJE IZVESTAJA
    result = results_dict if results_dict else {}
    
    if isinstance(results_dict, list) and len(results_dict) > 0:
        result = results_dict[0]
    elif isinstance(results_dict, dict):
        result = results_dict
    else:
        print(f"\n\n---------- |ERROR|DSCLINIC| - Bad response: ------\n")
        print(f"{results_dict}")
        print(f"\n-------------------------------------------------------------------\n")

    
    ime_pacijenta = result.get("ime_pacijenta", "NEPOZNATO")
    datum: str = result.get("datum", "NEPOZNATO")

    dijagnoza_bolesti = result.get("dijagnoza_bolesti", "NEPOZNATA DIJAGNOZA BOLESTI")
    dijagnoza = result.get("dijagnoza", "NEPOZNATA DIJAGNOZA")
    dijagnoza_summarized = result.get("dijagnoza_summarized", "NEPOZNATA DIJAGNOZA")
    strucno_misljenje_dijagnoza = result.get("strucno_misljenje_dijagnoza_summarized", "NEPOZNATO")
    preporucena_terapija_i_savet = result.get("preporucena_terapija_i_savet_summarized", "NEMA SAVETA")


    nalazi_list: list = result.get("nalazi", [])
    nalazi_dict: dict = {}
    

    for nalaz in nalazi_list:
        #misljenje: str = nalaz.get("misljenje", "NEPOZNATO")
        #dijagnoza: str = nalaz.get("dijagnoza", None)
        #if not dijagnoza: misljenje = f"{misljenje} ({dijagnoza})"
        #vrednost: str = nalaz.get("vrednost", "NEPOZNATO")
        #nalazi_dict[misljenje] = vrednost
        misljenje_i_dijagnoza: str = nalaz.get("misljenje_i_dijagnoza", "NEPOZNATO")
        parametar_i_vrednost: str = nalaz.get("parametar_i_vrednost", "NEPOZNATO")
        #if "NEPOZNATO" in parametar_i_vrednost: parametar_i_vrednost = f"{nalaz.get('parametar', '')} {nalaz.get('vrednost', 'NEPOZNATO')}"
        nalazi_dict[misljenje_i_dijagnoza] = parametar_i_vrednost
        

    # ANALIZA TEXTA I NALAZAK PROTOKOLA
    protokoli: list = [{"nalaz": "Neki nalaz", "terapija": ["terapija1", "terapija2"], "napomena": "Napomena o terapiji"},]
    #protokoli = analyze_content(text, BASE_SYNDROMS.VELIKA_BAZA)

    #dijagnoze_i_objasenjenja: dict = {}
    # for k,
    # for d in moguce_dijagnoze:
    #     nalaz = "NEPOZNATO"
    #     objasnjenje = "NEPOZNATO"
    #     tokens = d.split("(")
    #     if tokens and len(tokens) >= 2:
    #         nalaz = tokens[0].strip()
    #         #objasnjenje = tokens[1].strip("").replace(")", "")
    #     dijagnoze_i_objasenjenja[nalaz] = objasnjenje
        
    pdf = exporter.create_report(
        ime_pacijenta=ime_pacijenta, 
        date=datum, 
        preporucena_terapija_i_savet=strucno_misljenje_dijagnoza,
        dijagnoza_summarized=None,#preporucena_terapija_i_savet,
        dijagnoza=None,#strucno_misljenje_dijagnoza,
        dijagnoze_i_objasenjenja=nalazi_dict,
        protocols_found=protokoli
    )

    ## WRITE PDF REPORT
    # Filepath
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H-%M")
    output_path = os.path.join(OUTPUT_DIR, f"NALAZ_{ime_pacijenta}_{timestamp_str}.pdf")
    # Create dirs if need
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # Write file
    exporter.write_report_file(pdf, output_path=output_path)

    print(f"\n--------------- PROGRAM COMPLETE --------------------------\n")
    

def main():
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    if not os.path.exists(INPUT_DIR): os.makedirs(INPUT_DIR)

    # pokreni_analizu()
    pokreni_analizu_gemini()

    if os.name == 'nt': os.startfile(OUTPUT_DIR)
    elif os.name == 'posix': os.system(f'open {OUTPUT_DIR}')
    
    input("Press Enter to exit...")


if __name__ == "__main__":
    main()
