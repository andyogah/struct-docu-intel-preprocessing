import json
import logging
import base64
import azure.functions as func
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from shared_code.utils import save_bytes_to_temp_file, DOCUMENT_INTELLIGENCE_ENDPOINT, DOCUMENT_INTELLIGENCE_KEY

# def main(req: func.HttpRequest) -> func.HttpResponse:
#     logging.info('Python HTTP trigger function processed a request to analyze document content.')
    
#     try:
#         # Parse request body
#         req_body = req.get_json()
        
#         # Get the image as base64 string
#         image_data = req_body.get('image_data')
#         if not image_data:
#             return func.HttpResponse(
#                 json.dumps({"error": "No image data provided"}),
#                 status_code=400,
#                 mimetype="application/json"
#             )
            
#         # Get the model to use (default to prebuilt-document)
#         model = req_body.get('model', 'prebuilt-document')
        
#         # Decode base64 image
#         image_bytes = base64.b64decode(image_data)
        
#         # Save image to temp file
#         image_path = save_bytes_to_temp_file(image_bytes, suffix='.png')
        
#         # Initialize Azure Document Intelligence client
#         client = DocumentAnalysisClient(
#             DOCUMENT_INTELLIGENCE_ENDPOINT, 
#             AzureKeyCredential(DOCUMENT_INTELLIGENCE_KEY)
#         )
        
#         # Analyze the document
#         with open(image_path, "rb") as image_file:
#             poller = client.begin_analyze_document(model, image_file)
#             result = poller.result()
        
#         # Extract comprehensive document information
#         document_results = {
#             "full_text": result.content if result.content else "",
#             "languages": [],
#             "styles": [],
#             "paragraphs": [],
#             "pages": [],
#             "tables": [],
#             "key_value_pairs": [],
#             "documents": []
#         }
        
#         # Extract detected languages
#         if hasattr(result, 'languages') and result.languages:
#             for language in result.languages:
#                 document_results["languages"].append({
#                     "locale": language.locale,
#                     "confidence": language.confidence,
#                     "spans": [{"offset": span.offset, "length": span.length} for span in language.spans]
#                 })
        
#         # Extract text styles (handwritten, bold, etc.)
#         if hasattr(result, 'styles') and result.styles:
#             for style in result.styles:
#                 style_info = {
#                     "is_handwritten": getattr(style, 'is_handwritten', False),
#                     "confidence": getattr(style, 'confidence', 0.0),
#                     "spans": [{"offset": span.offset, "length": span.length} for span in style.spans]
#                 }
#                 document_results["styles"].append(style_info)
        
#         # Extract paragraphs
#         if hasattr(result, 'paragraphs') and result.paragraphs:
#             for para_idx, paragraph in enumerate(result.paragraphs):
#                 para_info = {
#                     "paragraph_index": para_idx,
#                     "content": paragraph.content,
#                     "role": getattr(paragraph, 'role', None),  # title, sectionHeading, etc.
#                     "bounding_regions": []
#                 }
                
#                 # Add bounding regions if available
#                 if hasattr(paragraph, 'bounding_regions') and paragraph.bounding_regions:
#                     for region in paragraph.bounding_regions:
#                         para_info["bounding_regions"].append({
#                             "page_number": region.page_number,
#                             "polygon": region.polygon
#                         })
                
#                 # Add spans if available
#                 if hasattr(paragraph, 'spans') and paragraph.spans:
#                     para_info["spans"] = [
#                         {"offset": span.offset, "length": span.length} 
#                         for span in paragraph.spans
#                     ]
                
#                 document_results["paragraphs"].append(para_info)
        
#         # Extract page-level information (lines, words, etc.)
#         if hasattr(result, 'pages') and result.pages:
#             for page_idx, page in enumerate(result.pages):
#                 page_data = {
#                     "page_number": page_idx + 1,
#                     "width": page.width,
#                     "height": page.height,
#                     "unit": page.unit,
#                     "angle": getattr(page, 'angle', 0.0),
#                     "lines": [],
#                     "words": [],
#                     "selection_marks": []
#                 }
                
#                 # Extract lines
#                 if hasattr(page, 'lines') and page.lines:
#                     for line_idx, line in enumerate(page.lines):
#                         line_data = {
#                             "line_index": line_idx,
#                             "content": line.content,
#                             "polygon": line.polygon
#                         }
                        
#                         # Add spans if available
#                         if hasattr(line, 'spans') and line.spans:
#                             line_data["spans"] = [
#                                 {"offset": span.offset, "length": span.length}
#                                 for span in line.spans
#                             ]
                        
#                         page_data["lines"].append(line_data)
                
#                 # Extract words (you already have this, but with more detail)
#                 if hasattr(page, 'words') and page.words:
#                     for word_idx, word in enumerate(page.words):
#                         word_data = {
#                             "word_index": word_idx,
#                             "content": word.content,
#                             "confidence": word.confidence,
#                             "polygon": word.polygon
#                         }
                        
