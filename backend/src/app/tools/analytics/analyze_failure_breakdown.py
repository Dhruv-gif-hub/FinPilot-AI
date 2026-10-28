from datetime import datetime
from uuid import UUID

from langchain.tools import ToolRuntime, tool

from ...schemas.util import UserContext
from ..helper_functions.analytics.analyze_failure_breakdown import failure_breakdown


@tool
async def analyze_failure_breakdown(
    merchant_id: UUID,
    previous_start: datetime,
    previous_end: datetime,
    current_start: datetime,
    current_end: datetime,
    runtime: ToolRuntime[UserContext]
) -> dict:
    user_id = runtime.context.user_id

    return await failure_breakdown(merchant_id=merchant_id, user_id=user_id,
                                   previous_start=previous_start,
                                   previous_end=previous_end, current_start=current_start,
                                   current_end=current_end)