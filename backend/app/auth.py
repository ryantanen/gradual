from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

class Auth0Config:
    DOMAIN = os.getenv("AUTH0_DOMAIN")
    API_AUDIENCE = os.getenv("AUTH0_API_AUDIENCE")
    ALGORITHMS = ["RS256"]

class TokenPayload(BaseModel):
    sub: str
    exp: int
    scope: Optional[str] = None

security = HTTPBearer()

async def get_token_auth_header(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Obtains the Access Token from the Authorization Header"""
    if credentials.scheme != "Bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

async def requires_auth(token: str = Depends(get_token_auth_header)) -> TokenPayload:
    """Validates the JWT token and returns the payload"""
    try:
        jwks_url = f"https://{Auth0Config.DOMAIN}/.well-known/jwks.json"
        jwks_client = jwt.get_unverified_header(token)
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks_client["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=Auth0Config.ALGORITHMS
                )
                return TokenPayload(**payload)
            except JWTError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to find appropriate key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) 