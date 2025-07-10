"""
Module: app.py

This module provides functionality to analyze documents using Azure Form Recognizer
and evaluate their compliance with accounting standards using OpenAI.

Functions:
- analyze_document(file_path): Analyzes a document using Azure Form Recognizer and extracts key-value pairs.
- evaluate_compliance(data, accounting_standards): Evaluates the compliance of extracted data with accounting standards using OpenAI.
- main(): Main function to analyze a contract document and evaluate its compliance with accounting standards.
"""

import os
from dotenv import load_dotenv
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI

# Load environment variables from config.env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'infras', 'config.env'))

# Azure Form Recognizer setup
FORM_RECOGNIZER_ENDPOINT = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
FORM_RECOGNIZER_KEY = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")

# Azure OpenAI setup
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_MODEL = os.getenv("AZURE_OPENAI_MODEL_DEPLOYMENT_NAME")

# print(FORM_RECOGNIZER_ENDPOINT)
# print(FORM_RECOGNIZER_KEY)
# print(AZURE_OPENAI_API_KEY)
# print(AZURE_OPENAI_ENDPOINT)
# print(OPENAI_MODEL)

# Initialize Azure OpenAI client
client = AzureOpenAI(
  api_key=AZURE_OPENAI_API_KEY,
  api_version="2024-11-20",
  azure_endpoint=AZURE_OPENAI_ENDPOINT
)


# Initialize Form Recognizer client
document_client = DocumentAnalysisClient(
    endpoint=FORM_RECOGNIZER_ENDPOINT,
    credential=AzureKeyCredential(FORM_RECOGNIZER_KEY),
)

#file_path = os.path.join(os.path.dirname(__file__), "..", "sample-data", "sample-invoice.pdf")
file_path = os.path.join(os.path.dirname(__file__), "..", "sample-data", "right_of_way_agreement.pdf")

# Read the document file
with open(file_path, "rb") as f:
    document_content = f.read()

# Analyze document
#poller = document_client.begin_analyze_document("prebuilt-layout", document_content)
poller = document_client.begin_analyze_document("prebuilt-document", document_content)
result = poller.result()


def build_combined_key_value_pairs(form_result):
    """
    Build a combined key-value pair structure from form_result.key_value_pairs and form_result.paragraphs.

    Args:
        form_result: The result object from Azure Form Recognizer.

    Returns:
        dict: A dictionary containing combined key-value pairs from key_value_pairs and paragraphs.
    """
    combined_data = {}

    # Process key-value pairs
    for kv_pair in form_result.key_value_pairs:
        kv_key = kv_pair.key.content if kv_pair.key else "No Key"
        kv_value = kv_pair.value.content if kv_pair.value else "No Value"
        if kv_key in combined_data:
            if isinstance(combined_data[kv_key], list):
                combined_data[kv_key].append(kv_value)
            else:
                combined_data[kv_key] = [combined_data[kv_key], kv_value]
        else:
            combined_data[kv_key] = kv_value

    # Process paragraphs
    for paragraph in result.paragraphs:
        key_ = paragraph.role if paragraph.role else "No Role"
        value_ = paragraph.content
        if key_ in combined_data:
            if isinstance(combined_data[key_], list):
                combined_data[key_].append(value_)
            else:
                combined_data[key_] = [combined_data[key_], value_]
        else:
            combined_data[key_] = value_

    return combined_data

# Example usage
combined_key_value_data = build_combined_key_value_pairs(result)
print("Combined Key-Value Pairs:")
for key, value in combined_key_value_data.items():
    print(f"{key}: {value}")



#print(result.paragraphs[0])
#print(result.paragraphs[0].content)
#print(result.paragraphs[0].content[0].text)

#print(result.paragraphs[1])
#print(result.paragraphs[1].content)

#print(result.paragraphs[2])
#print(result.paragraphs[2].content)

#print(result.content[0::])

#print(result.key_value_pairs[0::])
#result.documents[0].fields.get()
#print(result.paragraphs[0::])

#print(result.key_value_pairs[1])

# key=result.key_value_pairs[4].key.content
# value=result.key_value_pairs[4].value.content

# print({key:value})

# for idx, result in enumerate(result.key_value_pairs):    
#     key=result.key_value_pairs[idx].key.content
#     value=result.key_value_pairs[idx].value.content
#     print({key:value})

#print(result.content[0::])
# for idx, result in enumerate(result.key_value_pairs): 
#     idx += 1 
#     key=result.key_value_pairs[idx].key.content
#     value=result.key_value_pairs[idx].value.content

#     #print(f"Key: {key}, Value: {value}")
#     print({key:value})

# for idx, result in enumerate(result.key_value_pairs):    
#     key=result.key_value_pairs[1].key.content
#     value=result.key_value_pairs[1].value.content
# print(result.key_value_pairs[1].key.content)
# print(result.key_value_pairs[1].value.content)
# for idx, result in enumerate(result.documents):

#     #print(f"\nid: {idx}, with result {result} and result confidence of {result.confidence}.")
#     print(result.fields.get())





