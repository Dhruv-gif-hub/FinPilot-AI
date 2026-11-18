import operator
from datetime import datetime
from typing import Annotated, Any, TypedDict

from langgraph.graph.message import AnyMessage, add_messages


class FinPilotState(TypedDict, total=False):
    # Request and trusted execution context
    task_id: str
    thread_id: str
    run_id: str
    user_id: str
    task_type: str
    merchant_id: str
    user_preferance: list[dict]
    request: Annotated[list[str], operator.add]
    
    previous_start: datetime
    previous_end: datetime
    current_start: datetime
    current_end: datetime


    # Planning and specialist results
    plan: dict[str, Any]
    metrics: dict[str, Any]
    comparison: dict[str, Any]
    analyst_result: dict[str, Any]
    evidence: list[dict[str, Any]]
    researcher_result: dict[str, Any]
    research_completed: bool

    # Evaluation and recovery
    validation_issues: list[str]
    retry_count: int
    evaluation_passed: bool

    # Final output
    final_report: dict[str, Any]
    reconciliation_completed: bool
    reconciliation_summary: dict[str, Any]
    messages: Annotated[list[AnyMessage], add_messages]
    report_id: str