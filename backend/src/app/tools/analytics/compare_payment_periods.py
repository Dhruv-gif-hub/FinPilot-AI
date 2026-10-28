from datetime import date
from uuid import UUID

from langchain.tools import ToolRuntime, tool

from ...schemas.util import UserContext
from ...services.analytics.analytics_service import analytics_service
from ..helper_functions.analytics.analytics_functions import calculate_payment_metrics
from ..helper_functions.analytics.compare_metrics import compare_rates


@tool
async def compare_payment_periods(
    merchant_id: UUID,
    start_date: date,
    end_date: date,
    compare_period_start_date: date,
    compare_period_end_date: date,
    runtime: ToolRuntime[UserContext]
):
    """
    Compare the payments rates of two time periods
    for a merchant.
    """
    user_id = runtime.context.user_id

    if start_date >= end_date or compare_period_start_date >= compare_period_end_date:
        raise ValueError("Invalid date range.") 

    counts = await analytics_service.get_payment_counts(
        merchant_id=merchant_id, user_id=user_id, start_date=start_date, end_date=end_date)
    metrics = calculate_payment_metrics(**counts)

    compare_counts = await analytics_service.get_payment_counts(
        merchant_id=merchant_id, user_id=user_id, start_date=compare_period_start_date,
          end_date=compare_period_end_date)
    compare_metrics = calculate_payment_metrics(**compare_counts)

    return compare_rates(previous_rate = metrics["failure_rate_pct"],
                           current_rate = compare_metrics["failure_rate_pct"])
