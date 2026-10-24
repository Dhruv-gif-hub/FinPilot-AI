
from uuid import UUID

from numpy import ndarray
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.document_chunks import DocumentChunk


async def retrieve_chunks(session: AsyncSession, 
                          query_vector: ndarray, user_id: UUID, top_k: int = 30,
                          score_threshold: float = 0.5):
    """
    Retrieves PDF chunks from the database that match the given query.

    Args:
        session (AsyncSession): The database session.
        query (str): The query string to search for.
    """
    similarity = DocumentChunk.embedding.cosine_distance(query_vector)
    stmt = (select(DocumentChunk, similarity.label("similarity"))
            .where(and_
                   (DocumentChunk.embedding.isnot(None),
                    DocumentChunk.user_id == user_id))
            .order_by(similarity)
            .limit(top_k))
    rows = (await session.scalars(stmt)).all()
    result =  [row for row in rows if row.similarity <= score_threshold]
    return result