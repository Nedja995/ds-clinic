#
# Configuration file for DSClinic project
#
from enum import StrEnum


######### PROGRAM RUN SETTINGS #########

#### GEMINI

ARG_GEMINI_THINKING_LEVEL_STR: str = "HIGH"

## GEMINI CONSTANTS
class GEMINI_MODELS(StrEnum):
  """The model names, find more <link>"""
  GEMINI_3_PRO_PREVIEW = "gemini-3-pro-preview"
  GEMINI_3_FLASH_PREVIEW = "gemini-3-flash-preview"
  GEMINI_3_PRO_IMAGE_PREVIEW = "gemini-3-pro-image-preview"
ARG_GEMINI_MODEL_NAME: str = GEMINI_MODELS.GEMINI_3_FLASH_PREVIEW



class AI_TASKS(StrEnum):
  """AI analysis task descriptions."""
  TASK_1 = "Make analysis from these two laboratory results"
  TASK_2 = "Analiziraj laboratorijske nalaze i uporedi sa prethodnim nalazom. Pronadji anomalije i promene u odnosu na prethodni nalaz. Napravi detaljnu analizu i predlozi moguce dijagnoze i preporuke za dalje korake."
  TASK_3 = "Spoji, analiziraj i sumiraj analizu iz dva nalaza jedan je iz MetaHuner program a drugi je iz labaratorije"
  TASK_4 = "spoji podatke iz oba dokumenta i ukazi na kriticne simptome"
  TASK_5 = "spoji podatke iz oba dokumenta i ukazi na kriticne nalaze, nije bitno da li su od razlicitih pacijenata, prikazi ih kao json listu"
  TASK_6 = "Merge medical data from all documents and show critical symptoms summarized in Serbian language"
  TASK_7 = "spoji podatke iz oba dokumenta i ukazi na kriticne nalaze, nije bitno da li su od razlicitih pacijenata"
  TASK_8 = "spoji podatke iz oba dokumenta i ukazi na kriticne nalaze, nije bitno da li su od razlicitih pacijenata i prikazi ih kao json lista, a zatim napravi detaljnu analizu i predlozi moguce dijagnoze i preporuke za dalje korake"

ARG_AI_TASK_DESCRIPTION: str = AI_TASKS.TASK_2

## GOOGLE SERVICE
#
GOOGLE_API_KEY: str = "AIzaSyB6hNlueZ8ush24AEzfozI7XmONGwSuyIA"

GOOGLE_PROJECT_ID: str = "projects/278038315476" #"gen-lang-client-0650384180"
GOOGLE_PROJECT_LOCATION: str = "us-central1"

