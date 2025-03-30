import requests
import json

access_token = "ya29.a0AeXRPp6A92iN-g5ntVfuB5n0p7zqOa9PReUMikRtnLNtxu6DU5RImzNxYvFkhit0WDiP82At59uvITG9pHjvMMLSskfCpaaNIzKA6E-nhggXDxdbo8VctMg8eF5NyvJ6PkTngnM0JmFRR4yXDdcQG050SRBzafWV5iecrhNsaCgYKAaISARASFQHGX2MivwOmc2qGcas6kYpJx4EWHg0175"
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

    #print(response)

    if 'items' not in response:
        print("No calendars fetched")
        return;

    events = []
    for calendar in response['items']:
        #print (calendar['id'])
        #print (f"https://www.googleapis.com/calendar/v3/calendars/{calendar['id']}/events?timeMin={startTS}&timeMax={endTS}")
        calendar_data = requests.get(
            f"https://www.googleapis.com/calendar/v3/calendars/{calendar['id']}/events?timeMin={startTS}&timeMax={endTS}",
            headers=headers
        ).json()

        if 'items' not in calendar_data:
            continue

        for event in calendar_data['items']:
            id = event.get('id', None)
            start = event['start'].get('dateTime', None)
            end = event['end'].get('dateTime', None)
            location = event.get('location', None)
            event_name = event.get('summary', None)
            event_desc = event.get('description', None)
            collaborators = [attendee.get('email', None) for attendee in event.get('attendees', [])]

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