from typing import cast

from langchain.messages import AIMessage, HumanMessage, SystemMessage

from ...schemas.agent import ReportDraft
from ..llm import get_llm


async def writer_node(state):

    writer = get_llm().with_structured_output(
        ReportDraft
    )

    report = cast(ReportDraft, await writer.ainvoke([
        SystemMessage(
            """
            You are FinPilot's financial report writer.

            Use only the supplied metrics and research evidence.

            Requirements:
            - Explain the financial observations.
            - Include supporting evidence references.
            - Distinguish facts from hypotheses.
            - Include limitations.
            - Never invent numerical results.
            - Do not claim causation without evidence.
            """
        ),
        HumanMessage(
            str({
                "request": state["request"],
                "messages": state["messages"],
                "metrics": state.get("metrics"),
                "analyst_findings": state.get(
                    "analyst_result"
                ),
                "research": state.get("researcher_result"),
                "validation_issues": state.get(
                    "validation_issues"
                ),
            })
        ),
    ]))

    return {
        "final_report": report.model_dump(),
        "messages": AIMessage(report.model_dump_json())
    }