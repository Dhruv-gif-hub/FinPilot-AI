from langchain.messages import HumanMessage

from ..sub_agents.research_analyst import research_analyst


async def researcher_node(state, runtime):

    findings = state.get("analyst_result", {})
    metrics = state.get("metrics", {})

    prompt = f"""
    Investigate the following financial findings using
    authorized internal documentation.

    User request:
    {state["request"][-1]}

    Metrics:
    {metrics}

    Analyst observations:
    {findings}
    
    Conversation history:
    {state["messages"]}

    Search for relevant troubleshooting guides,
    payment failure explanations, and operational policies.

    Do not assume a documented issue caused the observed
    financial changes.
    """
    
    result = await research_analyst.ainvoke(
        {
            "messages": [
                HumanMessage(prompt)
            ]
        },
        context=runtime.context,
    )

    research = result["structured_response"]
    ai_message = result["messages"][-1]   
    return {
        "research_result": research.model_dump(),
        "research_completed": True,
        "messages": [ai_message]
    }