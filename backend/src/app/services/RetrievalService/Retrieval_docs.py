from collections.abc import Sequence
from uuid import UUID

from numpy import ndarray
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.document_chunks import DocumentChunk
from ..retrieval.hybrid import hybrid_retrieve_chunks
from ..retrieval.reranker import rerank
from ..retrieval.retriever import retrieve_chunks


class DocumentRetrieval:

    @staticmethod
    async def retrieval(session: AsyncSession, query_vector: ndarray, user_id: UUID):
        return await retrieve_chunks(session = session, query_vector = query_vector,
                               user_id = user_id)

    @staticmethod
    async def hybrid_retrieve(session: AsyncSession, user_id : UUID, query: str,
                              rows: list[DocumentChunk]):
        return await hybrid_retrieve_chunks(session = session, user_id = user_id, 
                                      query = query, rows = rows)

    @staticmethod
    def reranker_chunk(query: str, rows: Sequence[DocumentChunk]):
        return rerank(query = query, rows = rows)