from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .object_models.util import DocumentStatus
from .user import Base


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = ({"schema": "knowbase-ai"},)

    id: Mapped[UUID] = mapped_column(primary_key=True,  server_default=func.gen_random_uuid())
    user_id: Mapped[UUID] = mapped_column(ForeignKey("knowbase-ai.users.id"))
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    metadata: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[DocumentStatus] = mapped_column(String(50), nullable=False,
                                                    default=DocumentStatus.UPLOADING)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)  
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())