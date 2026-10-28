from datetime import datetime
from uuid import UUID

from sqlalchemy import CHAR, DateTime, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from .user import Base


class Merchants(Base):
    __tablename__ = "merchants"
    __table_args__ = ({"schema": "FinPilot-AI"},)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, 
                                      server_default=func.gen_random_uuid())
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    external_ref: Mapped[str] = mapped_column(String(100), nullable=False)
    currency: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 server_default=func.now())