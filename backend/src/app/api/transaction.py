from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.dependencies import require_write_user
from ..db.db_instance import get_db
from ..services.membership.user_merchant_service import MerchantMembershipService
from ..services.transaction_service.TransactionService import import_transactions_csv

router = APIRouter(
    prefix="/merchants",
    tags=["Transactions"],
)



@router.post("/{merchant_id}/transactions/import")
async def upload_transactions_csv(
    session: Annotated[AsyncSession, Depends(get_db)],
    merchant_id: UUID,
    file: UploadFile = File(...),
    current_user=Depends(require_write_user),
):

    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a CSV file.",
        )

    try:

        # Verify tenant access before importing.
        await MerchantMembershipService.verify_merchant_access(
            session,
            current_user.id,
            merchant_id,
        )

        result = await import_transactions_csv(
            session,
            merchant_id=merchant_id,
            file=file,
        )

        await session.commit()

        return {
            "message": "Transaction CSV imported successfully.",
            **result,
        }

    except Exception:
        await session.rollback()
        raise

    finally:
        await file.close()