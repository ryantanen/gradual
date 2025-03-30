from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse
import requests
from dotenv import load_dotenv
load_dotenv()
import os
import motor
from jose import jwt, JWTError
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from bson import ObjectId
from .db import init_db, users, User

# CORS configuration
origins = [
    "*"
]

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await init_db()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Replace these with your own values from the Google Developer Console
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = "http://localhost:5173/token"

# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET", GOOGLE_CLIENT_SECRET)  # Fallback to Google client secret if not set
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 60 * 24  # 24 hours

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

@app.get("/login/google")
async def login_google():
    return RedirectResponse(
        f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URI}&scope=openid%20profile%20email%20https://www.googleapis.com/auth/gmail.readonly%20https://www.googleapis.com/auth/calendar.readonly&access_type=offline"
    )

@app.get("/auth/google")
async def auth_google(code: str):
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    response = requests.post(token_url, data=data)
    token_data = response.json()
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    print(token_data)
    
    user_info = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers={"Authorization": f"Bearer {access_token}"})
    user_data = user_info.json()
    
    # Check if user exists in database
    existing_user = await users.find_one({"email": user_data.get("email")})
    
    if existing_user:
        # Update existing user's tokens
        await users.update_one(
            {"email": user_data.get("email")},
            {
                "$set": {
                    "google_token": access_token
                }
            }
        )
        user_id = str(existing_user["_id"])
    else:
        # Create new user
        new_user = User(
            name=user_data.get("name"),
            email=user_data.get("email"),
            access_token=access_token,
            google_token=refresh_token
        )
        result = await users.insert_one(new_user.model_dump())
        user_id = str(result.inserted_id)
    
    # Create our own JWT token
    jwt_token = create_access_token({
        "sub": user_id,
        "email": user_data.get("email"),
        "name": user_data.get("name"),
        "picture": user_data.get("picture")
    })
    
    return {
        "user": user_data,
        "access_token": jwt_token
    }

@app.get("/token")
async def get_token(token: str = Depends(oauth2_scheme)):
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

@app.get("/me")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    user_id = payload.get("sub")
    print(user_id)
    user = await users.find_one({"_id": ObjectId(user_id)})
    if user:
        # Convert MongoDB document to dict and handle ObjectId
        user_dict = dict(user)
        user_dict["_id"] = str(user_dict["_id"])  # Convert ObjectId to string
        return user_dict
    return None

@app.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {
        "message": "You have access to this protected route",
        "user": current_user
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)