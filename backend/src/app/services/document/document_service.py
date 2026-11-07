
from uuid import UUID

from fastapi import UploadFile

from .document_facade import DocumentServiceFacade


class DocumentUpload:

    @staticmethod
    async def process_document(files: list[UploadFile], user_id: UUID):
        await DocumentServiceFacade.document_pipeline(files = files, user_id = user_id)