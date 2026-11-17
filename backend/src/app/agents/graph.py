
from langgraph.graph import END, START, StateGraph
from langgraph.types import RetryPolicy, TimeoutPolicy

from .context import FinPilotContext
from .nodes.analyst import analyst_node
from .nodes.evaluator import evaluator_node
from .nodes.persist_report import persist_report_node
from .nodes.planner import planner_node
from .nodes.reconciliation import reconciliation_node
from .nodes.researcher import researcher_node
from .nodes.validate_task import validate_task_node
from .nodes.writer import writer_node
from .state import FinPilotState


def route_after_planner(state: FinPilotState) -> str:

    """
    Select the first required specialist stage.
    """

    if state.get("requires_analytics_agent", False):
        return "analyst"

    if state.get("requires_research_agent", False):
        return "researcher"
    
    return "evaluator"

def route_after_analyst(state: FinPilotState) -> str:

    """
    Continue with research or reconciliation
    after financial analytics.
    """

    if state.get("requires_research_agent", False):
        return "researcher"

    return "evaluator"

def route_after_evaluator(state: FinPilotState) -> str:

    """
    Decide whether the report can be written.

    This initial implementation stops when evaluation fails.
    A bounded repair/retry loop can be added later.
    """

    if state.get("evaluation_passed", False):
        return "writer"

    return "end"

# ==================================================
# GRAPH BUILDER
# ==================================================


def build_finpilot_graph(
    *,
    checkpointer=None, store=None
):

    """
    Build and compile the FinPilot-AI LangGraph.

        checkpointer:
            Optional LangGraph checkpointer.
    """

    builder = StateGraph(
        FinPilotState,
        context_schema=FinPilotContext,
    )

    # ----------------------------------------------
    # Register nodes
    # ----------------------------------------------

    builder.add_node(
        "validate_task",
        validate_task_node,
        retry_policy=RetryPolicy(max_attempts=3, initial_interval=1.0,
                                 backoff_factor=2.0, jitter=True, max_interval=10.0),
        timeout=TimeoutPolicy(run_timeout=120, idle_timeout=30)
    )

    builder.add_node(
        "planner",
        planner_node,
        retry_policy=RetryPolicy(max_attempts=3, initial_interval=1.0,
                                 backoff_factor=2.0, jitter=True, max_interval=10.0),
        timeout=TimeoutPolicy(run_timeout=120, idle_timeout=30)
    )

    builder.add_node(
        "analyst",
        analyst_node,
        retry_policy=RetryPolicy(max_attempts=3, initial_interval=1.0,
                                 backoff_factor=2.0, jitter=True, max_interval=10.0),
        timeout=TimeoutPolicy(run_timeout=120, idle_timeout=30)
    )

    builder.add_node(
        "researcher",
        researcher_node,
        retry_policy=RetryPolicy(max_attempts=3, initial_interval=1.0,
                                 backoff_factor=2.0, jitter=True, max_interval=10.0),
        timeout=TimeoutPolicy(run_timeout=120, idle_timeout=30)
    )


    builder.add_node(
        "reconciliation",
        reconciliation_node,
        retry_policy=RetryPolicy(max_attempts=3, initial_interval=1.0,
                                 backoff_factor=2.0, jitter=True, max_interval=10.0),
        timeout=TimeoutPolicy(run_timeout=120, idle_timeout=30)
    )

    builder.add_node(
        "evaluator",
        evaluator_node,
        retry_policy=RetryPolicy(max_attempts=3, initial_interval=1.0,
                                 backoff_factor=2.0, jitter=True, max_interval=10.0),
        timeout=TimeoutPolicy(run_timeout=120, idle_timeout=30)
    )

    builder.add_node(
        "writer",
        writer_node,
        retry_policy=RetryPolicy(max_attempts=3, initial_interval=1.0,
                                 backoff_factor=2.0, jitter=True, max_interval=10.0),
        timeout=TimeoutPolicy(run_timeout=120, idle_timeout=30)
    )

    builder.add_node(
        "persist_report",
        persist_report_node,
        retry_policy=RetryPolicy(max_attempts=3, initial_interval=1.0,
                                 backoff_factor=2.0, jitter=True, max_interval=10.0),
        timeout=TimeoutPolicy(run_timeout=120, idle_timeout=30)
    )

    # ----------------------------------------------
    # Define graph edges
    # ----------------------------------------------

    builder.add_edge(
        START,
        "validate_task",
    )

    builder.add_edge(
        "validate_task",
        "planner",
    )

    # Planner chooses the first required stage.
    builder.add_conditional_edges(
        "planner",
        route_after_planner,
        {
            "analyst": "analyst",
            "researcher": "researcher",
            "evaluator": "evaluator",
        },
    )

    # Analyst routing.
    builder.add_conditional_edges(
        "analyst",
        route_after_analyst,
        {
            "researcher": "researcher",
            "evaluator": "evaluator",
        },
    )


    # Investigation always hands structured findings
    # to the reconciliation persistence node.
    builder.add_edge(
        "investigation",
        "reconciliation",
    )

    builder.add_edge(
        "reconciliation",
        "evaluator",
    )

    # Evaluator decides whether the report is ready.
    builder.add_conditional_edges(
        "evaluator",
        route_after_evaluator,
        {
            "writer": "writer",
            "end": END,
        },
    )

    builder.add_edge(
        "writer",
        "persist_report",
    )

    builder.add_edge(
        "persist_report",
        END,
    )

    # ----------------------------------------------
    # Compile graph
    # ----------------------------------------------

    return builder.compile(
        checkpointer=checkpointer, store=store
    )