##
#
#
from typing import List
import json
from pydantic import BaseModel, Field
#
from google import genai
from google.genai import types
#
import config
from src import word_utils


# Gemini specific settings
ARG_GEMINI_THINKING_LEVEL: types.ThinkingLevel = types.ThinkingLevel[
    config.ARG_GEMINI_THINKING_LEVEL_STR]

CONST_INPUT_SUPPORTED_EXTENSIONS: list = [".jpg", ".jpeg", ".png", ".pdf"]


class AnalysisFound(BaseModel):
    name: str = Field(description="NN")
    description: str = Field(description="Nema opisa")
    vrednost: str = Field(description="Nepoznato")


class AnalysisReport(BaseModel):
    name: str = Field(description="NN")
    report_date: str = Field(description="Nepoznat datum")
    terapije_i_saveti: str = Field(description="Nema terapija i saveta")
    nalazi: List[AnalysisFound] = Field(description="Nema nalaza")


# API INITIALIZATION
def gemini_client_connect() -> genai.Client:
    print(f"---------- |GEMINI| Client initialization begin. ----------")
    client: genai.Client = None

    try:
        client = genai.Client(
            # METHOD 1 - API Key (Recommended for testing)
            api_key=config.GOOGLE_API_KEY,
            # METHOD 2 - VertexAI (Recommended for production)
            # vertexai=True,
            # project=GOOGLE_PROJECT_ID,
            # location=GOOGLE_PROJECT_LOCATION
        )
        print(f"\n---------- |GEMINI| Client initialization success. ----------")
    except Exception as e:
        print(f"\n\n---------- |GEMINI||ERROR| Client initialization failed. ----------")
        print(f"\nEXCEPTION:\n{str(e)}")
        print(f"\n----------------------------------")
    finally:
        pass

    return client

#


def analyze_docs(ai_task_description: str = config.ARG_AI_TASK_DESCRIPTION,
                documents_filepaths: List[str] = []) -> dict:
    model_name: str = config.GEMINI_MODELS.GEMINI_3_PRO_PREVIEW
    results: dict = {}

    # Initialize api client
    client = gemini_client_connect()
    # check
    # if client is None or client is not genai.Client:
    #   raise ValueError("Invalid client provided. Please provide a valid genai.Client instance.")

    # Analyze lab result documents
    try:
        results = analyze_docs2(model_name=model_name,
                                ai_task_description=ai_task_description,
                                documents_filepaths=documents_filepaths)
        print(f"\n---------- |GEMINI| - Analysis success. --------------")
        # print(f"{results}")
        # print(f"\n-------------------------------------------------------------------\n")
    except Exception as e:
        print(f"\n\n---------- |ERROR|GEMINI| - Analyze failed with exception: ------")
        print(f"{str(e)}")
        print(f"\n-------------------------------------------------------------------")
        # CHECK IS GEMINI MODEL EXPERIENCING HIG DEMAND
        if "high demand" in str(e):
            # Try again with different model
            if model_name == config.GEMINI_MODELS.GEMINI_3_PRO_PREVIEW:
                model_name = config.GEMINI_MODELS.GEMINI_3_FLASH_PREVIEW
            elif model_name == config.GEMINI_MODELS.GEMINI_3_FLASH_PREVIEW:
                model_name = config.GEMINI_MODELS.GEMINI_3_PRO_IMAGE_PREVIEW
            else:
                model_name = config.GEMINI_MODELS.GEMINI_3_PRO_PREVIEW
            results = analyze_docs2(
                model_name=model_name, documents_filepaths=documents_filepaths)
    finally:
        client.close()
        client = None

    return results


#
def analyze_docs2(model_name: str = config.ARG_GEMINI_MODEL_NAME,
                  ai_task_description: str = config.ARG_AI_TASK_DESCRIPTION,
                  documents_filepaths: List[str] = []) -> dict:
    thinking_level = ARG_GEMINI_THINKING_LEVEL
    results: dict = {}

    # Initialize api client
    client = gemini_client_connect()
    # if client is None or client is not genai.Client:
    #  raise ValueError("Invalid client provided. Please provide a valid genai.Client instance.")

    # Analyze lab result documents
    # try:
    results = analyze_lab_result_docs(
        client=client,
        model_name=model_name,
        thinking_level=thinking_level,
        task_description=ai_task_description,
        documents_filepaths=documents_filepaths
    )
    # except Exception as e:
    # print(f"\n\n---------- |ERROR|GEMINI| - Analyze failed with exception: ------")
    # print(f"{str(e)}")
    # raise e
    # finally:
    client.close()
    client = None

    return results


def load_document(filepath: str) -> genai.types.Part:
    print(f"\n---- |GEMINI||DEBUG| Load Document from filepath: {filepath}.")
    doc: types.Part = None
    doc_extension = [
        ext for ext in CONST_INPUT_SUPPORTED_EXTENSIONS if filepath.lower().endswith(ext)]

    if doc_extension and len(doc_extension) > 0:
        #print(f"\n---- |GEMINI||DEBUG| Document format supported: {doc_extension[0]}.")
        if doc_extension[0] in [".jpg", ".jpeg", ".png"]:
            # Document is Image file
            doc = types.Part.from_bytes(
                data=open(filepath, "rb").read(), mime_type="image/jpeg")
        elif doc_extension[0] == ".pdf":
            # Document is PDF file
            doc = types.Part.from_bytes(
                data=open(filepath, "rb").read(), mime_type="application/pdf")
    else:
        print(f"\n---------- |GEMINI||WARNING| Load Document failed because: Format not supported. Skip...")
        pass

    return doc


