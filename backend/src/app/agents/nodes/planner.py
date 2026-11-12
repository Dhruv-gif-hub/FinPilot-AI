from typing import cast

from langchain.messages import HumanMessage, SystemMessage

from ...schemas.agent import InvestigationPlan
from ..llm import get_llm


async def planner_node(state, runtime) -> dict:
    llm = get_llm().with_structured_output(
        InvestigationPlan
    )

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

    return {"plan": plan.model_dump()}