# def analyze_document(file_path):
#     """
#     Analyze a document using Azure Form Recognizer.

#     Args:
#         file_path (str): The path to the document file to be analyzed.

#     Returns:
#         dict: A dictionary containing the extracted key-value pairs from the document.
#     """
#     # Initialize Form Recognizer client
#     document_client = DocumentAnalysisClient(
#         endpoint=FORM_RECOGNIZER_ENDPOINT,
#         credential=AzureKeyCredential(FORM_RECOGNIZER_KEY),
#     )

#     # Read the document file
#     with open(file_path, "rb") as f:
#         document_content = f.read()

#     # Analyze document
#     #poller = document_client.begin_analyze_document("prebuilt-layout", document_content)
#     poller = document_client.begin_analyze_document("prebuilt-document", document_content)
#     result = poller.result()


#     for idx, result in enumerate(result.documents):
    
#         print(f"\nid: {idx}, with result {result} and result confidence of {result.confidence}.")

#     extracted_data = {}
#     raw_text = []

#     #for field in result.key_value_pairs:
#     for kv_pair in result.key_value_pairs:
#         #print(f"Key: {field.key}, Value: {field.value}")  # Debugging statement
#         #extracted_data[field.key] = field.value
#         key = kv_pair.key.content if kv_pair.key else None
#         value = kv_pair.value.content if kv_pair.value else None
#         if key and value:
#             if key in extracted_data:
#                 extracted_data[key].append(value)
#             else:
#                 extracted_data[key] = [value]
#             #print(f"Key: {key}, Value: {value}")  # Debugging statement

#     # Extract raw text
#     for page in result.pages:
#         for line in page.lines:
#             raw_text.append(line.content)

#     # Manually parse raw text to extract additional key-value pairs
#     additional_data = parse_raw_text(raw_text)
#     extracted_data.update(additional_data)

#     # Get the number of pages processed
#     page_count = len(result.pages)

#     return {"data": extracted_data, "raw_text": raw_text, "page_count": page_count}

# def parse_raw_text(raw_text):
#     """
#     Parse raw text to extract additional key-value pairs.

#     Args:
#         raw_text (list): The raw text extracted from the document.

#     Returns:
#         dict: A dictionary containing the additional key-value pairs.
#     """
#     additional_data = {}
#     current_key = None
#     current_value = []

#     for line in raw_text:
#         if ":" in line:
#             if current_key:
#                 # Save the previous key-value pair
#                 additional_data[current_key] = " ".join(current_value).strip()
#             # Start a new key-value pair
#             key, value = line.split(":", 1)
#             current_key = key.strip()
#             current_value = [value.strip()]
#         elif current_key:
#             # Continue the current value
#             current_value.append(line.strip())

#     # Save the last key-value pair
#     if current_key:
#         additional_data[current_key] = " ".join(current_value).strip()

#     # Convert single values to lists for consistency
#     for key in additional_data:
#         additional_data[key] = [additional_data[key]]

#     return additional_data

# def evaluate_compliance(data, accounting_standards):
#     """
#     Evaluate the compliance of extracted data with accounting standards using OpenAI.

#     Args:
#         data (dict): The extracted data from the document.
#         accounting_standards (str): The accounting standards to evaluate compliance against.

#     Returns:
#         str: The compliance analysis result from OpenAI.
#     """
#     # Prepare prompt for OpenAI
#     prompt = f"""
#     Analyze the following contract data for compliance with the accounting standards:
    
#     Contract Data: {data}

#     Accounting Standards: {accounting_standards}

#     Highlight any discrepancies or issues.
#     """

#     response = client.chat.completions.create(
#         model=OPENAI_MODEL,
#         messages=[
#             {"role": "system", "content": "You are a compliance analyst."},
#             {"role": "user", "content": prompt}
#         ],
#         max_tokens=500
#     )

#     return response["choices"][0]["text"]

# def main():
#     """
#     Main function to analyze a contract document and evaluate its compliance with accounting standards.
#     """
#     # Define the file path for the contract
#     contract_path = os.path.join(os.path.dirname(__file__), "..", "sample-data", "right_of_way_agreement.pdf")

#     # Define accounting standards (you can extract this from PDF or hardcode it)
#     #accounting_standards = "Insert accounting standards here or extract dynamically."

#     # # Step 1: Extract data using Form Recognizer
#      analysis_result = analyze_document(contract_path)
#     # contract_data = analysis_result["data"]
#     # raw_text = analysis_result["raw_text"]
#     # page_count = analysis_result["page_count"]

#     # Log or store the page count for chargeback purposes
#     print(f"Number of pages processed: {page_count}")

#     # Print the extracted contract data
#     print(f"Text of contract data processed: {contract_data}")

#     # Print the raw text extracted from the document
#     print("Raw text extracted from the document:")
#     for line in raw_text:
#         print(line)

#     # Step 2: Evaluate compliance using OpenAI
#     #compliance_result = evaluate_compliance(contract_data, accounting_standards)

#     #print("Compliance Analysis Result:")
#     #print(compliance_result)

# if __name__ == "__main__":
#     main()