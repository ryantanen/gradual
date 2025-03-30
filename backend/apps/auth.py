from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from datetime import datetime, timedelta
from bson import ObjectId
import os
from .db import users, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET", os.getenv("GOOGLE_CLIENT_SECRET"))
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 60 * 24  # 24 hours

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    user_id = payload.get("sub")
    user = await users.find_one({"_id": ObjectId(user_id)})
    if user:
        # Convert MongoDB document to dict and handle ObjectId
        user_dict = dict(user)
        user_dict["_id"] = str(user_dict["_id"])  # Convert ObjectId to string
        return user_dict
    return None 