from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .auth import requires_auth, TokenPayload
import requests
import os

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the API"}

@app.get("/callback")
async def auth_callback(code: str, state: str):
    try:
        # Exchange the authorization code for an access token
        token_url = f"https://{os.getenv('AUTH0_DOMAIN')}/oauth/token"
        client_id = os.getenv('AUTH0_CLIENT_ID')
        client_secret = os.getenv('AUTH0_CLIENT_SECRET')
        redirect_uri = "http://localhost:8000/callback"

        token_payload = {
            "grant_type": "authorization_code",
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "redirect_uri": redirect_uri
        }

        token_response = requests.post(token_url, json=token_payload)
        token_response.raise_for_status()
        token_data = token_response.json()

        return {
            "access_token": token_data.get("access_token"),
            "token_type": token_data.get("token_type"),
            "expires_in": token_data.get("expires_in")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/protected")
async def read_protected(user: TokenPayload = Depends(requires_auth)):
    print("test")
    return {
        "message": "This is a protected endpoint",
        "user_id": user.sub,
        "scopes": user.scope
    }

@app.get("/public")
async def read_public():
    return {"message": "This is a public endpoint"}