from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.db_instance import get_db
from ..services.Merchant.merchantservice import MerchantSetupService

router = APIRouter(prefix="/merchants", tags=["Merchants"],)


@router.post("/import")
async def import_merchants(
    session: Annotated[AsyncSession, Depends(get_db)],
    file: Annotated[UploadFile, File(...)]):

    if not file.filename or not file.filename.lower().endswith(".csv"):
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail="Please upload a CSV file.",
        )

    result = await MerchantSetupService.import_merchants(
        session,
        file=file,
    )


    return {
        "message": "Merchant import completed.",
        **result,
    }