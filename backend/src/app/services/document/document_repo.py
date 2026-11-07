
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.document_chunks import DocumentChunk
from ...models.documents import Document
from ...schemas.pdf_extracts import PDF_data
from ...schemas.util import Status
from ..embeddings.embeddings import get_embeddings
from ..ingestion.chunking import chunk_pages
from ..ingestion.extractor import extract_text_from_pdf


class DocumentService:

    @staticmethod
    async def extraction_service(file: UploadFile):
        """
        Handles the extraction of text from a PDF file.

        Args:
            file (UploadFile): The uploaded PDF file.
        """
        return extract_text_from_pdf(file = file)

    @staticmethod
    async def chunking_service(extracted_text):
        """
        Handles the chunking of extracted text.

        Args:
            extracted_text: The text extracted from the PDF.
        """
        chunks = chunk_pages(extracted_text)
        return chunks

    @staticmethod
    async def embedding_service(chunks):
        """
        Handles the embedding of chunks.

        Args:
            chunks: The chunks to be embedded.
        """
        embedding = get_embeddings(chunks)
        return embedding
    
    @staticmethod
    async def document_object(filename: str, metadata: dict | None, user_id : UUID, file_type: str, 
                              file_size: int, session : AsyncSession):
        object = Document(user_id = user_id,
                          filename = filename,
                          metadata = metadata,
                          mimetype = file_type,
                          file_size = file_size)
        session.add(object)
        await session.flush()
        return object


    @staticmethod
    async def process_document(user_id: UUID, extracted_text: PDF_data,
                               session: AsyncSession):
        """
        Orchestrates the document processing workflow: extraction, chunking, and embedding.

        Args:
            file (UploadFile): The uploaded PDF file.
        """

        doc = await DocumentService.document_object(
                                            filename = extracted_text.filename or "unnamed", 
                                            metadata = extracted_text.metadata,
                                            user_id = user_id, 
                                            file_type = extracted_text.content_type or "application/octet-stream",
                                            file_size = extracted_text.size, session = session
                                            )
        document_id = doc.id
        doc.status = Status.PROCESSING
        session.add(doc)
        await session.commit()
        try:
            chunks = await DocumentService.chunking_service(extracted_text.content)
            embedding = await DocumentService.embedding_service(chunks)
            session.add_all(
                DocumentChunk(document_id = document_id,
                                            user_id = user_id,
                                            content = chunk,
                                            chunk_index = i,
                                            embedding = embd,
                )
                for i, (chunk, embd) in enumerate(zip(chunks, embedding))

            )
            doc.status = Status.COMPLETED

        except Exception:
            doc.status = Status.FAILED
            raise