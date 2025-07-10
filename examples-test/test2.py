import os
import requests

# Read PDF file from sample-data folder
pdf_path = os.path.join("sample-data", "sample-invoice.pdf")

try:
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
except FileNotFoundError:
    print(f"Error: Could not find {pdf_path}")
    exit(1)

try:
    # Send raw PDF bytes directly
    response = requests.post(
        "http://localhost:7071/api/convert_pdf_to_images", 
        data=pdf_bytes,  # Send raw bytes, not JSON
        headers={'Content-Type': 'application/pdf'},
        timeout=30
    )
    
    response.raise_for_status()
    result = response.json()
    print(f"Success: {result}")
    
except requests.exceptions.RequestException as e:
    print(f"Error calling API: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response status: {e.response.status_code}")
        print(f"Response text: {e.response.text}")