def analyze_lab_result_docs(client: genai.Client,
                            model_name: str = config.ARG_GEMINI_MODEL_NAME,
                            thinking_level: genai.types.ThinkingLevel = ARG_GEMINI_THINKING_LEVEL,
                            task_description: str = config.ARG_AI_TASK_DESCRIPTION,
                            documents_filepaths: List[str] = [],
                            ) -> dict:
    print(f"\n---------- |GEMINI||INFO| Analysis - Run with parameters: --------------")
    print(f"\n---------- Thinking level: ${thinking_level}.")
    print(f"\n---------- Model: {model_name}.")
    print(f"\n---------- Documents: {documents_filepaths}.")
    print(f"\n---------- Task description: ${task_description}.")

    responseDict: dict = {}

    documents: List[genai.types.Part] = []

    for filepath in documents_filepaths:
        doc = load_document(filepath)
        if doc:
            documents.append(doc)
        else:
            print(
                f"\n---------- |GEMINI||ERROR| Failed to load document at path: ${filepath}.")

    # CONTENTS
    parts: List[genai.types.Part] = []
    # Add input documents
    parts.extend(documents)
    # Add AI task descripion
    parts.append(types.Part.from_text(text=task_description))

    contents = [
        types.Content(
            role="user",
            parts=parts
        ),
    ]
    tools = [
        types.Tool(google_search=types.GoogleSearch()),
        #types.Tool(url_context=types.UrlContext()),
        #types.Tool(enterprise_web_search=types.EnterpriseWebSearch())
    ]

    # CONTENT CONFIG
    print(f"\n---- |GEMINI||DEBUG| Analysis - Prepaire content config.")
    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level=thinking_level,
        ),
        temperature=config.ARG_GEMINI_MODEL_TEMPERATURE,
        top_p=config.ARG_GEMINI_MODEL_TOP_P,
        max_output_tokens=config.ARG_GEMINI_MODEL_MAX_OUTPUT_TOKENS,
        response_mime_type="application/json",
        # response_json_schema = AnalysisReport.model_json_schema(),
        # response_mime_type="application/json",
        # response_json_schema=types.JsonSchema(type="array", items=types.JsonSchema(type="dictionary")),
        safety_settings=[types.SafetySetting(
            category="HARM_CATEGORY_HATE_SPEECH",
            threshold="OFF"
        ), types.SafetySetting(
            category="HARM_CATEGORY_DANGEROUS_CONTENT",
            threshold="OFF"
        ), types.SafetySetting(
            category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
            threshold="OFF"
        ), types.SafetySetting(
            category="HARM_CATEGORY_HARASSMENT",
            threshold="OFF"
        )],
        tools=tools,
    )

    res = ""

    print(f"\n------- |GEMINI||INFO| Analysis: Start requests.")
    try:
        for response in client.models.generate_content_stream(
            model=model_name,
            contents=contents,
            config=generate_content_config
        ):
            print(f"\n----- |GEMINI| Analysis: Request finised. Checking response..")
            # Check
            if not response.candidates or not response.candidates[0].content or not response.candidates[0].content.parts:
                # PASS - Empty response
                print(
                    f"\n----- |GEMINI||WARNING| Analysis: No candidates or content in response. Skipping...")
                continue

            # RESPONSE PARSING
            responseText = response.text

            # report = AnalysisReport.model_validate_json(response.text)
            # print(f"\n---------- |GEMINI| - Analysis Report2:\n{report}\n")
            filtered_text = responseText
            #filtered_text: str = "".join(map(lambda x: word_utils.sredi_slova(x), responseText))
            #filtered_text = filtered_text.replace("?", "")
            # filtered_text = responseText.encode('latin-1', 'replace').decode('latin-1')
            # filtered_text = filtered_text.encode('latin-1', 'ignore').decode('latin-1')
            # print(responseText, end="")
            # results.append(responseText)
            res += filtered_text
            # res = res.replace("NLS Analiza: ", "")
            # print(res, end="")
            print(f"\n----- |GEMINI| Analysis: Request Checking response finished. Append to results..")
            # --- END FOR LOOP ---
    except Exception as e:
        if "high demand" in str(e):
            print(f"\n----------------- |GEMINI||FATAL| ALL MODELS ARE BUSY ----------------------------------------")
            print(f"\n---------------------------  TRY AGAIN LATER           ----------------------------------------")
        res = "{}"
        
    print(f"\n------- |GEMINI| Analysis: Requests finished.")

    # Convert the JSON string to a Python dictionary
    try:
        responseDict = json.loads(res)
        print(f"\n----- |GEMINI| Analysis: Response JSON created.")
    except json.JSONDecodeError as e:
        print(
            f"\n---------- |GEMINI| - Analysis - ERROR: Error decoding JSON:\n{e}.")
        responseDict = {}

    # print(f"\n---------- |GEMINI| - Response Dictionary: --------------\n")
    # print(responseDict, end="")

    return responseDict
