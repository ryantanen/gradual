from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from .db import emails
from .fetch_emails import sync_emails
from .auth import get_current_user

router = APIRouter(
    prefix="/emails",
    tags=["emails"]
)

@router.get("/sync")
async def sync_user_emails(current_user: dict = Depends(get_current_user)):
    """Sync emails from Gmail to our database"""
    if not current_user.get("google_token"):
        raise HTTPException(status_code=400, detail="No Google token found. Please login with Google first.")
    
    user_id = current_user["_id"]
    number_of_emails = 100  # You can make this configurable via query parameter
    
    try:
        count = await sync_emails(current_user["google_token"], user_id, number_of_emails)
        return {"message": f"Successfully synced {count} new emails"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_user_emails(
    current_user: dict,
    skip: int = 0,
    limit: int = 50,
    starred_only: bool = False
):
    """Get user's emails with pagination and filtering"""
    user_id = str(current_user["_id"])
    
    # Build query
    query = {"user_id": user_id}
    if starred_only:
        query["is_starred"] = True
    
    # Get total count
    total = await emails.count_documents(query)
    
    # Get emails with pagination
    cursor = emails.find(query)
    cursor = cursor.sort("datetime", -1)  # Sort by date descending
    cursor = cursor.skip(skip).limit(limit)
    
    email_list = await cursor.to_list(None)
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "emails": email_list
    }

@router.get("/{email_id}")
async def get_email(
    email_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific email by ID"""
    user_id = current_user["_id"]
    
    email = await emails.find_one({
        "_id": ObjectId(email_id),
        "user_id": user_id
    })
    
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    return email 