#                         # Add spans if available
#                         if hasattr(word, 'spans') and word.spans:
#                             word_data["spans"] = [
#                                 {"offset": span.offset, "length": span.length}
#                                 for span in word.spans
#                             ]
                        
#                         page_data["words"].append(word_data)
                
#                 # Extract selection marks (checkboxes, radio buttons)
#                 if hasattr(page, 'selection_marks') and page.selection_marks:
#                     for mark_idx, mark in enumerate(page.selection_marks):
#                         mark_data = {
#                             "mark_index": mark_idx,
#                             "state": mark.state,  # "selected" or "unselected"
#                             "confidence": mark.confidence,
#                             "polygon": mark.polygon
#                         }
                        
#                         if hasattr(mark, 'spans') and mark.spans:
#                             mark_data["spans"] = [
#                                 {"offset": span.offset, "length": span.length}
#                                 for span in mark.spans
#                             ]
                        
#                         page_data["selection_marks"].append(mark_data)
                
#                 document_results["pages"].append(page_data)
        
#         # Extract tables (if any)
#         if hasattr(result, 'tables') and result.tables:
#             for table_idx, table in enumerate(result.tables):
#                 table_data = {
#                     "table_index": table_idx,
#                     "row_count": table.row_count,
#                     "column_count": table.column_count,
#                     "cells": [],
#                     "bounding_regions": []
#                 }
                
#                 # Extract cells
#                 for cell in table.cells:
#                     cell_data = {
#                         "content": cell.content,
#                         "row_index": cell.row_index,
#                         "column_index": cell.column_index,
#                         "row_span": getattr(cell, 'row_span', 1),
#                         "column_span": getattr(cell, 'column_span', 1),
#                         "kind": getattr(cell, 'kind', None),  # "content", "rowHeader", "columnHeader"
#                         "confidence": getattr(cell, 'confidence', 0.0),
#                         "polygon": getattr(cell, 'polygon', [])
#                     }
                    
#                     if hasattr(cell, 'spans') and cell.spans:
#                         cell_data["spans"] = [
#                             {"offset": span.offset, "length": span.length}
#                             for span in cell.spans
#                         ]
                    
#                     table_data["cells"].append(cell_data)
                
#                 # Add table bounding regions
#                 if hasattr(table, 'bounding_regions') and table.bounding_regions:
#                     for region in table.bounding_regions:
#                         table_data["bounding_regions"].append({
#                             "page_number": region.page_number,
#                             "polygon": region.polygon
#                         })
                
#                 document_results["tables"].append(table_data)
        
#         # Extract key-value pairs (if any)
#         if hasattr(result, 'key_value_pairs') and result.key_value_pairs:
#             for kv_pair in result.key_value_pairs:
#                 kv_data = {
#                     "key": kv_pair.key.content if kv_pair.key else None,
#                     "value": kv_pair.value.content if kv_pair.value else None,
#                     "confidence": kv_pair.confidence
#                 }
#                 document_results["key_value_pairs"].append(kv_data)
        
#         # Extract document-level information (for prebuilt models)
#         if hasattr(result, 'documents') and result.documents:
#             for doc_idx, document in enumerate(result.documents):
#                 doc_data = {
#                     "document_index": doc_idx,
#                     "doc_type": document.doc_type,
#                     "confidence": document.confidence,
#                     "fields": {}
#                 }
                
#                 # Extract structured fields
#                 for field_name, field in document.fields.items():
#                     doc_data["fields"][field_name] = {
#                         "content": getattr(field, 'content', None),
#                         "confidence": getattr(field, 'confidence', 0.0),
#                         "value_type": str(getattr(field, 'value_type', 'unknown'))
#                     }
                
#                 document_results["documents"].append(doc_data)
                
#         return func.HttpResponse(
#             json.dumps({
#                 "message": "Document analyzed successfully",
#                 "model": model,
#                 "result": document_results
#             }),
#             mimetype="application/json"
#         )
    
#     except Exception as e:
#         logging.error(f"Error analyzing document: {str(e)}")
#         return func.HttpResponse(
#             json.dumps({"error": str(e)}),
#             status_code=500,
#             mimetype="application/json"
#         )








