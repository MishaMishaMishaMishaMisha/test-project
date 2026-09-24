from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.resfresh_session import RefreshSessionModel
from src.core.security import hash_token


class RefreshSessionRepository:
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_session(self, 
                             user_id: UUID, 
                             token: str, 
                             expires_at: datetime) -> RefreshSessionModel:
        
        session = RefreshSessionModel(user_id=user_id,
                                      token_hash=hash_token(token),
                                      expires_at=expires_at,
                                      is_revoked=False)
        
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get_active_session(self, token: str) -> RefreshSessionModel | None:
        
        token_hash = hash_token(token)
        
        query = select(RefreshSessionModel).where(
            RefreshSessionModel.token_hash == token_hash,
            RefreshSessionModel.is_revoked == False,
            RefreshSessionModel.expires_at > datetime.now(timezone.utc))
        
        result = await self.db.execute(query)
        
        return result.scalar_one_or_none()

    # logout user from his session
    async def revoke_session(self, token: str) -> None:
        
        token_hash = hash_token(token)

        # delete session
        query = (delete(RefreshSessionModel)
                 .where(RefreshSessionModel.token_hash == token_hash))        
        # or set is_revoked=True
        # query = (update(RefreshSessionModel)
        #          .where(RefreshSessionModel.token_hash == token_hash)
        #          .values(is_revoked=True))
        
        await self.db.execute(query)
        await self.db.commit()

        
