from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
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
from .db import init_db, users, nodes, branches, User, Node, Branch
from .email import router as email_router, sync_emails
from .pdf import router as pdf_router
from .scheduler import sync_user_data
from .auth import get_current_user, create_access_token, oauth2_scheme
from .events import router as events_router
from .ai import generate_nodes
import logging

# Configure logging
logger = logging.getLogger(__name__)

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

# Include routers
app.include_router(email_router)
app.include_router(pdf_router)
app.include_router(events_router)

# Replace these with your own values from the Google Developer Console
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = "http://localhost:5173/token"

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
                    "google_token": access_token,
                    "google_data": user_data
                }
            }
        )
        user_id = str(existing_user["_id"])
    else:
        # Create new user
        new_user = User(
            name=user_data.get("name"),
            email=user_data.get("email"),
            google_data=user_data,
            google_token=access_token
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
    return jwt.decode(token, os.getenv("JWT_SECRET", GOOGLE_CLIENT_SECRET), algorithms=["HS256"])

@app.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user

@app.get("/begin-ai")
async def start(background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    """Start a sync process for the current user"""
    if not current_user.get("google_token"):
        raise HTTPException(status_code=400, detail="No Google token found. Please login with Google first.")
    
    # Add sync task to background tasks
    background_tasks.add_task(sync_user_data, current_user["_id"], current_user["google_token"])
    
    return {
        "message": "Sync process started",
        "status": "processing"
    }

@app.get("/generate-ai-nodes")
async def generate_ai_nodes(current_user: dict = Depends(get_current_user)):
    """Generate a list of nodes using AI based on user's data"""
    try:
        result = await generate_nodes(current_user)
        return result
    except Exception as e:
        logger.error(f"Error generating AI nodes: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating AI nodes: {str(e)}")

@app.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {
        "message": "You have access to this protected route",
        "user": current_user
    }

@app.get("/nodes")
async def get_nodes(current_user: dict = Depends(get_current_user)):
    # Get all branches for the user
    
    # Get all nodes for the user
    nodes_list = current_user.get("nodes_tmp", [])
    return str(nodes_list)

@app.get("/node/{node_id}")
async def get_node(node_id: str, current_user: dict = Depends(get_current_user)):
    return await nodes.find_one({"_id": ObjectId(node_id), "user_id": current_user["_id"]})

@app.post("/add-node")
async def add_node(node_data: dict, current_user: dict = Depends(get_current_user)):
    # Find the main branch using case-insensitive regex
    main_branch = await branches.find_one({
        "name": {"$regex": "main", "$options": "i"},
        "user_id": current_user["_id"]
    })
    
    if not main_branch:
        raise HTTPException(status_code=404, detail="Main branch not found")
    
    # Create the node
    node = {
        "description": node_data.get("description"),
        "time": datetime.now(),
        "branch": str(main_branch["_id"]),  # Convert ObjectId to string
        "user_id": str(current_user["_id"]),  # Convert ObjectId to string
        "parents": [],
        "children": [],
        "sources": []
    }
    result = await nodes.insert_one(node)
    created_node = await nodes.find_one({"_id": result.inserted_id})
    created_node["_id"] = str(created_node["_id"])    
    return created_node

@app.get("/users")
async def get_users():
    users_list = await users.find().to_list(None)
    for user in users_list:
        user["_id"] = str(user["_id"])
    return users_list

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)