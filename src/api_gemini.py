from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List, Optional
import base64
import os
import json

from src import word_utils
import config


## Gemini specific settings
ARG_GEMINI_THINKING_LEVEL: types.ThinkingLevel = types.ThinkingLevel[config.ARG_GEMINI_THINKING_LEVEL_STR]

class AnalysisFound(BaseModel):
    name: str = Field(description="NN")
    description: str = Field(description="Nema opisa")
    vrednost: str = Field(description="Nepoznato")
    
class AnalysisReport(BaseModel):
    name: str = Field(description="NN")
    report_date: str = Field(description="Nepoznat datum")
    terapije_i_saveti: str = Field(description="Nema terapija i saveta")
    nalazi: List[AnalysisFound] = Field(description="Nema nalaza")
    




## API INITIALIZATION
def gemini_client_connect() -> genai.Client:
  '''
  Google Gemini Api client initialization and connection.
  
  :return: Description
  :rtype: Client
  '''
  client: genai.Client = None
  
  try:
    client = genai.Client(
            # METHOD 1 - API Key (Recommended for testing)
            api_key=config.GOOGLE_API_KEY,
            # METHOD 2 - VertexAI (Recommended for production)
            #vertexai=True,
            #project=GOOGLE_PROJECT_ID,
            #location=GOOGLE_PROJECT_LOCATION
        )
    print(f"\n---------- |GEMINI| - Client initialization success. ----------")
  except Exception as e:
    print(f"\n\n---------- |ERROR|GEMINI| - Client initialization failed. ----------")
    print(f"\nEXCEPTION:\n{str(e)}")
    print(f"\n----------------------------------\n")
  finally:
      pass
  
  return client

#
def analyze_docs(doc1_path: str, doc2_path: str) -> list:
  task_description: str = config.ARG_AI_TASK_DESCRIPTION
  model_name: str = config.ARG_GEMINI_MODEL_NAME
  thinking_level = ARG_GEMINI_THINKING_LEVEL
  results = None

  # Initialize api client
  client = gemini_client_connect()
  # check
  # if client is None or client is not genai.Client:
  #   raise ValueError("Invalid client provided. Please provide a valid genai.Client instance.")

  # Analyze lab result documents
  try:
      results = analyze_lab_result_docs(
          client=client,
          model_name=model_name,
          thinking_level=thinking_level,
          task_description=task_description,
          doc1_path=doc1_path, 
          doc2_path=doc2_path 
          )   
      print(f"\n---------- |GEMINI| - Analysis success. --------------\n")
      #print(f"{results}")
      #print(f"\n-------------------------------------------------------------------\n")
  except Exception as e:
      print(f"\n\n---------- |ERROR|GEMINI| - Analyze failed with exception: ------\n")
      print(f"{str(e)}")
      print(f"\n-------------------------------------------------------------------\n")
  finally:
      client.close()
      client = None

  return results

def sredi_slova(text):
    mape = {"č": "c", "ć": "c", "ž": "z", "š": "s", "đ": "dj", "Č": "C", "Ć": "C", "Ž": "Z", "Š": "S", "Đ": "Dj"}
    for k, v in mape.items(): text = text.replace(k, v)
    return text

