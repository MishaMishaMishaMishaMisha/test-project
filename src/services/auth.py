from uuid import UUID

from src.repositories.user import UserRepository
from src.repositories.refresh_session import RefreshSessionRepository
from src.core.security import (verify_password, 
                               create_access_token, 
                               create_refresh_token,
                               decode_token,
                               TokenTypeEnum)
from src.core.exceptions import (UserNotFoundError,
                                 InvalidCredentialsError,
                                 InvalidTokenError)


class AuthService:
    
    def __init__(self, 
                 user_repo: UserRepository, 
                 session_repo: RefreshSessionRepository):
        
        self.user_repo = user_repo
        self.session_repo = session_repo
        
    async def authenticate_user(self, login: str, password: str) -> tuple[str, str]:
        
        # try to find user by login
        try:
            if "@" in login:
                user = await self.user_repo.get_user_by_email(login)
            else:
                user = await self.user_repo.get_user_by_username(login)
        except UserNotFoundError:
            raise InvalidCredentialsError("wrong login")
        
        # check password
        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("wrong password")
        
        # create tokens
        access_token = create_access_token(user.id)
        refresh_token, expires_at = create_refresh_token(user.id)
        
        # save refresh token in db
        await self.session_repo.create_session(user_id=user.id,
                                               token=refresh_token,
                                               expires_at=expires_at)
        
        return (access_token, refresh_token)
    
    async def update_tokens(self, refresh_token: str) -> tuple[str, str]:
        
        # decode token
        payload = decode_token(refresh_token)
        if (payload is None) or (payload.get("type") != TokenTypeEnum.REFRESH):
            raise InvalidTokenError("invalid or expired token")
        
        # check old session in db
        session = await self.session_repo.get_active_session(refresh_token)
        if not session:
            raise InvalidTokenError("session is expired or already revoked")

        # disable old session
        await self.session_repo.revoke_session(refresh_token)
        
        # find user by this token
        try:
            user_id = UUID(payload["sub"])
            user = await self.user_repo.get_user_by_id(user_id)
            
        except (ValueError, KeyError):
            raise InvalidTokenError("Incorrect token payload")
        except UserNotFoundError:
            raise InvalidTokenError("User not found by id in token")
        
        # create new tokens
        new_access_token = create_access_token(user.id)
        new_refresh_token, expires_at = create_refresh_token(user.id)
        
        # add new refresh_token to db
        await self.session_repo.create_session(user_id=user_id,
                                               token=new_refresh_token,
                                               expires_at=expires_at)
        
        return (new_access_token, new_refresh_token)
    
    async def logout(self, refresh_token: str) -> None:
        await self.session_repo.revoke_session(refresh_token)

