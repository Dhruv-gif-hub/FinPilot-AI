from json import dumps
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ...core.redis import redis_client
from ..embeddings.embeddings import query_embeddings
from .Retrieval_docs import DocumentRetrieval


class RetrievalFacade:

    @staticmethod
    async def document_retrieval(session: AsyncSession,
                                 user_id: UUID, query: str):
        query_vector = query_embeddings(query = query)
        retrieved_docs = await DocumentRetrieval.retrieval(session = session, query_vector = query_vector,
                                                          user_id = user_id)
        hybrid_retrieved_docs = await DocumentRetrieval.hybrid_retrieve(session = session, 
                                            user_id = user_id, query = query, rows = retrieved_docs)
        reranked = DocumentRetrieval.reranker_chunk(query = query, rows = hybrid_retrieved_docs)
        await redis_client.set(f"{user_id}:{query}", dumps(reranked), ex = 1800)
        return reranked

        