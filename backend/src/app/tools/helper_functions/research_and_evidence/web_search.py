import asyncio
from typing import Literal
from urllib.parse import urlparse

from tavily import AsyncTavilyClient

from ....core.config import config_value

tavily_client = AsyncTavilyClient(
    api_key=config_value.tavily_api_key,
)


SearchTopic = Literal["general", "news", "finance"]
TimeRange = Literal["day", "week", "month", "year"]

async def web_service(
    query: str,
    max_results: int = 5,
    topic: SearchTopic = "general",
    time_range: TimeRange | None = None,
) -> dict:
    """Search the web and return normalized, source-backed results."""

    query = query.strip()

    if not query:
        raise ValueError("Search query cannot be empty.")

    max_results = max(1, min(max_results, 5))
    kwargs: dict = {}
    if time_range is not None:
        kwargs["time_range"] = time_range

    try:
        response = await asyncio.wait_for(
            tavily_client.search(
                query=query,
                search_depth="basic",
                topic=topic,
                max_results=max_results,
                include_answer=False,
                include_raw_content=False,
                timeout=10,
                **kwargs
            ),
            timeout=12,
        )

    except (TimeoutError, asyncio.TimeoutError):
        return {
            "query": query,
            "results": [],
            "error": "Web search timed out. Try again later.",
        }

    except Exception:
        # Log the actual exception internally in production.
        # Do not expose credentials or provider error details to the agent.
        return {
            "query": query,
            "results": [],
            "error": "The web search provider is temporarily unavailable.",
        }

    normalized_results = []

    for item in response.get("results", []):
        url = item.get("url", "")
        parsed_url = urlparse(url)

        # Accept only absolute HTTP(S) URLs returned by the provider.
        if (
            parsed_url.scheme not in {"http", "https"}
            or not parsed_url.netloc
        ):
            continue

        normalized_results.append(
            {
                "title": item.get("title") or "Untitled",
                "url": url,
                "snippet": item.get("content") or "",
                "published_date": item.get("published_date"),
                "score": item.get("score"),
            }
        )

    return {
        "query": query,
        "result_count": len(normalized_results),
        "results": normalized_results,
    }