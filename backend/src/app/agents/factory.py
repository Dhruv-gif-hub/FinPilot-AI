from .llm import get_llm
from .graph import build_finpilot_graph

def create_finpilot_graph(checkpointer=None):
    """
    Create and return a FinPilot-AI LangGraph instance.

        checkpointer:
            Optional LangGraph checkpointer.
    """

    model = get_llm()
    graph = build_finpilot_graph(checkpointer=checkpointer)
    return graph
