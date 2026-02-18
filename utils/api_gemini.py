from enum import StrEnum
from google import genai
from google.genai import types
import base64
import os
import json


## GOOGLE SERVICE
#
GOOGLE_API_KEY: str = "AIzaSyB6hNlueZ8ush24AEzfozI7XmONGwSuyIA"

GOOGLE_PROJECT_ID: str = "projects/278038315476" #"gen-lang-client-0650384180"
GOOGLE_PROJECT_LOCATION: str = "us-central1"


## PROGRAM ARGUMENTS
#
# Analyis task description
class TASKS(StrEnum):
  """The Gemini Tasks."""
  TASK_1 = "Make analysis from these two laboratory results"
  TASK_2 = "Analiziraj laboratorijske nalaze i uporedi sa prethodnim nalazom. Pronadji anomalije i promene u odnosu na prethodni nalaz. Napravi detaljnu analizu i predlozi moguce dijagnoze i preporuke za dalje korake."
  TASK_3 = "Spoji, analiziraj i sumiraj analizu iz dva nalaza jedan je iz MetaHuner program a drugi je iz labaratorije"
  TASK_4 = "spoji podatke iz oba dokumenta i ukazi na kriticne simptome"
  TASK_5 = "spoji podatke iz oba dokumenta i ukazi na kriticne nalaze, nije bitno da li su od razlicitih pacijenata, prikazi ih kao json listu"
  TASK_6 = "Merge medical data from all documents and show critical symptoms summarized in Serbian language"
  TASK_7 = "spoji podatke iz oba dokumenta i ukazi na kriticne nalaze, nije bitno da li su od razlicitih pacijenata"
  TASK_8 = "spoji podatke iz oba dokumenta i ukazi na kriticne nalaze, nije bitno da li su od razlicitih pacijenata i prikazi ih kao json lista, a zatim napravi detaljnu analizu i predlozi moguce dijagnoze i preporuke za dalje korake"

def gemini_client_connect() -> genai.Client:
    client = genai.Client(
        # METHOD 1 - API Key (Recommended for testing)
        api_key=GOOGLE_API_KEY,
        # METHOD 2 - VertexAI (Recommended for production)
        #vertexai=True,
        #project=GOOGLE_PROJECT_ID,
        #location=GOOGLE_PROJECT_LOCATION
    )
    return client


def analyze_lab_result_docs(client: genai.Client, # Gemini client instance
                            doc1: str, # Path to first PDF document
                            doc2: str, # Path to second PDF document
                            task_text: str = TASKS.TASK_2, # Task description for Gemini
                            thinking_level: types.ThinkingLevel = types.ThinkingLevel.HIGH
                            ) -> list:
  results: list = []

  # Check Gemini client
  # if client is None or client is not genai.Client:
  #   raise ValueError("Invalid client provided. Please provide a valid genai.Client instance.")

  doc1 = types.Part.from_bytes(data=open(doc1, "rb").read(), mime_type="application/pdf")
  doc2 = types.Part.from_bytes(data=open(doc2, "rb").read(), mime_type="application/pdf")

  # GEMINI MODEL
  model = "gemini-3-pro-preview"

  # CONTENTS
  contents = [
    types.Content(
      role="user",
      parts=[
        doc1,
        doc2,
        types.Part.from_text(text=task_text)
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
    temperature = 1,
    top_p = 0.95,
    max_output_tokens = 65535,
    response_mime_type="application/json",
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

  for response in client.models.generate_content_stream(
      model = model,
      contents = contents,
      config = generate_content_config
    ):
    if not response.candidates or not response.candidates[0].content or not response.candidates[0].content.parts:
        # Pass
        continue
    # Parse response
    responseText = response.text
    #print(responseText, end="")
   


    # Function result
    #results.append(responseText)
    res += responseText
    #print(res, end="")

  # Convert the JSON string to a Python dictionary
  responseDict = json.loads(res)
  # Now you can use the data as a normal Python dictionary
  #print(f"\ndict: {responseDict}")
  print(f"\nCategory: {responseDict['category']}")
  print(f"\nTest: {responseDict['test_name']} - {responseDict['flag']}")
  print(f"\nResult: {responseDict['result']} {responseDict['unit']}")
  print(f"\nReference interval: {responseDict['reference_interval']}")
  print(f"\nStatus: {responseDict['test_status']}\n")

  return responseDict


# try:
#   gemini_client = gemini_client_connect()
#   res = analyze_lab_result_docs(gemini_client, "", "")
#   print(f"SUCCESS - RESPONSE: {res}")
# except Exception as e:
#   print(f"ERROR - GOOGLE SERVICE: {str(e)}")




# async def main():
#     # Create a local session to maintain conversation history
#     client = vertexai.Client(project=GOOGLE_PROJECT_ID, location=GOOGLE_PROJECT_LOCATION)
#     remote_app = client.agent_engines.get(name=''projects/449719406185/locations/us-central1/reasoningEngines/<agent_id>')
#     remote_session = await remote_app.async_create_session(user_id="u_456")
#     print(remote_session)

# if __name__ == "__main__":
#     asyncio.run(main())