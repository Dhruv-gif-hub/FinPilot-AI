from uuid import uuid4

from langchain.messages import HumanMessage

from ..sub_agents.financial_analyst import financial_analyst


async def analyst_node(state, runtime):

    context = runtime.context
    user_id = context.user_id

    namespace_for_memory = (user_id, "memories")
    store = runtime.store

    prompt = f"""
    Analyze the following payment metrics.

    User request:
    {state["request"][-1]}

    Conversation history:
    {state["messages"]}

    Identify important observations and trends.

    Use the failure breakdown tool if you need additional
    information about payment methods or failure categories.

    Do not invent numerical values or causes.
    """

    result = await financial_analyst.ainvoke({
        "messages": [
        HumanMessage(prompt)
    ]},
        context=context,
    )

    analysis = result["structured_response"]
    ai_message = result["messages"][-1]
    user_preferance = analysis["store"]

    await store.aput(
        namespace_for_memory,
        str(uuid4()),
        user_preferance
    )


    return {
        "analyst_result": analysis.model_dump(),
        "metrics": analysis.metrics,
        "messages": [ai_message]
    }