def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request to analyze document content.')
    
    try:
        # ... existing code for getting image_data and model ...
        
        # Analyze the document
        with open(image_path, "rb") as image_file:
            poller = client.begin_analyze_document(model, image_file)
            result = poller.result()
        
        # DEBUG: Log what's available in the result
        logging.info("=== DEBUG: Available attributes in result ===")
        for attr in dir(result):
            if not attr.startswith('_'):
                value = getattr(result, attr)
                if hasattr(value, '__len__') and not isinstance(value, str):
                    logging.info(f"{attr}: {type(value).__name__} with {len(value)} items")
                else:
                    logging.info(f"{attr}: {type(value).__name__}")
        
        # Extract comprehensive document information
        document_results = {
            "full_text": result.content if result.content else "",
            "languages": [],
            "styles": [],
            "paragraphs": [],
            "pages": [],
            "tables": [],
            "key_value_pairs": [],
            "documents": [],
            "debug_info": {
                "has_content": bool(result.content),
                "content_length": len(result.content) if result.content else 0,
                "has_pages": bool(result.pages),
                "page_count": len(result.pages) if result.pages else 0,
                "has_paragraphs": bool(getattr(result, 'paragraphs', None)),
                "paragraph_count": len(result.paragraphs) if getattr(result, 'paragraphs', None) else 0,
                "has_languages": bool(getattr(result, 'languages', None)),
                "has_styles": bool(getattr(result, 'styles', None)),
                "model_used": model
            }
        }
        
        # Log the debug info
        logging.info(f"Debug info: {document_results['debug_info']}")
        
        # Extract detected languages
        if hasattr(result, 'languages') and result.languages:
            logging.info(f"Found {len(result.languages)} languages")
            for language in result.languages:
                document_results["languages"].append({
                    "locale": language.locale,
                    "confidence": language.confidence,
                    "spans": [{"offset": span.offset, "length": span.length} for span in language.spans]
                })
        else:
            logging.info("No languages found or languages attribute missing")
        
        # Extract text styles
        if hasattr(result, 'styles') and result.styles:
            logging.info(f"Found {len(result.styles)} styles")
            for style in result.styles:
                style_info = {
                    "is_handwritten": getattr(style, 'is_handwritten', False),
                    "confidence": getattr(style, 'confidence', 0.0),
                    "spans": [{"offset": span.offset, "length": span.length} for span in style.spans]
                }
                document_results["styles"].append(style_info)
        else:
            logging.info("No styles found or styles attribute missing")
        
        # Extract paragraphs
        if hasattr(result, 'paragraphs') and result.paragraphs:
            logging.info(f"Found {len(result.paragraphs)} paragraphs")
            for para_idx, paragraph in enumerate(result.paragraphs):
                para_info = {
                    "paragraph_index": para_idx,
                    "content": paragraph.content,
                    "role": getattr(paragraph, 'role', None),
                    "bounding_regions": []
                }
                
                if hasattr(paragraph, 'bounding_regions') and paragraph.bounding_regions:
                    for region in paragraph.bounding_regions:
                        para_info["bounding_regions"].append({
                            "page_number": region.page_number,
                            "polygon": region.polygon
                        })
                
                if hasattr(paragraph, 'spans') and paragraph.spans:
                    para_info["spans"] = [
                        {"offset": span.offset, "length": span.length} 
                        for span in paragraph.spans
                    ]
                
                document_results["paragraphs"].append(para_info)
        else:
            logging.info("No paragraphs found or paragraphs attribute missing")
        
        # Extract page-level information (this should always work)
        if hasattr(result, 'pages') and result.pages:
            logging.info(f"Found {len(result.pages)} pages")
            for page_idx, page in enumerate(result.pages):
                page_data = {
                    "page_number": page_idx + 1,
                    "width": page.width,
                    "height": page.height,
                    "unit": page.unit,
                    "angle": getattr(page, 'angle', 0.0),
                    "lines": [],
                    "words": [],
                    "selection_marks": []
                }
                
                # Extract lines
                if hasattr(page, 'lines') and page.lines:
                    logging.info(f"Page {page_idx + 1}: Found {len(page.lines)} lines")
                    for line_idx, line in enumerate(page.lines):
                        line_data = {
                            "line_index": line_idx,
                            "content": line.content,
                            "polygon": line.polygon
                        }
                        
                        if hasattr(line, 'spans') and line.spans:
                            line_data["spans"] = [
                                {"offset": span.offset, "length": span.length}
                                for span in line.spans
                            ]
                        
                        page_data["lines"].append(line_data)
                else:
                    logging.info(f"Page {page_idx + 1}: No lines found")
                
                # Extract words
                if hasattr(page, 'words') and page.words:
                    logging.info(f"Page {page_idx + 1}: Found {len(page.words)} words")
                    for word_idx, word in enumerate(page.words):
                        word_data = {
                            "word_index": word_idx,
                            "content": word.content,
                            "confidence": word.confidence,
                            "polygon": word.polygon
                        }
                        
                        if hasattr(word, 'spans') and word.spans:
                            word_data["spans"] = [
                                {"offset": span.offset, "length": span.length}
                                for span in word.spans
                            ]
                        
                        page_data["words"].append(word_data)
                
                document_results["pages"].append(page_data)
        
        # ... rest of your existing code for tables, key_value_pairs, documents ...
                
        return func.HttpResponse(
            json.dumps({
                "message": "Document analyzed successfully",
                "model": model,
                "result": document_results
            }),
            mimetype="application/json"
        )
    
    except Exception as e:
        logging.error(f"Error analyzing document: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )







