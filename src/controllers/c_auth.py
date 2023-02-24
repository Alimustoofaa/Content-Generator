import os
import json
from dotenv import load_dotenv
load_dotenv()

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt

from src.schemas.s_auth import UserInDB, TokenData

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

user_json = {
    os.getenv('USERNAME'):{
        'username':os.getenv('USERNAME'),
        'hashed_password': os.getenv('PASSWORD')
}}

def create_access_token(data: dict):
    return jwt.encode(data, os.getenv('SECRET_KEY'), algorithm=os.getenv('ALGORITHM'))

def verify_password(plain_password, hashed_password):
	return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
	user = get_user(user_json, username)
	if not user: return False
	if not verify_password(password, user.hashed_password): return False
	return user

def get_user(db, username: str):
	if username in db:
		user_dict = db[username]
		return UserInDB(**user_dict)

async def check_authentication(token: str = Depends(oauth2_scheme)):
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"},
	)
	try:
		payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=[os.getenv('ALGORITHM')])
		username: str = payload.get("sub")
		if username is None: raise credentials_exception
		token_data = TokenData(username=username)
	except JWTError: raise credentials_exception

	user = get_user(user_json, username=token_data.username)
	if user is None: raise credentials_exception
	return user