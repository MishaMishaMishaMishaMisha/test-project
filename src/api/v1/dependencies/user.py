from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from src.repositories.user import UserRepository
from src.services.user import UserService
from src.database.db_connection import get_db_session


def get_user_service(db_session: AsyncSession = Depends(get_db_session)) -> UserService:
    
    user_repo = UserRepository(db_session)
    user_service = UserService(user_repo)
    
    return user_service
