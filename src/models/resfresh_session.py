from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import text, ForeignKey, DateTime
from sqlalchemy import UUID as sqlalchemy_uuid
from uuid import UUID as python_uuid
from datetime import datetime

from src.models.base import BaseModel


class RefreshSessionModel(BaseModel):
    
    __tablename__ = "refresh_sessions"
    
    id: Mapped[python_uuid] = mapped_column(sqlalchemy_uuid(as_uuid=True),
                                            primary_key=True,
                                            server_default=text("gen_random_uuid()"))
    
    user_id: Mapped[python_uuid] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    
    token_hash: Mapped[str] = mapped_column(index=True)
    
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    
    is_revoked: Mapped[bool] = mapped_column(default=False,
                                             server_default=text("false"))
    
    
    