
from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.document_chunks import DocumentChunk


async def hybrid_retrieve_chunks(session: AsyncSession, user_id : UUID,
                                 query: str, rows: Sequence[DocumentChunk], top_k: int = 20,
                                 k = 60):
    """
    Retrieves PDF chunks from the database that match the given query.
    """
    vector_similarity =  rows #await retrieve_chunks(session, query_vector, user_id)
    row_rank = {row.id: i+1 for i, row in enumerate(vector_similarity)}
    rank = func.ts_rank_cd(DocumentChunk.search_vector, func.plain_to_tsquery("english", query))
    bm25_stmt = (select(DocumentChunk, rank.label("rank"))
                 .where(and_(DocumentChunk.user_id == user_id,
                             DocumentChunk.search_vector.match(query, postgresql_regconfig="english")
                             ))
                 .order_by(rank.desc())
                 .limit(20)
                 )
    bm25_rows = (await session.scalars(bm25_stmt)).all()
    bm25_rank = {row.id: i+1 for i, row in enumerate(bm25_rows)}
    all_ids = set(row_rank) | set(bm25_rank)
    scores = {
        cid: 1/(k + row_rank.get(cid, 1000)) + 1/(k + bm25_rank.get(cid, 1000))
        for cid in all_ids
    }
    top_ids = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:top_k]
    chunks = (await session.scalars(select(DocumentChunk).where(DocumentChunk.id.in_(top_ids)))).all()
    return chunks