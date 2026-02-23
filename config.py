##
# Configuration file for DSClinic project
#
from enum import StrEnum


##### APP #####
APP_VERSION = "v0.4"

######### PROGRAM RUN SETTINGS #########

#### GEMINI

## Tinking level
ARG_GEMINI_THINKING_LEVEL_STR: str = "HIGH"

## Models
class GEMINI_MODELS(StrEnum):
  """The model names, find more <link>"""
  GEMINI_3_PRO_PREVIEW = "gemini-3-pro-preview"
  GEMINI_3_FLASH_PREVIEW = "gemini-3-flash-preview"
  GEMINI_3_PRO_IMAGE_PREVIEW = "gemini-3-pro-image-preview"

ARG_GEMINI_MODEL_NAME: str = GEMINI_MODELS.GEMINI_3_PRO_PREVIEW

## AI Task descriptions
class AI_TASKS(StrEnum):
  """AI analysis task descriptions."""
  TASK_1 = "Make analysis from these two laboratory results"
  TASK_2 = "Analiziraj laboratorijske nalaze i uporedi sa prethodnim nalazom. Pronadji anomalije i promene u odnosu na prethodni nalaz. Napravi detaljnu analizu i predlozi moguce dijagnoze i preporuke za dalje korake."
  TASK_3 = "Spoji, analiziraj i sumiraj analizu iz dva nalaza jedan je iz MetaHuner program a drugi je iz labaratorije"
  TASK_4 = "Procitaj podatke iz dokumenata/izvestaja i ukazi na kriticne nalaze, predstavi podatke formatirane u json formatu, koji sadrzi polje 'ime_pacijenta', polje 'datum' (trenutni), polje 'dijagnoza_bolesti', polje 'dijagnoza_summarized', polje 'dijagnoza', polje 'strucno_misljenje_dijagnoza_summarized', polje 'preporucena_terapija_i_savet_summarized', polje 'nalazi' u dictionary formatu sa poljima, 'misljenje_i_dijagnoza', polje 'parametar', vrednost', 'status', 'znacaj', 'parametar_i_vrednost', 'dijagnoza'."
  TASK_5 = "spoji podatke iz oba dokumenta i ukazi na kriticne nalaze, nije bitno da li su od razlicitih pacijenata, prikazi ih kao json listu"
  TASK_6 = "Merge medical data from all documents and show critical symptoms summarized in Serbian language"
  TASK_7 = "spoji podatke iz oba dokumenta i ukazi na kriticne nalaze, nije bitno da li su od razlicitih pacijenata"
  TASK_8 = "spoji podatke iz oba dokumenta i ukazi na kriticne nalaze, nije bitno da li su od razlicitih pacijenata i prikazi ih kao json lista, a zatim napravi detaljnu analizu i predlozi moguce dijagnoze i preporuke za dalje korake"
  # TASK_9 = ("Procitaj podatke iz dokumenata/izvestaja i ukazi na kriticne nalaze i gde su problemi, predstavi podatke formatirane u json formatu, koji sadrzi polje 'ime_pacijenta', polje 'datum' (trenutni), polje 'dijagnoza_bolesti', polje 'dijagnoza_summarized', polje 'dijagnoza', polje 'strucno_misljenje_dijagnoza_summarized', polje 'preporucena_terapija_i_savet_summarized', polje 'gde je problem', polje 'rezime', polje 'uzrok_problema', polje 'nalazi' u dictionary formatu sa poljima, 'misljenje_i_dijagnoza', polje 'parametar', vrednost', 'status', 'znacaj', 'parametar_i_vrednost', 'dijagnoza', 'gde_je_problem', 'rezime', 'uzrok_problema', 'uzrok_problema_detaljno', 'uzrok_problema_summarized'."
  TASK_9 = ("Procitaj podatke iz medicinskih svih prilozenih dokumenata, nalaza, rezultata, izvestaja i ostalih podataka i " 
            "ukazi na kriticne nalaze, predlozi moguce dijagnoze, gde su problemi i sta su uzroci."
            "Predstavi podatke u json formatu, koristeci sledecu strukturu:"
            "{ "
            "   'ime_pacijenta', "
            "   'trenutni_datum', "
            "   'dijagnoza_bolesti', "
            "   'dijagnoza_summarized', "
            "   'dijagnoza', "
            "   'strucno_misljenje_dijagnoza_summarized', "
            "   'preporucena_terapija_i_savet_summarized', "
            "   'gde_je_problem', "
            "   'rezime', "
            "   'uzrok_problema', "
            "   'uzrok_problema_detaljno', "
            "   'uzrok_problema_summarized', "
            "   'nalazi': [ "
            "       { "
            "           'misljenje_i_dijagnoza', "
            "           'parametar', "
            "           'vrednost', "
            "           'status', "
            "           'znacaj', "
            "           'parametar_i_vrednost', "
            "           'dijagnoza', "
            "           'gde_je_problem', "
            "           'rezime', "
            "           'uzrok_problema', "
            "           'uzrok_problema_detaljno', "
            "           'uzrok_problema_summarized' "
            "       }, "
            "   ] "
            "} "
            " "
  )
ARG_AI_TASK_DESCRIPTION: str = AI_TASKS.TASK_9

"""
https://docs.cloud.google.com/vertex-ai/generative-ai/docs/model-reference/inference#generationconfig

Temperature controls response randomness. 
Lower values (min 0) are deterministic and better for factual tasks, 
while higher values increase creativity. 
If responses are too generic or loop, adjust the temperature (at least 0.1).
"""
ARG_GEMINI_MODEL_TEMPERATURE: float = 1.0

"""
https://docs.cloud.google.com/vertex-ai/generative-ai/docs/model-reference/inference#generationconfig

If specified, nucleus sampling is used.
Top-P changes how the model selects tokens for output. Tokens are selected from the most (see top-K) to least probable until the sum of their probabilities equals the top-P value. For example, if tokens A, B, and C have a probability of 0.3, 0.2, and 0.1 and the top-P value is 0.5, then the model will select either A or B as the next token by using temperature and excludes C as a candidate.
Specify a lower value for less random responses and a higher value for more random responses.

"""
ARG_GEMINI_MODEL_TOP_P: float = 0.95

ARG_GEMINI_MODEL_MAX_OUTPUT_TOKENS: int = 65535


## GOOGLE SERVICE
GOOGLE_API_KEY: str = "AIzaSyB6hNlueZ8ush24AEzfozI7XmONGwSuyIA"
# Project
GOOGLE_PROJECT_ID: str = "projects/278038315476" #"gen-lang-client-0650384180"
GOOGLE_PROJECT_LOCATION: str = "us-central1"
