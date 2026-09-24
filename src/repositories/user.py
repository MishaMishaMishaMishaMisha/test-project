from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from typing import Sequence
from uuid import UUID

from src.api.v1.schemas.user import UserAddDTO
from src.models.user import UserModel
from src.core.exceptions import (UserError,
                                 UserNotFoundError,
                                 UsernameTakenError,
                                 EmailTakenError)


class UserRepository:
    
    def __init__(self, db_session: AsyncSession):    
        self.db_session = db_session
        
    async def make_commit(self):
        await self.db_session.commit()
        
    async def make_rollback(self):
        await self.db_session.rollback()
    
    async def add_user(self, 
                       user: UserAddDTO,
                       password_hash: str) -> UserModel:
        
        user_data = user.model_dump(exclude={"password"})
        user_model = UserModel(**user_data, password_hash=password_hash)
        
        try:
            self.db_session.add(user_model)
            await self.db_session.commit()
            await self.db_session.refresh(user_model)
            return user_model

        except IntegrityError as e:
            await self.db_session.rollback()

            msg = str(e.orig)

            if 'ix_users_username' in msg:
                raise UsernameTakenError

            if 'ix_users_email' in msg:
                raise EmailTakenError

            raise UserError(str(e))
    
    async def get_user_by_id(self, user_id: UUID) -> UserModel:
        
        query = select(UserModel).where(UserModel.id==user_id)
        
        res = await self.db_session.execute(query)
        user = res.scalar_one_or_none()
        
        if user is None:
            raise UserNotFoundError
        
        return user
    
    async def get_user_by_username(self, username: str) -> UserModel:
        
        query = select(UserModel).where(UserModel.username==username)
        
        res = await self.db_session.execute(query)
        user = res.scalar_one_or_none()
        
        if user is None:
            raise UserNotFoundError
        
        return user
    
    async def get_user_by_email(self, email: str) -> UserModel:
        
        query = select(UserModel).where(UserModel.email==email)
        
        res = await self.db_session.execute(query)
        user = res.scalar_one_or_none()
        
        if user is None:
            raise UserNotFoundError
        
        return user
    
    async def get_users(self, limit: int, offset: int) -> Sequence[UserModel]:
        
        query = (select(UserModel)
                 .order_by(UserModel.created_at)
                 .limit(limit)
                 .offset(offset))
        
        res = await self.db_session.execute(query)
        return res.scalars().all()
    