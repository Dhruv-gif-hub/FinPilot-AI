import pymupdf
from fastapi import HTTPException, UploadFile

from ...schemas.pdf_extracts import PDF_data

MAX_FILE_SIZE = 50 * 1024 * 1024

async def extract_text_from_pdf(file: UploadFile):
    """
    Extracts text from a PDF file using PyMuPDF.

    Args:
        file_path (str): The path to the PDF file.
    """
    file_path = await file.read()
    if len(file_path) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max {MAX_FILE_SIZE // (1024*1024)} MB."
        )
    extracted_text = []
    with pymupdf.open(stream=file_path, filetype="pdf") as pdf_document:
        del file_path # Free memory after reading the file
        metadata = pdf_document.metadata
        size = len(pdf_document)
        page_count = pdf_document.page_count
        for page_number in range(page_count):
            page = pdf_document[page_number]
            text = page.get_text()
            extracted_text.append(text)

    object_data = PDF_data(content = extracted_text, metadata = metadata, size = size,
                           content_type = file.content_type, filename = file.filename)
    return object_data
