import json
import logging
import base64
import azure.functions as func
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from shared_code.utils import (
    save_bytes_to_temp_file,
    DOCUMENT_INTELLIGENCE_ENDPOINT,
    DOCUMENT_INTELLIGENCE_KEY,
)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(
        "Python HTTP trigger function processed a request to analyze document layout."
    )

    try:
        # Parse request body
        req_body = req.get_json()

        # Get the image as base64 string
        image_data = req_body.get("image_data")
        if not image_data:
            return func.HttpResponse(
                json.dumps({"error": "No image data provided"}),
                status_code=400,
                mimetype="application/json",
            )

        # Decode base64 image
        image_bytes = base64.b64decode(image_data)

        # Save image to temp file
        image_path = save_bytes_to_temp_file(image_bytes, suffix=".png")

        # Initialize Azure Document Intelligence client
        client = DocumentAnalysisClient(
            DOCUMENT_INTELLIGENCE_ENDPOINT,
            AzureKeyCredential(DOCUMENT_INTELLIGENCE_KEY),
        )

        # Analyze the document layout
        with open(image_path, "rb") as image_file:
            poller = client.begin_analyze_document("prebuilt-layout", image_file)
            result = poller.result()

        # Extract and format result
        layout_result = {"pages": [], "tables": []}

        for page in result.pages:
            page_info = {
                "page_number": page.page_number,
                "width": page.width,
                "height": page.height,
                "unit": page.unit,
                "lines": [],
            }

            for line in page.lines:
                line_info = {
                    "text": line.content,
                    "bounding_regions": [
                        {"offset": span.offset, "length": span.length}
                        for span in (line.spans or [])
                    ],
                }
                page_info["lines"].append(line_info)

            layout_result["pages"].append(page_info)

        for table in result.tables:
            table_info = {
                "row_count": table.row_count,
                "column_count": table.column_count,
                "cells": [],
            }

            for cell in table.cells:
                cell_info = {
                    "row_index": cell.row_index,
                    "column_index": cell.column_index,
                    "text": cell.content,
                    "bounding_regions": [
                        {"offset": span.offset, "length": span.length}
                        for span in (cell.spans or [])
                    ],
                }
                table_info["cells"].append(cell_info)

            layout_result["tables"].append(table_info)

        return func.HttpResponse(
            json.dumps(
                {
                    "message": "Document layout analyzed successfully",
                    "result": layout_result,
                }
            ),
            mimetype="application/json",
        )

    except Exception as e:
        logging.error(f"Error analyzing document layout: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}), status_code=500, mimetype="application/json"
        )
