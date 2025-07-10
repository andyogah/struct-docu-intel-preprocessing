"""
Module: app2.py

This module provides functionality to analyze documents using Azure Form Recognizer
and evaluate their compliance with accounting standards using OpenAI.

Functions:
- analyze_document(file_path): Analyzes a document using Azure Form Recognizer and extracts key-value pairs.
- evaluate_compliance(data, accounting_standards): Evaluates the compliance of extracted data with accounting standards using OpenAI.
- main(): Main function to analyze a contract document and evaluate its compliance with accounting standards.
"""

import os
from azure.ai.formrecognizer import DocumentAnalysisClient
from dotenv import load_dotenv
from auth import AuthenticatorFactory  # Import the authentication module
import openai

# Load environment variables from config.env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'infras', 'config.env'))

# Azure Form Recognizer setup
FORM_RECOGNIZER_ENDPOINT = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")

# Azure OpenAI setup
OPENAI_API_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_MODEL = os.getenv("AZURE_OPENAI_MODEL_DEPLOYMENT_NAME")
#APIM_SUBSCRIPTION_KEY = os.getenv("AZURE_APIM_SUBSCRIPTION_KEY")

def analyze_document(file_path, document_analysis_client):
    """
    Analyze a document using Azure Form Recognizer.

    Args:
        file_path (str): The path to the document file to be analyzed.

    Returns:
        dict: A dictionary containing the extracted key-value pairs from the document and the page count.
    """
    # Read the document file
    with open(file_path, "rb") as f:
        document_content = f.read()

    # Analyze document
    poller = document_analysis_client.begin_analyze_document("prebuilt-layout", document_content)
    result = poller.result()

    extracted_data = {}
    for field in result.key_value_pairs:
        extracted_data[field.key] = field.value

    # Get the number of pages processed
    page_count = len(result.pages)

    return {"data": extracted_data, "page_count": page_count}

def evaluate_compliance(data, accounting_standards, openai_client):
    """
    Evaluate the compliance of extracted data with accounting standards using OpenAI.

    Args:
        data (dict): The extracted data from the document.
        accounting_standards (str): The accounting standards to evaluate compliance against.

    Returns:
        str: The compliance analysis result from OpenAI.
    """
    # Prepare prompt for OpenAI
    prompt = f"""
    Analyze the following contract data for compliance with the accounting standards:
    
    Contract Data: {data}

    Accounting Standards: {accounting_standards}

    Highlight any discrepancies or issues.
    """

    response = openai_client.ChatCompletion.create(
        engine=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a compliance analyst."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )

    return response["choices"][0]["message"]["content"]

def main():
    """
    Main function to analyze a contract document and evaluate its compliance with accounting standards.
    """
    # Set up authentication
    factory = AuthenticatorFactory(auth_type='managed_identity')  # Default to managed identity
    authenticator = factory.get_authenticator()
    credential = authenticator.get_credential()

    # Initialize Azure clients with the credential
    document_analysis_client = DocumentAnalysisClient(
        endpoint=FORM_RECOGNIZER_ENDPOINT,
        credential=credential
    )

    #openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
    openai.api_base = OPENAI_API_ENDPOINT
    openai.api_type = "azure"
    openai.api_version = "2024-11-20"

    # Define the file path for the contract
    contract_path = os.path.join(os.path.dirname(__file__), "..", "sample-data", "right_of_way_agreement.pdf")

    # Define accounting standards (you can extract this from PDF or hardcode it)
    #accounting_standards = "Insert accounting standards here or extract dynamically."

    # Step 1: Extract data using Form Recognizer
    analysis_result = analyze_document(contract_path, document_analysis_client)
    contract_data = analysis_result["data"]
    page_count = analysis_result["page_count"]

    # Log or store the page count for chargeback purposes
    print(f"Number of pages processed: {analysis_result}")
    print(f"Number of pages processed: {page_count}")
    print(f"Text of contract data processed: {contract_data}")
    
#     # Step 2: Evaluate compliance using OpenAI
#     compliance_result = evaluate_compliance(contract_data, accounting_standards, openai)

#     print("Compliance Analysis Result:")
#     print(compliance_result)

# if __name__ == "__main__":
#     main()
