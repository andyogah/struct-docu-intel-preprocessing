import os
import base64
import json
import requests

# Read PDF file from sample-data folder
pdf_path = os.path.join("sample-data", "right_of_way_agreement.pdf")

try:
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
except FileNotFoundError:
    print(f"Error: Could not find {pdf_path}")
    print("Make sure the sample-invoice.pdf file exists in the sample-data folder")
    exit(1)

# Encode as base64
pdf_base64 = base64.b64encode(pdf_bytes).decode()

# Set options
payload = {
    "file_data": pdf_base64,
    "options": {
        "convert_pdf": False,
        "preprocess_images": False,
        "analyze_layout": False,
        "analyze_content": True
    },
    "model": "prebuilt-document",  # Use specialized invoice model
    "preprocessing_options": {
        "apply_grayscale": False,
        "apply_blur": False,
        "apply_threshold": False,
        "apply_edge_detection": False
    }
}

try:
    # Call the API
    response = requests.post(
        "http://localhost:7071/api/process_document", 
        json=payload,
        timeout=30  # Add timeout for large files
    )
    
    # Check if request was successful
    response.raise_for_status()
    
    # Parse the response
    result = response.json()
    print(json.dumps(result, indent=2))
    
except requests.exceptions.RequestException as e:
    print(f"Error calling API: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response status: {e.response.status_code}")
        print(f"Response text: {e.response.text}")
except json.JSONDecodeError as e:
    print(f"Error parsing JSON response: {e}")
    print(f"Raw response: {response.text}")