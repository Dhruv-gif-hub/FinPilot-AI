from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Path, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.dependencies import require_write_user
from ..db.db_instance import get_db
from ..schemas.response import Transaction
from ..services.membership.user_merchant_service import MerchantMembershipService
from ..services.transaction_service.TransactionService import import_financial_csv

router = APIRouter(
    prefix="/merchants",
    tags=["Transactions"],
)



@router.post("/{merchant_id}/transactions/import", response_model=Transaction)
async def upload_transactions_csv(
    session: Annotated[AsyncSession, Depends(get_db)],
    merchant_id: Annotated[UUID, Path()],
    file: Annotated[UploadFile, File(...)],
    current_user=Depends(require_write_user),
):

    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a CSV file.",
        )

    # Verify tenant access before importing.
    await MerchantMembershipService.verify_merchant_access(
        session,
        current_user.id,
        merchant_id,
    )

    result = await import_financial_csv(
        session,
        merchant_id=merchant_id,
        file=file,
    )


    return {
        "message": "Transaction CSV imported successfully.",
        **result,
    }