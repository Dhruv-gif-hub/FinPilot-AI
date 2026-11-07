from typing import Any

from ...db.session import Session_local
from ...services.Reconciliation.ReconciliationService import ReconciliationService


async def reconciliation_node(
    state, runtime,
) -> dict[str, Any]:

    """
    LangGraph node responsible for persisting
    discrepancies identified by the investigation agent.
    """

    context = runtime.context

    # 1. Retrieve structured investigation results.
    reconciliation_result = state.get(
        "analyst_result", None
    ).get("Reconciliation", None)

    if not reconciliation_result:
        return {
            "reconciliation_completed": False,
            "reconciliation_error": (
                "No reconciliation investigation results found."
            ),
        }

    # 2. Persist the identified discrepancies.
    async with Session_local() as session:
        result = await ReconciliationService.create_reconciliation_cases(
            session=session,
            merchant_id=context.merchant_id,
            reconciliation_data=reconciliation_result,
        )

    # 3. Update LangGraph state.
    return {
        "reconciliation_completed": True,
        "reconciliation_summary": result,
    }