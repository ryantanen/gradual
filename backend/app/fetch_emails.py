import requests
import base64
import json
import time
from dotenv import load_dotenv
import os
load_dotenv()
access_token = os.getenv("TEST_GOOGLE_ACCESS_TOKEN")

def get_recent_emails(access_token, number):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    emails = []
    base_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
    max_per_page = 100  # Gmail allows up to 500    
    params = {
        "maxResults": min(number, max_per_page)  # Adjust batch size as needed
    }

    while len(emails) < number:
        response = requests.get(base_url, headers=headers, params=params).json()

        # Handle error cases
        if "messages" not in response:
            print("Error fetching messages:", response)
            break

        for message in response['messages']:
            if (len(emails) >= number):
                break
            msg_id = message['id']
            message_data = requests.get(
                f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}",
                headers=headers
            ).json()

            payload = message_data.get('payload', {})
            encoded_bytes = None

            # Try both formats: multipart or plain
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

            # Extract headers
            headers_list = payload.get('headers', [])
            headers_dict = {h['name'].lower(): h['value'] for h in headers_list}

            email_data = {
                "id": message_data['id'],
                "response_text": decoded_bytes,
                "date": headers_dict.get('date', "No date"),
                "from_address": headers_dict.get('from', "No sender"),
                "subject": headers_dict.get('subject', "No subject"),
                "STARRED": 1 if 'STARRED' in message_data.get('labelIds', []) else 0
            }
            emails.append(email_data)

        print(f"✅ Fetched batch: {len(response['messages'])} — Total collected: {len(emails)}")

        # Pagination
        if "nextPageToken" in response:
            params["pageToken"] = response["nextPageToken"]
            params["maxResults"] = min(number - len(emails), max_per_page)
            time.sleep(0.3)  # Avoid hitting rate limits
        else:
            break

    return emails

def append_new_emails_cron_job(access_token, number=100, path='app/emails.json'):
    existing = []
    
    with open(path, 'r', encoding='utf-8') as f:
        existing = json.load(f)

    existing_ids = {e["id"] for e in existing}
    new_emails = get_recent_emails(access_token, number)
    unique_emails = [e for e in new_emails if e["id"] not in existing_ids]

    if unique_emails:
        combined = existing + unique_emails
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(combined, f, indent=2, ensure_ascii=False)
        print(f"✅ Added {len(unique_emails)} new emails. Total now: {len(combined)}")
    else:
        print("📭 No new emails to add.")

# emails = get_recent_emails(access_token, 100)
# with open('app/emails.json', 'w', encoding='utf-8') as f:
#          json.dump(emails, f, indent=2, ensure_ascii=False)
# print(f"📁 Saved {len(emails)} emails to app/emails.json")

append_new_emails_cron_job(access_token, number=100, path='app/emails.json')