from langchain.tools import ToolRuntime, tool

from ...db.session import Session_local
from ...schemas.util import UserContext
from ...services.RetrievalService.RetrievalService import RetrievalService


@tool("RAG document search", description="Perform RAG search on the internal documents.")
async def search_internal_documents(
    runtime: ToolRuntime[UserContext],
    query: str):
    
    user_id = runtime.context.user_id
    async with Session_local() as session:
        return await RetrievalService.context_retrieval(
            session=session, user_id = user_id, query=query
        )
