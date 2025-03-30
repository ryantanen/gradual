import requests
import base64
import json

access_token = "ya29.a0AeXRPp7Ke1Hra75qM6UFDQHwLu6TNvn5TJ32qSpIoSR1LgTwHr6STwsAJDskkeH-bo0P30NSTdEm3o5THmSzqeBb6LOg_5Srny_yHGrAQ-X5Wz-gwVmgW1mdYiNaJ9P-WnbgjEo5Kw79FsWYuH7RJMA_7_oHeku5F2D9VZztaCgYKAcISARMSFQHGX2Mipml5m5pWl6Sdg4J1NJ42tA0175"
def get_emails():
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(
        "https://gmail.googleapis.com/gmail/v1/users/me/messages",
        headers=headers
    )

    emails = []

    response_data = response.json()

    for message in response_data['messages']:
        message_data = requests.get(
            f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message['id']}",
            headers=headers
        ).json()
        
        # Handle both payload structures
        payload = message_data['payload']
        encoded_bytes = None
        
        if 'parts' in payload:
            # Case 1: Direct parts structure
            if 'body' in payload['parts'][0] and 'data' in payload['parts'][0]['body']:
                encoded_bytes = payload['parts'][0]['body']['data']
        # Case 2: Direct body structure
        elif 'body' in payload and 'data' in payload['body']:
            encoded_bytes = payload['body']['data']
        
        if not encoded_bytes:
            continue  # Skip messages without content
        
        # Find the header indices
        date_header_index = next(
            (i for i, header in enumerate(payload['headers']) 
            if header['name'].lower() == 'date'),
            None
        )
        from_header_index = next(
            (i for i, header in enumerate(payload['headers']) 
            if header['name'].lower() == 'from'),
            None
        )
        subject_header_index = next(
            (i for i, header in enumerate(payload['headers']) 
            if header['name'].lower() == 'subject'),
            None
        )
        
        # Extract header values
        date = payload['headers'][date_header_index]['value'] if date_header_index is not None else "No date found"
        from_address = payload['headers'][from_header_index]['value'] if from_header_index is not None else "No sender found"
        subject = payload['headers'][subject_header_index]['value'] if subject_header_index is not None else "No subject found"
        id = message_data['id']
        decoded_bytes = base64.urlsafe_b64decode(encoded_bytes).decode('utf-8')

        # Check if message is starred
        is_starred = 1 if 'STARRED' in message_data.get('labelIds', []) else 0

        # Create a JSON object for this email
        email_data = {
            "id": id,
            "response_text": decoded_bytes,
            "date": date,
            "from_address": from_address,
            "subject": subject,
            "STARRED": is_starred
        }
        emails.append(email_data)

    # Save emails to a JSON file
    with open('app/emails.json', 'w', encoding='utf-8') as f:
        json.dump(emails, f, indent=2, ensure_ascii=False)
    