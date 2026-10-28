from datetime import datetime
from uuid import UUID

from pydantic import EmailStr
from sqlalchemy import Boolean, DateTime, MetaData, String, Uuid, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )

class User(Base):

    __tablename__ = "users"
    __table_args__ = ({"schema": "FinPilot-AI"},)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True,  server_default=func.gen_random_uuid())
    email: Mapped[EmailStr] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 server_default=func.now(), onupdate=func.now())
    
    def to_dict(self) -> dict:
            return {"id": self.id, "email": self.email, 
                    "password": self.password, "created_at": self.created_at}