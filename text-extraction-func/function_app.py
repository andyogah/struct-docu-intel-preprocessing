


import logging
import azure.functions as func

# Import all your existing functions
from convert_pdf_to_images.__init__ import main as pdf_to_images_func
from analyze_document.__init__ import main as analyze_document_func
from analyze_layout.__init__ import main as analyze_layout_func
from preprocess_image.__init__ import main as preprocess_image_func
from process_document.__init__ import main as process_document_func

# Create the function app
app = func.FunctionApp()

# Register each function with its own route
@app.route(route="convert_pdf_to_images", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def convert_pdf_to_images(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('PDF to images function processed a request.')
    return pdf_to_images_func(req)

# Add decorators for your other functions
@app.route(route="analyze_document", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET", "POST"])
def analyze_document(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Function2 processed a request.')
    return analyze_document_func(req)

@app.route(route="analyze_layout", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def analyze_layout(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Function3 processed a request.')
    return analyze_layout_func(req)

@app.route(route="preprocess_image", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET", "POST"])
def preprocess_image(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Function4 processed a request.')
    return preprocess_image_func(req)

@app.route(route="process_document", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET", "POST"])
def process_document(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Function4 processed a request.')
    return process_document_func(req)


