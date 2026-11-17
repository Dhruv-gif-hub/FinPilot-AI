from typing import cast

from langchain.messages import AIMessage, HumanMessage, SystemMessage

from ...schemas.agent import InvestigationPlan
from ..llm import get_llm


async def planner_node(state, runtime) -> dict:
    llm = get_llm().with_structured_output(
        InvestigationPlan
    )
    user_id = runtime.context.user_id
    namespace_for_memory = (user_id, "memories")
    store = runtime.store

    memories = await store.asearch(namespace_for_memory, limit=10)
    if not memories:
        memories = None

    plan = cast(InvestigationPlan, await llm.ainvoke([
        SystemMessage(
            """
            You are FinPilot's investigation planner.

            Understand the user's task and decide which capabilities
            are required.

            Payment investigation can require:
            - Payment metrics
            - Period comparison
            - Internal documentation retrieval
            - External Information Search
            - AI agents
            - Relevant dates

            Do not execute tools.
            Do not invent financial results.
            """
        ),
        HumanMessage(state["request"][-1]),
    ]))

    return {"plan": plan.model_dump(),
            "user_preferance": memories,
            "messages": AIMessage(plan.model_dump_json())}