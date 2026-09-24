from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from loguru import logger

from src.repositories.user import UserRepository
from src.repositories.refresh_session import RefreshSessionRepository
from src.services.auth import AuthService
from src.services.user import UserService
from src.database.db_connection import get_db_session
from src.models.user import UserModel
from src.core.security import decode_token, TokenTypeEnum
from src.core.exceptions import UserNotFoundError
from src.api.v1.dependencies.user import get_user_service


def get_auth_service(
        db_session: AsyncSession = Depends(get_db_session)
        ) -> AuthService:
    
    user_repo = UserRepository(db_session)
    session_repo = RefreshSessionRepository(db_session)
    auth_service = AuthService(user_repo=user_repo,
                               session_repo=session_repo)
    
    return auth_service


# get access_token from header Authtorization: bearer <token>
oauth2_schem = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", 
                                    auto_error=False)


async def get_current_user_or_none(
        token: str = Depends(oauth2_schem),
        user_service: UserService = Depends(get_user_service)
        ) -> UserModel | None:
    
    logger.debug("getting user from access token: trying")
    
    if token is None:
        logger.debug("getting user from access token: token is missing")
        return None
    
    payload = decode_token(token)
    if (payload is None) or (payload.get("type") != TokenTypeEnum.ACCESS):
        logger.debug("getting user from access token: wrong payload")
        return None
    
    try:
        user_id = UUID(payload["sub"])
        user = await user_service.get_user(user_id)
        
        logger.debug("getting user from access token: done")
        
        return user
        
    except (ValueError, KeyError):
        logger.debug("getting user from access token: sub is missing in payload")
        return None

    except UserNotFoundError:
        logger.debug("getting user from access token: user not found")
        return None
    
    
    
async def get_current_user(
            user: UserModel | None = Depends(get_current_user_or_none)
            ) -> UserModel:
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate access token",
                            headers={"WWW-Authenticate": "Bearer"})
    
    return user
