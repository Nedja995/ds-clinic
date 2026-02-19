import os, sys
import src.api_gemini as api_gemini
import src.exporter as exporter
from src import BASE_SYNDROMS

#import warnings
#warnings.filterwarnings("ignore")
#sys.stdout.reconfigure(encoding='utf-8')

## SCRIPT PARAMETERS
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

## APP PARAMETERS
DATA_DIR = ROOT_DIR
INPUT_DIR = os.path.join(DATA_DIR, "ULAZ")
OUTPUT_DIR = os.path.join(DATA_DIR, "IZVESTAJI")


## UTILITIES



# TRAZI DIJAGNOZE
def analyze_content(text: str = "", BASE_DICT: dict = {}) -> list:
    protocols_found : list = []

    for kljuc, podaci in BASE_DICT.items():
        if kljuc.upper() in text:
            protocols_found.append(podaci)

    return protocols_found

      
def pokreni_analizu_gemini():
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    if not os.path.exists(INPUT_DIR): os.makedirs(INPUT_DIR)
    
    # PRONALAZAK PDF FAJLOVA U FOLDERU
    documents_names = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.pdf') or f.lower().endswith('.jpg') or f.lower().endswith('.jpeg') or f.lower().endswith('.png')]
    documents_filepaths = [os.path.join(INPUT_DIR, f) for f in documents_names]
  
    # Call Gemini API to analyze lab result documents
    results_dict: dict = api_gemini.analyze_docs(documents_filepaths[0], 
                                                 documents_filepaths[1])

    #
    ##map(lambda x: word_utils.sredi_slova(x), res)
    #print(f"\n----------\nSUCCESS - RESPONSE:\n{res}")

    print(f"\n---------- |GEMINI| - Analysis success. --------------\n")
    print(f"{results_dict}")
    print(f"\n-------------------------------------------------------------------\n")
      
    # ANALIZA TEXTA I NALAZAK PROTOKOLA
    protokoli: list = []
    protokoli = [{"nalaz": "Neki nalaz", "terapija": ["terapija1", "terapija2"], "napomena": "Napomena o terapiji"},]
    #protokoli = analyze_content(text, BASE_SYNDROMS.VELIKA_BAZA)

    # GHENERISANJE IZVESTAJA
    result = results_dict if results_dict else {}
    ime_pacijenta = result.get("ime_pacijenta", "NEPOZNATO")
    datum: str = result.get("datum", "NEPOZNATO")
    nalazi_list: list = result.get("nalazi", [])
    nalazi_dict: dict = {}

    for nalaz in nalazi_list:
        #misljenje: str = nalaz.get("misljenje", "NEPOZNATO")
        misljenje: str = nalaz.get("dijagnoza", "NEPOZNATO")
        vrednost: str = nalaz.get("vrednost", "NEPOZNATO")
        nalazi_dict[misljenje] = vrednost


    #datum_rodjenja = result.get("datum_rodjenja", "NEPOZNATO")
    #datum_nalaza_lab = result.get("datum_nalaza_lab", "NEPOZNATO")
    #datum_nalaza_nls = result.get("datum_nalaza_nls", "NEPOZNATO")
    #preporuke_za_dalje_korake = result.get("preporuke_za_dalje_korake", "NEMA PREPORUKA ZA DALJE KORAKE")
    preporuke: list = result.get("preporuke", [])
    #moguce_dijagnoze: list = result.get("moguce_dijagnoze", [])

    
    dijagnoze_i_objasenjenja: dict = {}
    # for k,
    # for d in moguce_dijagnoze:
    #     nalaz = "NEPOZNATO"
    #     objasnjenje = "NEPOZNATO"
        
    #     tokens = d.split("(")
    #     if tokens and len(tokens) >= 2:
    #         nalaz = tokens[0].strip()
    #         #objasnjenje = tokens[1].strip("").replace(")", "")
        
    #     dijagnoze_i_objasenjenja[nalaz] = objasnjenje
        
    exporter.create_report(
        ime_pacijenta, 
        datum, 
        preporuke[0] if len(preporuke) > 0 else "Nema preporuka",
        nalazi_dict,
        protokoli, 
        OUTPUT_DIR)

    print(f"\n--------------- PROGRAM COMPLETE --------------------------\n")
    
    if os.name == 'nt': os.startfile(OUTPUT_DIR)


def main():
    # pokreni_analizu()
    pokreni_analizu_gemini()

if __name__ == "__main__":
    main()
