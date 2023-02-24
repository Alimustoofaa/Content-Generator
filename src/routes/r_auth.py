# from logging_datetime import logging
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import  OAuth2PasswordRequestForm

from src.schemas.s_auth import Token
from src.controllers.c_auth import authenticate_user, create_access_token

router = APIRouter()

router = APIRouter(
	prefix="/token",
	tags=["token"],
	responses={404: {"description": "Not found"}},
)

@router.post("", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        # logging.info(f'[User] Failed generate token for user {form_data.username}')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username}
    )
    # logging.info(f'[User] Success generate token for user {form_data.username}')
    return {"access_token": access_token, "token_type": "bearer"}