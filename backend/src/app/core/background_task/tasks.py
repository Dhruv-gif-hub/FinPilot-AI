
import asyncio
from uuid import UUID

from celery import shared_task

from ...db.session import Session_local
from ...schemas.pdf_extracts import PDF_data
from ...services.document.document_repo import DocumentService


@shared_task(autoretry_for=(Exception,), max_retries = 5, retry_backoff = True, retry_backoff_max = 10,
             retry_jitter = True)
def BackgroundDocumentUpload(user_id: str, extracted_text):
    async def run_pipeline():
        async with Session_local() as session:
            try:
                pdf_data = PDF_data.model_validate(extracted_text)
                await DocumentService.process_document(session = session, user_id = UUID(user_id),
                                                    extracted_text = pdf_data)
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    asyncio.run(run_pipeline())