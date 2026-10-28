from langchain.tools import tool

from ..helper_functions.research_and_evidence.web_search import (
    SearchTopic,
    TimeRange,
    web_service,
)


@tool
async def search_web_service(
    query: str,
    max_results: int = 5,
    topic: SearchTopic = "general",
    time_range: TimeRange | None = None,
) -> dict:
    """Search the web and return normalized, source-backed results."""

    return await web_service(
        query=query, max_results=max_results, topic=topic, time_range=time_range
    )