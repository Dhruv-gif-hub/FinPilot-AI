from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile

from app.core.middleware.rate_limit import rate_limiter

from ..core.dependencies import require_write_user
from ..models.user import User
from ..services.document.document_service import DocumentUpload

router = APIRouter(prefix="/documents")


upload_limiter = rate_limiter(max_requests=2, window_seconds=60)

@router.post("/UploadDocument", dependencies=[Depends(upload_limiter)])
async def document_upload(files: list[UploadFile], user: Annotated[User, Depends(require_write_user)]):
    await DocumentUpload.process_document(files = files, user_id = user.id)