def analyze_lab_result_docs(client: genai.Client,
                            model_name: str = "gemini-3-pro-preview",
                            thinking_level: genai.types.ThinkingLevel = genai.types.ThinkingLevel.HIGH,
                            task_description: str = "Analiziraj laboratorijske nalaze i uporedi sa prethodnim nalazom. Pronadji anomalije i promene u odnosu na prethodni nalaz. Napravi detaljnu analizu i predlozi moguce dijagnoze i preporuke za dalje korake.",
                            doc1_path: str = "", # Path to first PDF document
                            doc2_path: str = "" # Path to second PDF document
                            ) -> list:
  results: list = []

  support_extensions = [".jpg", ".jpeg", ".png", ".pdf"]
  
  ext = [ext for ext in support_extensions if doc1_path.lower().endswith(ext)]
  
  doc1: types.Part = None
  doc2: types.Part = None
  
  if ext and len(ext) > 0:
    print(f"\n---------- |GEMINI| - Document 1 format supported: {ext[0]} ----------\n")
    if ext[0] in [".jpg", ".jpeg", ".png"]:
      doc1 = types.Part.from_bytes(data=open(doc1_path, "rb").read(), mime_type="image/jpeg")
    elif ext[0] == ".pdf":
      doc1 = types.Part.from_bytes(data=open(doc1_path, "rb").read(), mime_type="application/pdf")
      
   
    ext = [ext for ext in support_extensions if doc2_path.lower().endswith(ext)]
    print(f"\n---------- |GEMINI| - Document 2 format supported: {ext[0]} ----------\n")
    if ext and len(ext) > 0:
      if ext[0] in [".jpg", ".jpeg", ".png"]:
        doc2 = types.Part.from_bytes(data=open(doc2_path, "rb").read(), mime_type="image/jpeg")
      elif ext[0] == ".pdf":
        doc2 = types.Part.from_bytes(data=open(doc2_path, "rb").read(), mime_type="application/pdf")
  else:
    pass
  
  # CONTENTS
  contents = [
    types.Content(
      role="user",
      parts=[
        doc1,
        doc2,
        types.Part.from_text(text=task_description)
      ]
    ),
  ]
  tools = [
    types.Tool(google_search=types.GoogleSearch()),
  ]

  # CONTENT CONFIG
  generate_content_config = types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(
      thinking_level=thinking_level,
    ),
    temperature = config.ARG_GEMINI_MODEL_TEMPERATURE,
    top_p = config.ARG_GEMINI_MODEL_TOP_P,
    max_output_tokens = config.ARG_GEMINI_MODEL_MAX_OUTPUT_TOKENS,
    response_mime_type = "application/json",

    #response_json_schema = AnalysisReport.model_json_schema(),
    #response_mime_type="application/json",
    #response_json_schema=types.JsonSchema(type="array", items=types.JsonSchema(type="dictionary")),
    safety_settings = [types.SafetySetting(
      category="HARM_CATEGORY_HATE_SPEECH",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_DANGEROUS_CONTENT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_HARASSMENT",
      threshold="OFF"
    )],
    tools = tools,
  )

  res = ""

  print(f"\n---------- |GEMINI| - Analysis Start... --------------\n")
  for response in client.models.generate_content_stream(
      model = model_name,
      contents = contents,
      config = generate_content_config
    ):
    # Check
    if not response.candidates or not response.candidates[0].content or not response.candidates[0].content.parts:
      # PASS - Empty response
      print(f"\n---------- |GEMINI| - Analysis WARNING: No candidates or content in response. Skipping...")
      continue
    
    
    # Parse response
    responseText = response.text
    
    #report = AnalysisReport.model_validate_json(response.text)
    #print(f"\n---------- |GEMINI| - Analysis Report2:\n{report}\n")

    filtered_text: str = "".join(map(lambda x: sredi_slova(x), responseText))
    #filtered_text = responseText.encode('latin-1', 'replace').decode('latin-1')
  
    #print(responseText, end="")
    #results.append(responseText)
    res += filtered_text
    #res = res.replace("NLS Analiza: ", "")
    #print(res, end="")
    print(f"\n---------- |GEMINI| - Analysis End. -----------------\n")

  responseDict: dict = {}
  # Convert the JSON string to a Python dictionary
  try:
    responseDict = json.loads(res)
  except json.JSONDecodeError as e:
    print(f"--------- |GEMINI| Error decoding JSON: {e}")
    responseDict = {}
    
  # print(f"\n---------- |GEMINI| - Response Dictionary: --------------\n")
  # print(responseDict, end="")
  # Now you can use the data as a normal Python dictionary
  #print(f"\ndict: {responseDict}")
  # print(f"\nCategory: {responseDict['category']}")
  # print(f"\nTest: {responseDict['test_name']} - {responseDict['flag']}")
  # print(f"\nResult: {responseDict['result']} {responseDict['unit']}")
  # print(f"\nReference interval: {responseDict['reference_interval']}")
  # print(f"\nStatus: {responseDict['test_status']}\n")

  return responseDict
