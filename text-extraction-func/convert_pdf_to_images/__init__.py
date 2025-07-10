import json
import logging
import base64
import azure.functions as func
from shared_code.utils import (
    save_bytes_to_temp_file,
    create_temp_directory,
    cleanup_temp_files,
    convert_pdf_to_images,
)

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function HTTP trigger that converts a PDF file to a collection of images.
    
    This function:
    1. Extracts a PDF file from the request body
    2. Converts each page to a PNG image
    3. Returns both file paths and base64-encoded image data
    
    Parameters:
        req (func.HttpRequest): The HTTP request containing the PDF file in the body
    
    Returns:
        func.HttpResponse: JSON response containing:
            - success message with page count
            - total image count
            - list of images with page numbers and base64-encoded data
            
    Error responses:
        - 400 Bad Request: If no PDF is provided
        - 500 Internal Server Error: For processing failures
    """
    logging.info(
        "Python HTTP trigger function processed a request to convert PDF to images."
    )

    try:
        # Try to get JSON data first
        try:
            req_body = req.get_json()
            if req_body and 'file_data' in req_body:
                # Decode base64 PDF data
                pdf_base64 = req_body['file_data']
                pdf_bytes = base64.b64decode(pdf_base64)
            else:
                # Fall back to raw body for direct PDF upload
                pdf_bytes = req.get_body()
        except (ValueError, json.JSONDecodeError):
            # If JSON parsing fails, try raw body
            pdf_bytes = req.get_body()

        if not pdf_bytes:
            return func.HttpResponse(
                json.dumps({"error": "No PDF file provided"}),
                status_code=400,
                mimetype="application/json",
            )

        # Save PDF to temp file
        pdf_path = save_bytes_to_temp_file(pdf_bytes)
        
        # Create temporary directory for output images (optional)
        output_folder = create_temp_directory()

        # Convert PDF to images with base64 encoding
        result = convert_pdf_to_images(
            pdf_path, 
            output_folder=output_folder,
            return_base64=True
        )

        # Clean up the temporary PDF file
        cleanup_temp_files([pdf_path])

        return func.HttpResponse(
            json.dumps(
                {
                    "message": f"Converted {result['image_count']} pages to images",
                    "image_count": result['image_count'],
                    "images": result['image_data'],
                }
            ),
            mimetype="application/json",
        )

    except Exception as e:
        logging.error(f"Error converting PDF to images: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Error converting PDF: {str(e)}"}), 
            status_code=500, 
            mimetype="application/json"
        )
