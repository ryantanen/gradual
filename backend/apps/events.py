from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from datetime import datetime, timedelta, UTC
from .db import calendars
from .fetch_events import sync_events
from .auth import get_current_user

router = APIRouter(
    prefix="/events",
    tags=["events"]
)

@router.get("/sync")
async def sync_user_events(current_user: dict = Depends(get_current_user)):
    """Sync events from Google Calendar to our database"""
    if not current_user.get("google_token"):
        raise HTTPException(status_code=400, detail="No Google token found. Please login with Google first.")
    
    user_id = str(current_user["_id"])
    
    # Get events for the past 30 days
    start_time = datetime.now(UTC).isoformat() + "Z"
    end_time = (datetime.now(UTC) + timedelta(days=60)).isoformat() + "Z"
    try:
        count = await sync_events(current_user["google_token"], user_id, start_time, end_time)
        return {"message": f"Successfully synced {count} new events"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_user_events(
    current_user: dict = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50,
    start_date: datetime | None = None,
    end_date: datetime | None = None
):
    """Get user's events with pagination and date filtering"""
    user_id = str(current_user["_id"])
    
    # Build query
    query = {"user_id": user_id}
    if start_date and end_date:
        query["datetime_start"] = {"$gte": start_date}
        query["datetime_end"] = {"$lte": end_date}
    
    # Get total count
    total = await calendars.count_documents(query)
    
    # Get events with pagination
    cursor = calendars.find(query)
    cursor = cursor.sort("datetime_start", 1)  # Sort by start time ascending
    cursor = cursor.skip(skip).limit(limit)
    
    event_list = await cursor.to_list(None)
    
    # Convert ObjectIds to strings
    for event in event_list:
        event["_id"] = str(event["_id"])
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "events": event_list
    }

@router.get("/count")
async def count_events(current_user: dict = Depends(get_current_user)):
    """Get total count of events for the user"""
    user_id = str(current_user["_id"])
    total = await calendars.count_documents({"user_id": user_id})
    return {"total": total}

@router.get("/{event_id}")
async def get_event(
    event_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific event by ID"""
    user_id = str(current_user["_id"])
    
    event = await calendars.find_one({
        "_id": ObjectId(event_id),
        "user_id": user_id
    })
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Convert ObjectId to string before returning
    event["_id"] = str(event["_id"])
    
    return event