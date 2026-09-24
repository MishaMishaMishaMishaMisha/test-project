# from passlib.context import CryptContext

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def hash_password(password: str) -> str:
#     return pwd_context.hash(password)
# def verify_password(password: str, hashed_password: str) -> bool:
#     return pwd_context.verify(password, hashed_password)



import jwt
import bcrypt
from hashlib import sha256
from uuid import UUID, uuid4
from datetime import datetime, timedelta, timezone
from enum import Enum
from loguru import logger
from pydantic import ValidationError

from src.core.config import settings


class TokenTypeEnum(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    

def hash_password(password: str) -> str:
    
    return bcrypt.hashpw(password.encode("utf-8"), 
                         bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed: str) -> bool:
    
    return bcrypt.checkpw(plain_password.encode("utf-8"),
                          hashed.encode("utf-8"))


def create_jwt(data: dict, expire_timedelta: timedelta) -> str:
    
    data_to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expire_timedelta
    data_to_encode.update({"exp": expire})
    
    return jwt.encode(data_to_encode, 
                      settings.jwt.SECRET_KEY, 
                      algorithm=settings.jwt.ALGORITHM)

def create_access_token(user_id: UUID) -> str:
    
    logger.info(f"user {user_id} creating access token")
    
    payload = {"sub": str(user_id), "type": TokenTypeEnum.ACCESS}
    return create_jwt(payload, 
                      timedelta(minutes=settings.jwt.ACCESS_TOKEN_EXPIRE_MINUTES))

def create_refresh_token(user_id: UUID) -> tuple[str, datetime]:
    
    logger.info(f"user {user_id} creating refresh token")
    
    payload = {"sub": str(user_id), "type": TokenTypeEnum.REFRESH}
    time = timedelta(days=settings.jwt.REFRESH_TOKEN_EXPIRE_DAYS)
    
    token = create_jwt(payload, time)
    expires_at = datetime.now(timezone.utc) + time
    
    return (token, expires_at)

def decode_token(token: str) -> dict | None:
    
    try:
        logger.info("try decoding token")
        
        payload = jwt.decode(token, 
                             settings.jwt.SECRET_KEY, 
                             algorithms=settings.jwt.ALGORITHM)
        return payload
    
    except jwt.PyJWTError:
        logger.info("token has expired")

    except ValidationError:
        logger.error(f"validation error while decoding token {token}")

def hash_token(token: str) -> str:
        return sha256(token.encode()).hexdigest()

if __name__ == "__main__":
    
    token1 = create_jwt({"data": "qwfefvfv"}, timedelta(minutes=10))
    h1 = hash_token(token1)
    h2 = hash_token(token1)
    print("qe", h1)
    print(h1 == h2)