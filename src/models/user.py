from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import text, DateTime
from sqlalchemy import UUID as sqlalchemy_uuid
from uuid import UUID as python_uuid
from datetime import datetime

from src.models.base import BaseModel


class UserModel(BaseModel):
    
    __tablename__ = "users"
    
    id: Mapped[python_uuid] = mapped_column(sqlalchemy_uuid(as_uuid=True),
                                            primary_key=True,
                                            server_default=text("gen_random_uuid()"))
    
    username: Mapped[str] = mapped_column(unique=True, index=True)
    
    email: Mapped[str] = mapped_column(unique=True, index=True)
    
    password_hash: Mapped[str]
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 server_default=text("now()"))
    
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 server_default=text("now()"),
                                                 server_onupdate=text("now()"))
    
    