from datetime import date
from decimal import Decimal
from uuid import UUID

from langchain.tools import ToolRuntime, tool

from ...schemas.util import UserContext
from ...services.analytics.analytics_service import analytics_service
from ..helper_functions.analytics.analytics_functions import calculate_payment_metrics


@tool
async def get_payment_metrics(
        merchant_id: UUID,
        start_date: date,
        end_date: date,
        runtime: ToolRuntime[UserContext]
        ):
    
    """
    Get payment counts and rates for a merchant.

    start_date is inclusive.
    end_date is exclusive.
    """
    user_id = runtime.context.user_id

    if start_date >= end_date:
        raise ValueError("Invalid date range.")   

    counts = await analytics_service.get_payment_counts(
        merchant_id=merchant_id, user_id=user_id, start_date=start_date, end_date=end_date)

    return calculate_payment_metrics(**counts)