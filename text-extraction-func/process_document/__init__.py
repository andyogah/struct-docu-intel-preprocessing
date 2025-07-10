import json
import logging
import base64
import os
import requests
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request to process a document.')
    
    try:
        # Parse request body
        req_body = req.get_json()
        
        # Get processing options
        options = req_body.get('options', {})
        convert_pdf = options.get('convert_pdf', True)
        preprocess_images = options.get('preprocess_images', False)
        analyze_layout = options.get('analyze_layout', False)
        analyze_content = options.get('analyze_content', True)
        
        # Get the model to use for document analysis
        model = req_body.get('model', 'prebuilt-document')
        
        # Get preprocessing options
        preprocessing_options = req_body.get('preprocessing_options', {})
        
        # Get file data (PDF or image)
        file_data = req_body.get('file_data')
        if not file_data:
            return func.HttpResponse(
                json.dumps({"error": "No file data provided"}),
                status_code=400,
                mimetype="application/json"
            )
            
        base_url = get_base_url(req)
        results = {}
        
        # Convert PDF to images if needed
        if convert_pdf:
            pdf_bytes = base64.b64decode(file_data)
            pdf_response = convert_pdf_to_images(base_url, pdf_bytes)
            
            if 'error' in pdf_response:
                return func.HttpResponse(
                    json.dumps(pdf_response),
                    status_code=500,
                    mimetype="application/json"
                )
                
            results['pdf_conversion'] = pdf_response
            images = pdf_response.get('images', [])
        else:
            # If not converting PDF, treat file_data as single image
            images = [{"page_number": 1, "image_data": file_data}]
            
        # Process each image
        page_results = []
        for image in images:
            page_number = image['page_number']
            image_data = image['image_data']
            page_result = {"page_number": page_number}
            
            # Preprocess image if needed
            if preprocess_images:
                preprocessed = preprocess_image(base_url, image_data, preprocessing_options)
                
                if 'error' in preprocessed:
                    page_result['preprocessing_error'] = preprocessed['error']
                else:
                    page_result['preprocessing'] = "success"
                    image_data = preprocessed.get('processed_image', image_data)
            
            # Analyze layout if needed
            if analyze_layout:
                layout = analyze_document_layout(base_url, image_data)
                
                if 'error' in layout:
                    page_result['layout_error'] = layout['error']
                else:
                    page_result['layout'] = layout.get('result', {})
            
            # Analyze content if needed
            if analyze_content:
                content = analyze_document_content(base_url, image_data, model)
                
                if 'error' in content:
                    page_result['content_error'] = content['error']
                else:
                    page_result['content'] = content.get('result', {})
            
            page_results.append(page_result)
            
        results['pages'] = page_results
        
        return func.HttpResponse(
            json.dumps(results),
            mimetype="application/json"
        )
    
    except Exception as e:
        logging.error(f"Error processing document: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

def get_base_url(req):
    """Get the base URL for function calls."""
    # For local development
    if req.headers.get('x-forwarded-host'):
        return f"https://{req.headers.get('x-forwarded-host')}"
    return "http://localhost:7071"

def convert_pdf_to_images(base_url, pdf_bytes):
    """Call the ConvertPdfToImages function."""
    try:
        response = requests.post(
            f"{base_url}/api/convert_pdf_to_images",
            data=pdf_bytes,
            headers={"Content-Type": "application/pdf"},
            timeout=30  # Increased from 10 to 30 seconds
        )
        return response.json()
    except Exception as e:
        return {"error": f"Error converting PDF: {str(e)}"}

def preprocess_image(base_url, image_data, options):
    """Call the PreprocessImage function."""
    try:
        response = requests.post(
            f"{base_url}/api/preprocess_image",
            json={"image_data": image_data, "options": options},
            headers={"Content-Type": "application/json"},
            timeout=30  # Increased from 10 to 30 seconds
        )
        return response.json()
    except Exception as e:
        return {"error": f"Error preprocessing image: {str(e)}"}

def analyze_document_layout(base_url, image_data):
    """Call the AnalyzeLayout function."""
    try:
        response = requests.post(
            f"{base_url}/api/analyze_layout",
            json={"image_data": image_data},
            headers={"Content-Type": "application/json"},
            timeout=45  # Increased from 10 to 45 seconds
        )
        return response.json()
    except Exception as e:
        return {"error": f"Error analyzing layout: {str(e)}"}

def analyze_document_content(base_url, image_data, model):
    """Call the AnalyzeDocument function."""
    try:
        response = requests.post(
            f"{base_url}/api/analyze_document",
            json={"image_data": image_data, "model": model},
            headers={"Content-Type": "application/json"},
            timeout=60  # Increased from 10 to 60 seconds
        )
        return response.json()
    except Exception as e:
        return {"error": f"Error analyzing content: {str(e)}"}