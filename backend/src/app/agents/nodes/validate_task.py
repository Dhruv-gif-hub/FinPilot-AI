
from langchain.messages import HumanMessage

from ...db.session import Session_local
from ...services.analytics.analytics_service import analytics_service


async def validate_task_node(state, runtime):
    context = runtime.context

    async with Session_local() as session:
        await analytics_service.merchant_access(
            session=session,
            user_id=context.user_id,
            merchant_id=context.merchant_id,
        )

    if not state.get("request"):
        raise ValueError("Task request is missing.")

    if not state.get("task_id"):
        raise ValueError("Task ID is missing.")

    return {
        "status": "validated",
        "validation_issues": [],
        "messages": [HumanMessage(state["request"][-1])]
    }