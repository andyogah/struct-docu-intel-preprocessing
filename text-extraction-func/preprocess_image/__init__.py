
import json
import logging
from io import BytesIO
import base64
import cv2
import numpy as np
import azure.functions as func
from shared_code.utils import save_bytes_to_temp_file

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request to preprocess an image.')
    
    try:
        # Parse request body
        req_body = req.get_json()
        
        # Get the image as base64 string
        image_data = req_body.get('image_data')
        if not image_data:
            return func.HttpResponse(
                json.dumps({"error": "No image data provided"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Get preprocessing options
        options = req_body.get('options', {})
        apply_grayscale = options.get('apply_grayscale', False)
        apply_blur = options.get('apply_blur', False)
        apply_threshold = options.get('apply_threshold', False)
        apply_edge_detection = options.get('apply_edge_detection', False)
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Apply preprocessing steps based on options
        processed_image = image.copy()
        
        if apply_grayscale:
            processed_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2GRAY)
            
        if apply_blur:
            # Ensure image is grayscale for blur
            if len(processed_image.shape) == 3:
                processed_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2GRAY)
            processed_image = cv2.GaussianBlur(processed_image, (5, 5), 0)
            
        if apply_threshold:
            # Ensure image is grayscale for threshold
            if len(processed_image.shape) == 3:
                processed_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2GRAY)
            _, processed_image = cv2.threshold(processed_image, 150, 255, cv2.THRESH_BINARY)
            
        if apply_edge_detection:
            # Ensure image is grayscale for edge detection
            if len(processed_image.shape) == 3:
                processed_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2GRAY)
            processed_image = cv2.Canny(processed_image, 50, 150)
        
        # Encode the processed image to base64
        _, buffer = cv2.imencode('.png', processed_image)
        processed_image_data = base64.b64encode(buffer).decode('utf-8')
        
        return func.HttpResponse(
            json.dumps({
                "message": "Image preprocessed successfully",
                "processed_image": processed_image_data
            }),
            mimetype="application/json"
        )
    
    except Exception as e:
        logging.error(f"Error preprocessing image: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )