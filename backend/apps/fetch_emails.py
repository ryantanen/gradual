import requests
import base64
import json
import time
import hashlib
from datetime import datetime
from typing import List, Dict, Any
from .db import emails, Email

def generate_email_hash(content: str, sender: str, subject: str, datetime: datetime) -> str:
    """Generate a unique hash for an email based on its content and metadata"""
    # Combine content and metadata
    hash_input = f"{content}{sender}{subject}{datetime.isoformat()}"
    # Generate SHA-256 hash
    return hashlib.sha256(hash_input.encode('utf-8')).hexdigest()

async def get_recent_emails(access_token: str, user_id: str, number: int = 100) -> List[Dict[str, Any]]:
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    fetched_emails = []
    base_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
    max_per_page = 100  # Gmail allows up to 500    
    params = {
        "maxResults": min(number, max_per_page)
    }

    while len(fetched_emails) < number:
        response = requests.get(base_url, headers=headers, params=params).json()

        if "messages" not in response:
            print("Error fetching messages:", response)
            break

        for message in response['messages']:
            if len(fetched_emails) >= number:
                break
                
            msg_id = message['id']
            message_data = requests.get(
                f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}",
                headers=headers
            ).json()

            payload = message_data.get('payload', {})
            encoded_bytes = None

            if 'parts' in payload:
                for part in payload['parts']:
                    if part.get('mimeType') == 'text/plain' and 'data' in part.get('body', {}):
                        encoded_bytes = part['body']['data']
                        break
            elif 'body' in payload and 'data' in payload['body']:
                encoded_bytes = payload['body']['data']

            if not encoded_bytes:
                continue

            try:
                decoded_bytes = base64.urlsafe_b64decode(encoded_bytes).decode('utf-8')
            except Exception as e:
                print(f"⚠️ Could not decode message {msg_id}: {e}")
                continue

            headers_list = payload.get('headers', [])
            headers_dict = {h['name'].lower(): h['value'] for h in headers_list}

            # Parse the date string
            date_str = headers_dict.get('date', "")
            try:
                # Try to parse the date string
                email_date = datetime.strptime(date_str.split(" +")[0], "%a, %d %b %Y %H:%M:%S")
            except:
                email_date = datetime.utcnow()

            sender = headers_dict.get('from', "No sender")
            subject = headers_dict.get('subject', "No subject")
            
            # Generate content hash
            content_hash = generate_email_hash(decoded_bytes, sender, subject, email_date)

            email_data = Email(
                sender=sender,
                subject=subject,
                datetime=email_date,
                content=decoded_bytes,
                is_starred=1 if 'STARRED' in message_data.get('labelIds', []) else 0,
                user_id=user_id,
                content_hash=content_hash
            )
            
            fetched_emails.append(email_data.model_dump())

        print(f"✅ Fetched batch: {len(response['messages'])} — Total collected: {len(fetched_emails)}")

        if "nextPageToken" in response:
            params["pageToken"] = response["nextPageToken"]
            params["maxResults"] = min(number - len(fetched_emails), max_per_page)
            time.sleep(0.3)  # Avoid hitting rate limits
        else:
            break

    return fetched_emails

async def sync_emails(access_token: str, user_id: str, number: int = 100):
    """Sync emails from Gmail to MongoDB"""
    # Get existing email hashes for this user
    existing_emails = await emails.find({"user_id": user_id}).to_list(None)
    existing_hashes = {email.get("content_hash") for email in existing_emails}
    
    # Fetch new emails
    new_emails = await get_recent_emails(access_token, user_id, number)
    
    # Filter out emails we already have based on content hash
    emails_to_insert = [
        email for email in new_emails 
        if email.get("content_hash") not in existing_hashes
    ]
    
    if emails_to_insert:
        result = await emails.insert_many(emails_to_insert)
        print(f"✅ Added {len(emails_to_insert)} new emails")
        return len(emails_to_insert)
    else:
        print("📭 No new emails to add")
        return 0 