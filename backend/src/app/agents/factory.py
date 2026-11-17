from .graph import build_finpilot_graph
from .llm import get_llm


def create_finpilot_graph(checkpointer=None, store=None):
    """
    Create and return a FinPilot-AI LangGraph instance.

        checkpointer:
            Optional LangGraph checkpointer.
    """

    model = get_llm()
    graph = build_finpilot_graph(checkpointer=checkpointer, store=store)
    return graph
