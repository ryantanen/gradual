from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2AuthorizationCodeBearer
from auth import verify_token

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Your React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def get_root():
    return {"message": "Welcome to Gradual"}

@app.get("/protected")
async def get_protected(payload: dict = Depends(verify_token)):
    return {"message": "This is a protected endpoint", "user": payload["sub"]}

@app.get("/callback")
async def get_callback():
    return {"Hello"}