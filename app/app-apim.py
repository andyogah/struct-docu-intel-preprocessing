"""
Module: app-apim.py

This module provides functionality to analyze documents using Azure Form Recognizer
and evaluate their compliance with accounting standards using OpenAI.

Functions:
- analyze_document(file_path): Analyzes a document using Azure Form Recognizer and extracts key-value pairs.
- evaluate_compliance(data, accounting_standards): Evaluates the compliance of extracted data with accounting standards using OpenAI.
- main(): Main function to analyze a contract document and evaluate its compliance with accounting standards.
"""

import os
from dotenv import load_dotenv
import requests

# Load environment variables from config.env
load_dotenv()

# Azure Form Recognizer and OpenAI setup
APIM_ENDPOINT = os.getenv("AZURE_APIM_ENDPOINT")
APIM_SUBSCRIPTION_KEY = os.getenv("AZURE_APIM_SUBSCRIPTION_KEY")
OPENAI_MODEL = os.getenv("AZURE_OPENAI_MODEL_DEPLOYMENT_NAME")

def analyze_document(file_path):
    """
    Analyze a document using Azure Form Recognizer.

    Args:
        file_path (str): The path to the document file to be analyzed.

    Returns:
        dict: A dictionary containing the extracted key-value pairs from the document and the page count.
    """
    headers = {
        "Ocp-Apim-Subscription-Key": APIM_SUBSCRIPTION_KEY
    }

    # Read the document file
    with open(file_path, "rb") as f:
        document_content = f.read()

    # Analyze document
    response = requests.post(
        f"{APIM_ENDPOINT}/formrecognizer/v2.1/prebuilt/receipt/analyze",
        headers=headers,
        data=document_content,
        timeout=30  # Add a timeout of 30 seconds
    )

    result = response.json()

    extracted_data = {}
    for field in result["analyzeResult"]["documentResults"][0]["fields"]:
        extracted_data[field] = result["analyzeResult"]["documentResults"][0]["fields"][field]["text"]

    # Get the number of pages processed
    page_count = len(result["analyzeResult"]["readResults"])

    return {"data": extracted_data, "page_count": page_count}

def evaluate_compliance(data, accounting_standards):
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

    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": APIM_SUBSCRIPTION_KEY
    }

    response = requests.post(
        f"{APIM_ENDPOINT}/openai/deployments/{OPENAI_MODEL}/chat/completions?api-version=2024-11-20",
        headers=headers,
        json={
            "messages": [
                {"role": "system", "content": "You are a compliance analyst."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 500
        },
        timeout=30  # Add a timeout of 30 seconds
    )

    response_json = response.json()
    return response_json["choices"][0]["message"]["content"]

def main():
    """
    Main function to analyze a contract document and evaluate its compliance with accounting standards.
    """
    # Define the file path for the contract
    contract_path = os.path.join(os.path.dirname(__file__), "..", "sample-data", "right_of_way_agreement.pdf")

    # Define accounting standards (you can extract this from PDF or hardcode it)
    accounting_standards = "Insert accounting standards here or extract dynamically."

    # Step 1: Extract data using Form Recognizer
    analysis_result = analyze_document(contract_path)
    contract_data = analysis_result["data"]
    page_count = analysis_result["page_count"]

    # Log or store the page count for chargeback purposes
    print(f"Number of pages processed: {page_count}")
    
    # Step 2: Evaluate compliance using OpenAI
    compliance_result = evaluate_compliance(contract_data, accounting_standards)

    print("Compliance Analysis Result:")
    print(compliance_result)

if __name__ == "__main__":
    main()
