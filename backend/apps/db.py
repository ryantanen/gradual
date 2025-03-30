from motor import motor_asyncio
import os
from typing import Annotated
from pydantic import BeforeValidator
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
db = client.get_database("production")
PyObjectId = Annotated[str, BeforeValidator(str)]

# Collections
emails = db.get_collection("emails")
pdfs = db.get_collection("pdfs")
photos = db.get_collection("photos")
calendars = db.get_collection("calendars") 
contacts = db.get_collection("contacts")
users = db.get_collection("users")
branches = db.get_collection("branches")
nodes = db.get_collection("nodes")

# Models
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

class BaseMongoModel(BaseModel):
    _id: str

class Email(BaseMongoModel):
    sender: str
    subject: Optional[str] = None
    datetime: datetime
    content: Optional[str] = None
    url: Optional[str] = None
    is_starred: bool = False
    user_id: str
    content_hash: Optional[str] = None  # Hash of email content to prevent duplicates

class PDF(BaseMongoModel):
    filename: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    user_id: str

class Photo(BaseMongoModel):
    datetime: datetime
    description: Optional[str] = None
    location: Optional[str] = None
    user_id: str

class Calendar(BaseMongoModel):
    datetime_start: datetime
    datetime_end: datetime
    event_name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    collaborators: List[str] = []
    user_id: str

class Contact(BaseMongoModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    user_id: str

class GoogleData(BaseModel):
    sub: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    picture: Optional[str] = None
    email_verified: Optional[bool] = None
    locale: Optional[str] = None

class User(BaseModel):
    name: str
    email: str
    google_data: Optional[Dict[str, Any]] = None
    google_token: Optional[str] = None

class Branch(BaseMongoModel):
    name: str
    user_id: str

class Source(BaseMongoModel):
    kind: str
    item: str

class Node(BaseMongoModel):
    parents: List[str] = []
    children: List[str] = []
    user_id: str
    sources: List[Source] = []
    image_url: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    branch: str
    occurred_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    root: Optional[bool] = False

async def init_db():
    """Initialize database collections and indexes"""
    # Create indexes for users collection
    await users.create_index("email", unique=True)
    
    # Create indexes for emails collection
    await emails.create_index("content_hash")
    await emails.create_index("user_id")
    await emails.create_index("datetime")

async def drop_all_collections():
    """Drop all collections except users for development purposes"""
    collections_to_drop = [
        emails,
        pdfs,
        photos,
        calendars,
        contacts,
        branches,
        nodes
    ]
    
    for collection in collections_to_drop:
        await collection.drop()

