from google import genai
from google.genai import types
import base64
import os
import json
import config


## Gemini specific settings
ARG_GEMINI_THINKING_LEVEL: types.ThinkingLevel = types.ThinkingLevel[config.ARG_GEMINI_THINKING_LEVEL_STR]

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
      print(f"\n---------- |GEMINI| - Analysis success. Results raw: --------------\n")
      print(f"{results}")
      print(f"\n-------------------------------------------------------------------\n")
  except Exception as e:
      print(f"\n\n---------- |ERROR|GEMINI| - Analyze failed with exception: ------\n")
      print(f"{str(e)}")
      print(f"\n-------------------------------------------------------------------\n")
  finally:
      client.close()
      client = None

  return results

def analyze_lab_result_docs(client: genai.Client,
                            model_name: str = "gemini-3-pro-preview",
                            thinking_level: genai.types.ThinkingLevel = genai.types.ThinkingLevel.HIGH,
                            task_description: str = "Analiziraj laboratorijske nalaze i uporedi sa prethodnim nalazom. Pronadji anomalije i promene u odnosu na prethodni nalaz. Napravi detaljnu analizu i predlozi moguce dijagnoze i preporuke za dalje korake.",
                            doc1_path: str = "", # Path to first PDF document
                            doc2_path: str = "" # Path to second PDF document
                            ) -> list:
  results: list = []

  doc1 = types.Part.from_bytes(data=open(doc1_path, "rb").read(), mime_type="application/pdf")
  doc2 = types.Part.from_bytes(data=open(doc2_path, "rb").read(), mime_type="application/pdf")

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
      model = model_name,
      contents = contents,
      config = generate_content_config
    ):
    # Check
    if not response.candidates or not response.candidates[0].content or not response.candidates[0].content.parts:
      # PASS - Empty response
      print(f"\n---------- |GEMINI| - Analysis Info: No candidates or content in response. Skipping...")
      continue
    
    # Parse response
    responseText = response.text
    #print(responseText, end="")
    #results.append(responseText)
    res += responseText
    print(res, end="")

  # Convert the JSON string to a Python dictionary
  responseDict = json.loads(res)
  print(f"\n---------- |GEMINI| - Response Dictionary: --------------\n")
  print(responseDict, end="")
  # Now you can use the data as a normal Python dictionary
  #print(f"\ndict: {responseDict}")
  # print(f"\nCategory: {responseDict['category']}")
  # print(f"\nTest: {responseDict['test_name']} - {responseDict['flag']}")
  # print(f"\nResult: {responseDict['result']} {responseDict['unit']}")
  # print(f"\nReference interval: {responseDict['reference_interval']}")
  # print(f"\nStatus: {responseDict['test_status']}\n")

  return responseDict

def extract_info_from_response(response: dict) -> dict:
  # Extract specific information from the response dictionary
  extracted_info = {
      "category": response.get("category", ""),
      "test_name": response.get("test_name", ""),
      "flag": response.get("flag", ""),
      "result": response.get("result", ""),
      "unit": response.get("unit", ""),
      "reference_interval": response.get("reference_interval", ""),
      "test_status": response.get("test_status", "")
  }
  return extracted_info


## Using Example
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