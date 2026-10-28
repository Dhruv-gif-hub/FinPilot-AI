from datetime import datetime
from uuid import UUID

from langchain.tools import ToolRuntime, tool

from ...schemas.util import UserContext
from ..helper_functions.financial_operations.reconciliation_discrepancies import (
   reconciliation_discrepancies,
)


@tool
async def find_reconciliation_discrepancies(
    merchant_id: UUID,
    runtime: ToolRuntime[UserContext],
    start_date: datetime,
    end_date: datetime,
) -> dict:
    user_id = runtime.context.user_id

    return await reconciliation_discrepancies(merchant_id=merchant_id,
                            user_id=user_id, start_date=start_date, end_date=end_date)