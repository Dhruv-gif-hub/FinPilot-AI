
from collections.abc import Sequence

from sentence_transformers import CrossEncoder

from ...models.document_chunks import DocumentChunk

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def rerank(query: str, rows: Sequence[DocumentChunk], top_k: int = 10):
    candidates = rows
    if not candidates: 
        return []
    pairs = [[query, c.content] for c in candidates]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
    return [
        {"content": c.content, "rerank_score": float(s), "chunk_index": c.chunk_index}
        for c, s in ranked[:top_k]
    ]