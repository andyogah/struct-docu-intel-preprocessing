import requests
import base64
import json
import os
import sys

# Add the project root to the path so we can import shared_code
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Function to process a document
def process_document(file_path, use_vision_api=False):
    # Read file
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    # Determine file type
    file_extension = os.path.splitext(file_path)[1].lower()
    is_pdf = file_extension == '.pdf'
    
    # Encode as base64
    file_base64 = base64.b64encode(file_bytes).decode()

    # Set options
    payload = {
        "file_data": file_base64,
        "file_type": file_extension[1:],  # Remove the dot
        "options": {
            "convert_pdf": is_pdf,
            "preprocess_images": True,
            "analyze_layout": True,
            "analyze_content": True,
            "use_vision_api": use_vision_api
        },
        "model": "prebuilt-document" if not is_pdf else "prebuilt-layout",
        "preprocessing_options": {
            "apply_grayscale": True,
            "apply_blur": False,
            "apply_threshold": False,
            "apply_edge_detection": False
        }
    }

    # Call the API
    # For local testing, use http://localhost:7071
    # For deployed function app, use https://your-function-app.azurewebsites.net
    response = requests.post(
        "http://localhost:7071/api/ProcessDocument",
        json=payload
    )

    # Parse the response
    if response.status_code == 200:
        result = response.json()
        print(f"Document processed successfully with {'Vision API' if use_vision_api else 'Document Intelligence'}")
        return result
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# Main function
def main():
    # Example usage: process a PDF with Document Intelligence
    print("Processing document with Document Intelligence...")
    di_result = process_document("../sample-data/sample-invoice.pdf", use_vision_api=False)
    print(json.dumps(di_result, indent=2))
    
    # Example usage: process the same PDF with Vision API
    print("\nProcessing document with Vision API...")
    vision_result = process_document("../sample-data/sample-invoice.pdf", use_vision_api=True)
    print(json.dumps(vision_result, indent=2))
    
    # Example with an image file
    print("\nProcessing image file...")
    image_result = process_document("../sample-data/sample-receipt.jpg", use_vision_api=False)
    print(json.dumps(image_result, indent=2))

if __name__ == "__main__":
    main()
