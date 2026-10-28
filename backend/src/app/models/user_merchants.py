from uuid import UUID

from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..schemas.util import Role
from .merchants import Merchants
from .user import Base, User


class UserMerchants(Base):
    __tablename__ = "user_merchants"
    __table_args__ = ({"schema": "FinPilot-AI"},)

    user_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("FinPilot-AI.users.id"),
                                           primary_key=True, nullable=False)
    merchant_id: Mapped[UUID] = mapped_column(ForeignKey("FinPilot-AI.merchants.id"),
                                               primary_key=True, nullable=False)
    role: Mapped[Role] = mapped_column(String(30), 
                                       unique = False, nullable=False, default=Role.OWNER)

    user: Mapped["User"] = relationship(back_populates="user_merchants")    
    merchant: Mapped["Merchants"] = relationship(back_populates="user_merchants")