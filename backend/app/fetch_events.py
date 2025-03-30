import requests
import json
import urllib


from dotenv import load_dotenv
import os
load_dotenv()
access_token = os.getenv("TEST_GOOGLE_ACCESS_TOKEN")

def get_events_between(startTS, endTS): 
    # gets events from all calendars between startTs and endTS
    # startTS and endTS has to be RFC 3339 format        
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(
        "https://www.googleapis.com/calendar/v3/users/me/calendarList",
        headers=headers
    ).json()

    print(response)

    if 'items' not in response:
        print("No calendars fetched")
        return;

    events = []
    for calendar in response['items']:
        #print (calendar['id'])
        #print (f"https://www.googleapis.com/calendar/v3/calendars/{calendar['id']}/events?timeMin={startTS}&timeMax={endTS}")
        encoded_id = urllib.parse.quote(calendar['id'], safe='')
        calendar_data = requests.get(
            f"https://www.googleapis.com/calendar/v3/calendars/{encoded_id}/events?timeMin={startTS}&timeMax={endTS}",
            headers=headers
        ).json()

        if 'items' not in calendar_data:
            continue

        for event in calendar_data['items']:
            id = event.get('id', "No ID")
            start = event.get('start', {}).get('dateTime') or event.get('start', {}).get('date') or "No start time"
            end = event.get('end', {}).get('dateTime') or event.get('end', {}).get('date') or "No end time"
            location = event.get('location', "No location")
            event_name = event.get('summary', "No event name")
            event_desc = event.get('description', "No description")
            collaborators = [attendee.get('email', "No email") for attendee in event.get('attendees', [])] if 'attendees' in event else []


            event_data = {
                "id": id,
                "start": start,
                "end": end,
                "location": location,
                "event_name": event_name,
                "event_desc": event_desc,
                "collaborators": collaborators
            }
            events.append(event_data)
    # Save emails to a JSON file
    with open('app/events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)


startTime = "2025-01-29T20:05:11-04:00"
endTime = "2025-03-29T20:05:11-04:00"
get_events_between(startTime, endTime)