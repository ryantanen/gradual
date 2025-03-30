import requests
import json
import urllib
from datetime import datetime
from typing import List, Dict, Any
from .db import calendars, Calendar

async def get_events_between(access_token: str, user_id: str, startTS: str, endTS: str) -> List[Dict[str, Any]]:
    """Gets events from all calendars between startTS and endTS"""
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    try:
        response = requests.get(
            "https://www.googleapis.com/calendar/v3/users/me/calendarList",
            headers=headers
        ).json()

        if 'items' not in response:
            print("No calendars fetched")
            return []

        events = []
        for calendar in response['items']:
            encoded_id = urllib.parse.quote(calendar['id'], safe='')
            calendar_data = requests.get(
                f"https://www.googleapis.com/calendar/v3/calendars/{encoded_id}/events?timeMin={startTS}&timeMax={endTS}",
                headers=headers
            ).json()

            if 'items' not in calendar_data:
                continue

            for event in calendar_data['items']:
                # Parse start and end times
                start = event.get('start', {}).get('dateTime') or event.get('start', {}).get('date')
                end = event.get('end', {}).get('dateTime') or event.get('end', {}).get('date')
                
                try:
                    start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    print(f"⚠️ Could not parse dates for event {event.get('id')}")
                    continue

                event_data = Calendar(
                    datetime_start=start_dt,
                    datetime_end=end_dt,
                    event_name=event.get('summary', "No event name"),
                    location=event.get('location', "No location"),
                    description=event.get('description', "No description"),
                    collaborators=[attendee.get('email', "No email") for attendee in event.get('attendees', [])] if 'attendees' in event else [],
                    user_id=user_id
                )
                events.append(event_data.model_dump())

        return events

    except Exception as e:
        print(f"Error fetching events: {e}")
        return []

async def sync_events(access_token: str, user_id: str, startTS: str, endTS: str):
    """Sync events from Google Calendar to MongoDB"""
    # Get existing event IDs for this user
    existing_events = await calendars.find({"user_id": user_id}).to_list(None)
    existing_ids = {event.get("_id") for event in existing_events}
    
    # Fetch new events
    new_events = await get_events_between(access_token, user_id, startTS, endTS)
    
    # Filter out events we already have
    events_to_insert = [
        event for event in new_events 
        if event.get("_id") not in existing_ids
    ]
    
    if events_to_insert:
        result = await calendars.insert_many(events_to_insert)
        print(f"✅ Added {len(events_to_insert)} new events")
        return len(events_to_insert)
    else:
        print("📅 No new events to add")
        return 0