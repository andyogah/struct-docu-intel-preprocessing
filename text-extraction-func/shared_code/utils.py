import os
import logging
import tempfile
import base64
from io import BytesIO
import fitz  # PyMuPDF
from PIL import Image  # For image processing
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Azure credentials
DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT")
DOCUMENT_INTELLIGENCE_KEY = os.getenv("DOCUMENT_INTELLIGENCE_KEY")


def convert_pdf_to_images(pdf_path, output_folder=None, dpi=300, return_base64=False):
    """
    Converts a PDF to individual images (one per page) using PyMuPDF.
    
    Args:
        pdf_path: Path to the PDF file
        output_folder: Folder to save the images (if None, images won't be saved to disk)
        dpi: Resolution for the output images (default 300)
        return_base64: Whether to return base64-encoded image data
        
    Returns:
        dict: Contains:
            - image_paths: List of paths to the generated images (if output_folder is provided)
            - image_count: Number of pages/images
            - image_data: List of dicts with page_number and base64-encoded image data (if return_base64=True)
    """
    # Calculate zoom factor based on DPI (PyMuPDF uses 72 DPI as base)
    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)
    
    # Open the PDF
    pdf_document = fitz.open(pdf_path)
    
    result = {
        "image_count": len(pdf_document)
    }
    
    image_paths = []
    image_data = []
    
    # Process each page
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        
        # Render page to pixmap (image)
        pix = page.get_pixmap(matrix=matrix)
        
        # Convert to PIL Image for consistent handling
        img_data = pix.tobytes("png")
        pil_image = Image.open(BytesIO(img_data))
        
        # Save image to disk if output_folder is provided
        if output_folder:
            output_path = os.path.join(output_folder, f"page_{page_num + 1}.png")
            pil_image.save(output_path, "PNG")
            image_paths.append(output_path)
        
        # Generate base64-encoded data if requested
        if return_base64:
            buffered = BytesIO()
            pil_image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            image_data.append({"page_number": page_num + 1, "image_data": img_str})
    
    # Close the PDF document
    pdf_document.close()
    
    # Add image paths to result if we saved images
    if output_folder:
        result["image_paths"] = image_paths
    
    # Add base64 data to result if requested
    if return_base64:
        result["image_data"] = image_data
    
    return result


def save_bytes_to_temp_file(file_bytes, suffix='.pdf'):
    """Save bytes to a temporary file and return the file path."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp_file.write(file_bytes)
    temp_file.close()
    return temp_file.name


def create_temp_directory():
    """Create a temporary directory and return the path."""
    return tempfile.mkdtemp()


def cleanup_temp_files(file_paths):
    """Clean up temporary files."""
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error cleaning up file {file_path}: {str(e)}")