from datetime import datetime
from uuid import UUID

from pgvector.sqlalchemy import VECTOR
from sqlalchemy import BigInteger, Computed, ForeignKey, Index, Text, func
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column

from .user import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[UUID] = mapped_column(primary_key=True,  server_default=func.gen_random_uuid())
    documents_id: Mapped[UUID] = mapped_column(ForeignKey("knowbase-ai.documents.id"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("knowbase-ai.users.id"))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(BigInteger, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(VECTOR(1536), nullable=False)
    search_vector: Mapped[str] = mapped_column(
        TSVECTOR, 
        Computed("to_tsvector('english', content)", persisted=True),
        index=False
        )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    __table_args__ = (
            Index(
            "idx_documents_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
            Index(
            "idx_documents_search_vector",
            "search_vector",
            postgresql_using="gin"
        ),
            {"schema": "knowbase-ai"},
        )
