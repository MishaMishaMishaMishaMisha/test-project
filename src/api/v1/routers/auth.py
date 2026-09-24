from fastapi import (APIRouter, 
                     Depends, 
                     status, 
                     Request,
                     Response, 
                     HTTPException)
from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger

from src.api.v1.dependencies.user import get_user_service
from src.api.v1.dependencies.auth import get_auth_service
from src.services.user import UserService
from src.services.auth import AuthService
from src.api.v1.schemas.user import UserAddDTO, UserResponseDTO
from src.core.exceptions import (UserError,
                                 UsernameTakenError,
                                 EmailTakenError,
                                 InvalidCredentialsError,
                                 InvalidTokenError)


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponseDTO)
async def register_user(response: Response,
                        new_user: UserAddDTO,
                        user_service: UserService = Depends(get_user_service)
                        ) -> UserResponseDTO:
    
    try:
        logger.info(f"try to add new user <{new_user.username}, {new_user.email}>")
        
        user = await user_service.add_user(new_user)
        
        logger.info(f"new user added <{new_user.username}, {new_user.email}>")
        
        response.status_code = status.HTTP_201_CREATED    
        
        return user
    
    except UsernameTakenError:
        logger.info(f"user try to register with existing username <{new_user.username}>")
        
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Such username already taken")
        
    except EmailTakenError:
        logger.info(f"user try to register with existing email <{new_user.email}>")
        
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Such email already taken")
                
    except UserError as e:
        logger.error(f"Cant add new user. Error: {str(e)}")
        
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Server cant create new user, please wait")
    
    
@router.post("/login")
async def login(response: Response,
                form_data: OAuth2PasswordRequestForm = Depends(),
                auth_service: AuthService = Depends(get_auth_service)):

    try:
        
        logger.info(f"user <{form_data.username}> try to login")
        
        # login and save refresh token in db if login is valid
        access_token, refresh_token = await auth_service.authenticate_user(
                                                login=form_data.username,
                                                password=form_data.password)
        
        # send refresh token in cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,  # protect from XSS attack
            secure=True,    # use only HTTPS
            samesite="lax")  # protect from CSRF attack
        
        # send access token in body response
        return {"access_token": access_token, "token_type": "bearer"}
    
    except InvalidCredentialsError as e:
        
        logger.info(f"user <{form_data.username}> input wrong login or password")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail=str(e))

@router.post("/logout")
async def logout(request: Request,
                 response: Response,
                 auth_service: AuthService = Depends(get_auth_service)):
    
    logger.info("user try logout")
    
    # get token from cookie
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        return {"message": "Refresh token not found"}
    
    # delete token from db
    await auth_service.logout(refresh_token)
    
    # delete token from cookie
    response.delete_cookie(key="refresh_token")
    
    return {"message": "Logged out successfully"}

@router.post("/refresh")
async def refresh(request: Request,
                  response: Response,
                  auth_service: AuthService = Depends(get_auth_service)):
    
    logger.info("user try to refresh tokens")

    # get token from cookie
    refresh_token = request.cookies.get("refresh_token")
    
    if refresh_token is None:
        logger.info("user try to refresh tokens: refresh token is missing")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Refresh token is missing")
        
    try:

        # check old token and create new tokens
        new_access_token, new_refresh_token = await auth_service.update_tokens(refresh_token)
        
        logger.info("user refreshed tokens successfully")
        
        # send new refresh token in cookie
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=True,
            samesite="lax") 
        
        # send new access token in body response
        return {"access_token": new_access_token, "token_type": "bearer"}
    
    except InvalidTokenError:
        logger.info("user try to refresh tokens: refresh token has expired")
        pass
