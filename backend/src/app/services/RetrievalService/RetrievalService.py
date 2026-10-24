from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from .RetrievalFacade import RetrievalFacade


class RetrievalService:

    @staticmethod
    async def context_retrieval(session: AsyncSession, user_id : UUID, query: str):
        return await RetrievalFacade.document_retrieval(session = session, user_id = user_id,
                                                  query = query)