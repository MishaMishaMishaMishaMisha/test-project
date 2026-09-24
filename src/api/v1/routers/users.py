from fastapi import (APIRouter, 
                     Depends, 
                     status, 
                     HTTPException,
                     Path, Query)
from typing import Sequence, Annotated
from uuid import UUID
from loguru import logger

from src.api.v1.dependencies.user import get_user_service
from src.api.v1.dependencies.auth import get_current_user
from src.models.user import UserModel
from src.services.user import UserService
from src.api.v1.schemas.user import UserResponseDTO
from src.core.exceptions import UserNotFoundError

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponseDTO)
async def get_me(user: UserModel = Depends(get_current_user)) -> UserResponseDTO:
    
    logger.info(f"user <{user.username}> called me")
    
    return UserResponseDTO.model_validate(user)


@router.get("/{user_id}", response_model=UserResponseDTO)
async def get_user(user_id: Annotated[UUID, Path(...)],
                   user_service: UserService = Depends(get_user_service)
                   ) -> UserResponseDTO:
    
    try:
        logger.info(f"try getting user {user_id}")
        return await user_service.get_user(user_id)
    
    except UserNotFoundError:
        logger.info(f"user not found {user_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User with such ID not found")
        
@router.get("/", response_model=Sequence[UserResponseDTO])
async def get_users(limit: Annotated[int, Query(ge=1, le=100)] = 10,
                    offset: Annotated[int, Query(ge=0)] = 0,
                    user_service: UserService = Depends(get_user_service)
                    ) -> Sequence[UserResponseDTO]:

    logger.info(f"try getting users with limit={limit}, offset={offset}")
    
    users = await user_service.get_users(limit, offset)
    
    logger.info(f"found {len(users)} users with limit={limit}, offset={offset}")
    
    return users
