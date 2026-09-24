from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, EmailStr


class UserBaseDTO(BaseModel):
    
    username: str = Field(min_length=8, max_length=25)
    email: EmailStr


class UserAddDTO(UserBaseDTO):
    
    password: str = Field(min_length=8, max_length=30)
    
    
class UserResponseDTO(UserBaseDTO):
    
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True