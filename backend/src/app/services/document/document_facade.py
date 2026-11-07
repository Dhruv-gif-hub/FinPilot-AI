
import asyncio
from uuid import UUID

from fastapi import UploadFile

from ...core.background_task.tasks import BackgroundDocumentUpload
from .document_repo import DocumentService


class DocumentServiceFacade:

    @staticmethod
    async def document_pipeline(files: list[UploadFile], user_id: UUID):
        semaphore = asyncio.Semaphore(3)

        async def extract(file: UploadFile):
            async with semaphore:
                extracted_text = await DocumentService.extraction_service(file)
                return extracted_text

        tasks = [
            asyncio.create_task(extract(file))
            for file in files
        ]

        try:
            for completed in asyncio.as_completed(tasks):
                extracted_text = await completed

            BackgroundDocumentUpload.delay(
                user_id = str(user_id),
                extracted_text = extracted_text.model_dump(mode="json")) # type: ignore
        finally:
            for task in tasks:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)