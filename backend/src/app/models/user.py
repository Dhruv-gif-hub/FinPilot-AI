from datetime import datetime
from uuid import UUID

from pydantic import EmailStr
from sqlalchemy import String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass 

class User(Base):

    __tablename__ = "users"
    __table_args__ = ({"schema": "knowbase-ai"},)

    id: Mapped[UUID] = mapped_column(primary_key=True,  server_default=func.gen_random_uuid())
    email: Mapped[EmailStr] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    role: Mapped[str] = mapped_column(String(20), unique = False, nullable=False, default="user")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    
    def to_dict(self) -> dict:
            return {"id": self.id, "email": self.email, 
                    "password": self.password, "created_at": self.created_at}