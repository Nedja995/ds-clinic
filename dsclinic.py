import os
from utils import BASE_SYNDROMS, api_gemini, exporter

#import warnings
#warnings.filterwarnings("ignore")

## SCRIPT PARAMETERS
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

## APP PARAMETERS
DATA_DIR = ROOT_DIR
INPUT_DIR = os.path.join(DATA_DIR, "ULAZ")
OUTPUT_DIR = os.path.join(DATA_DIR, "IZVESTAJI")


## UTILITIES

def sredi_slova(text):
    mape = {"č": "c", "ć": "c", "ž": "z", "š": "s", "đ": "dj", "Č": "C", "Ć": "C", "Ž": "Z", "Š": "S", "Đ": "Dj"}
    for k, v in mape.items(): text = text.replace(k, v)
    return text

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
    documents_names = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.pdf')]
    documents_filepaths = [os.path.join(INPUT_DIR, f) for f in documents_names]
  
    # Call Gemini API to analyze lab result documents
    res = api_gemini.analyze_docs(documents_filepaths[0], documents_filepaths[1])
    #
    #print(f"\n----------\nSUCCESS - RESPONSE RAW:\n{res}")
    #
    ##map(lambda x: sredi_slova(x), res)
    #print(f"\n----------\nSUCCESS - RESPONSE:\n{res}")

    print(f"\n--------------- PROGRAM COMPLETE --------------------------\n")

    # ANALIZA TEXTA I NALAZAK PROTOKOLA
    #protokoli = analyze_content(text, BASE_SYNDROMS.VELIKA_BAZA)

    # GHENERISANJE IZVESTAJA
    #generate_report_pdf(document, protokoli, OUTPUT_DIR)

    #if os.name == 'nt': os.startfile(OUTPUT_DIR)



def main():
    # pokreni_analizu()
    pokreni_analizu_gemini()

if __name__ == "__main__":
    main()
