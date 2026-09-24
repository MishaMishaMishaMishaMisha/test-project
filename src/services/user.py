from uuid import UUID
from typing import Sequence

from src.repositories.user import UserRepository
from src.api.v1.schemas.user import UserAddDTO, UserResponseDTO
from src.core.security import hash_password


class UserService:
    
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        
    async def add_user(self, user: UserAddDTO) -> UserResponseDTO:
        
        password_hash = hash_password(user.password)
        user_db = await self.user_repo.add_user(user, password_hash)
        
        return UserResponseDTO.model_validate(user_db)
    
    async def get_user(self, user_id: UUID) -> UserResponseDTO:
        
        user_db = await self.user_repo.get_user_by_id(user_id)
        return UserResponseDTO.model_validate(user_db)
    
    async def get_users(self, limit: int, offset: int) -> Sequence[UserResponseDTO]:
        
        users_db = await self.user_repo.get_users(limit, offset)
        return [UserResponseDTO.model_validate(u) for u in users_db]
        
        
        