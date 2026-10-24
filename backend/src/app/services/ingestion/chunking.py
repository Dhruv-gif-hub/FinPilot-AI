from langchain_text_splitters import RecursiveCharacterTextSplitter

from ...models.object_models.pdf_chunks import PDFChunks
from ...models.object_models.pdf_extracts import PDFExtracts


def chunk_pages(pages: PDFExtracts, chunk_size: int = 1000, chunk_overlap: int = 200) -> list[PDFChunks]:
    """
    Splits the extracted text from PDF pages into smaller chunks.

    Args:
        pages (PDFExtracts): The extracted text from PDF pages.
        chunk_size (int): The maximum size of each chunk.
        chunk_overlap (int): The number of overlapping characters between chunks.

    Returns:
        list[PDFChunks]: A list of PDFChunks containing the split text.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = []
    for page in pages.content:
        page_chunks = text_splitter.split_text(page)
        for chunk in page_chunks:
            chunks.append(PDFChunks(content=chunk))
    return chunks